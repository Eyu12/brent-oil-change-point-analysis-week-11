"""
Bayesian modeling for Brent oil change point detection
"""

import pymc as pm
import arviz as az
import numpy as np
import pandas as pd
from typing import Dict, Any
import warnings
warnings.filterwarnings("ignore")


class BayesianChangePointAnalyzer:
    """
    Bayesian change point analysis for Brent oil prices
    """

    def __init__(self, prices: np.ndarray = None, dates: pd.DatetimeIndex = None):
        self.prices = prices
        self.dates = dates
        self.model = None
        self.trace = None
        self.results = {}

    def set_data(self, prices: np.ndarray, dates: pd.DatetimeIndex = None) -> None:
        self.prices = prices
        self.dates = dates

    # ------------------------------------------------------------------
    # MODEL DEFINITIONS
    # ------------------------------------------------------------------
    def build_single_change_point_model(self) -> pm.Model:
        if self.prices is None:
            raise ValueError("No price data provided")

        n = len(self.prices)

        with pm.Model() as model:
            tau = pm.DiscreteUniform("tau", lower=0, upper=n)

            mu_before = pm.Normal("mu_before", mu=self.prices.mean(), sigma=self.prices.std())
            mu_after = pm.Normal("mu_after", mu=self.prices.mean(), sigma=self.prices.std())

            sigma = pm.HalfNormal("sigma", sigma=self.prices.std())

            mu = pm.math.switch(tau > np.arange(n), mu_before, mu_after)

            pm.Normal("likelihood", mu=mu, sigma=sigma, observed=self.prices)

            self.model = model

        return model

    def build_multiple_change_point_model(self, n_change_points: int = 2) -> pm.Model:
        if self.prices is None:
            raise ValueError("No price data provided")

        n = len(self.prices)

        with pm.Model() as model:
            taus = []
            for i in range(n_change_points):
                lower = 0 if i == 0 else taus[i - 1] + 1
                tau = pm.DiscreteUniform(f"tau_{i}", lower=lower, upper=n)
                taus.append(tau)

            means = [
                pm.Normal(f"mu_{i}", mu=self.prices.mean(), sigma=self.prices.std())
                for i in range(n_change_points + 1)
            ]

            sigma = pm.HalfNormal("sigma", sigma=self.prices.std())

            mu_array = means[0] * np.ones(n)
            for i, tau in enumerate(taus):
                mu_array = pm.math.switch(np.arange(n) > tau, means[i + 1], mu_array)

            pm.Normal("likelihood", mu=mu_array, sigma=sigma, observed=self.prices)

            self.model = model

        return model

    # ------------------------------------------------------------------
    # SAMPLING
    # ------------------------------------------------------------------
    def sample(
        self,
        model: pm.Model = None,
        draws: int = 2000,
        tune: int = 1000,
        chains: int = 2,
        cores: int = 2,
        random_seed: int = 42,
    ) -> az.InferenceData:

        if model is None:
            model = self.model or self.build_single_change_point_model()

        print(f"Running MCMC: chains={chains}, draws={draws}, tune={tune}")

        with model:
            trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                cores=cores,
                random_seed=random_seed,
                return_inferencedata=True,
                progressbar=True,
            )

        self.trace = trace
        return trace

    # ------------------------------------------------------------------
    # CONVERGENCE DIAGNOSTICS 
    # ------------------------------------------------------------------
    def check_convergence(self, trace: az.InferenceData = None) -> Dict[str, Any]:
        if trace is None:
            trace = self.trace
        if trace is None:
            raise ValueError("No trace available")

        diagnostics = {}

        summary = az.summary(trace)
        diagnostics["summary"] = summary

        # ---- R-hat ----
        rhat = summary["r_hat"]
        diagnostics["rhat"] = {
            "values": rhat.to_dict(),
            "min": float(rhat.min()),
            "max": float(rhat.max()),
            "mean": float(rhat.mean()),
            "all_close_to_1": bool(np.all((rhat > 0.99) & (rhat < 1.01))),
        }

        # ---- ESS (FIXED VERSION) ----
        ess = az.ess(trace)

        ess_values = {}
        all_ess_numbers = []

        for var in ess.data_vars:
            values = ess[var].values.flatten()
            values = values[~np.isnan(values)]

            if len(values) > 0:
                ess_values[var] = float(values.mean())
                all_ess_numbers.extend(values.tolist())

        diagnostics["effective_sample_size"] = {
            "values": ess_values,
            "min": float(np.min(all_ess_numbers)),
            "mean": float(np.mean(all_ess_numbers)),
            "acceptable": bool(np.all(np.array(all_ess_numbers) > 400)),
        }

        # ---- MCSE ----
        mcse = az.mcse(trace)
        mcse_values = {
            var: float(mcse[var].values.mean())
            for var in mcse.data_vars
        }

        diagnostics["mcse"] = {
            "values": mcse_values,
            "max": float(max(mcse_values.values())),
        }

        # ---- Divergences ----
        try:
            n_div = int(trace.sample_stats["diverging"].sum())
            total = trace.posterior.sizes["chain"] * trace.posterior.sizes["draw"]
            diagnostics["divergent_transitions"] = {
                "count": n_div,
                "percentage": 100 * n_div / total,
                "acceptable": n_div == 0,
            }
        except Exception:
            diagnostics["divergent_transitions"] = {
                "count": 0,
                "percentage": 0.0,
                "acceptable": True,
            }

        diagnostics["converged"] = (
            diagnostics["rhat"]["all_close_to_1"]
            and diagnostics["effective_sample_size"]["acceptable"]
            and diagnostics["divergent_transitions"]["acceptable"]
        )

        self.results["convergence"] = diagnostics
        return diagnostics

    # ------------------------------------------------------------------
    # CHANGE POINT IDENTIFICATION
    # ------------------------------------------------------------------
    def identify_change_points(self, trace: az.InferenceData = None) -> Dict[str, Any]:
        if trace is None:
            trace = self.trace
        if trace is None:
            raise ValueError("No trace available")

        change_points = {}

        tau_params = [v for v in trace.posterior.data_vars if v.startswith("tau")]

        for param in tau_params:
            samples = trace.posterior[param].values.flatten()

            stats = {
                "mean": float(np.mean(samples)),
                "median": float(np.median(samples)),
                "std": float(np.std(samples)),
                "95ci": [
                    float(np.percentile(samples, 2.5)),
                    float(np.percentile(samples, 97.5)),
                ],
            }

            if self.dates is not None:
                stats["date_mean"] = self.dates[int(stats["mean"])].strftime("%Y-%m-%d")

            change_points[param] = stats

        self.results["change_points"] = change_points
        return change_points

    # ------------------------------------------------------------------
    # IMPACT QUANTIFICATION
    # ------------------------------------------------------------------
    def quantify_impact(self, trace: az.InferenceData = None) -> Dict[str, Any]:
        if trace is None:
            trace = self.trace
        if trace is None:
            raise ValueError("No trace available")

        impact = {}

        mu_params = sorted([v for v in trace.posterior.data_vars if v.startswith("mu_")])

        if len(mu_params) >= 2:
            mu0 = trace.posterior[mu_params[0]].values.flatten()
            mu1 = trace.posterior[mu_params[1]].values.flatten()
            diff = mu1 - mu0

            impact["single_change"] = {
                "mu_before": float(mu0.mean()),
                "mu_after": float(mu1.mean()),
                "difference": float(diff.mean()),
                "percent_change": float(diff.mean() / mu0.mean() * 100),
                "probability_increase": float(np.mean(diff > 0)),
            }

        self.results["impact"] = impact
        return impact

    # ------------------------------------------------------------------
    # FULL PIPELINE
    # ------------------------------------------------------------------
    def run_full_analysis(self, n_change_points: int = 1) -> Dict[str, Any]:
        print("=" * 60)
        print("BAYESIAN CHANGE POINT ANALYSIS")
        print("=" * 60)

        if n_change_points == 1:
            model = self.build_single_change_point_model()
        else:
            model = self.build_multiple_change_point_model(n_change_points)

        trace = self.sample(model)
        convergence = self.check_convergence(trace)
        change_points = self.identify_change_points(trace)
        impact = self.quantify_impact(trace)

        return {
            "model_type": f"{n_change_points}_change_point",
            "convergence": convergence,
            "change_points": change_points,
            "impact": impact,
        }


# ------------------------------------------------------------------
# EXAMPLE USAGE
# ------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    n = 200

    dates = pd.date_range("2020-01-01", periods=n, freq="D")
    prices = np.concatenate([
        np.random.normal(50, 5, 100),
        np.random.normal(70, 8, 100),
    ])

    analyzer = BayesianChangePointAnalyzer(prices, dates)
    results = analyzer.run_full_analysis(n_change_points=1)

    print("\nChange points:", results["change_points"])
    print("Impact:", results["impact"])
    print("Converged:", results["convergence"]["converged"])
