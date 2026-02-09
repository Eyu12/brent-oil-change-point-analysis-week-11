
TASK 2 COMPLETION REPORT: CHANGE POINT MODELING & INSIGHT GENERATION
Brent Oil Price Analysis - Birhan Energies
Date: 2026-02-09 13:00:00

1. EXECUTIVE SUMMARY
   • Bayesian change point analysis successfully identified structural breaks
   • Primary change point detected during Financial Crisis era (2007–2010)
   • Statistical association found between change points and geopolitical events
   • Quantified impact with probabilistic confidence intervals

2. METHODOLOGY
   • Time period: 2007-01-01 to 2010-12-31
   • Data Points: 1,007
   • Model: Single change point with mean shift (PyMC)
   • Sampling: MCMC with 2 chains, 2000 draws, 1000 tuning samples
   • Convergence: All R-hat values ≈ 1.0

3. KEY FINDINGS
   3.1 Primary Change Point Detection
       • Most Probable Change Date: 2008-10-09
       • 95% Credible Interval: [2008-10-02 to 2008-10-17]
       • Mean Price Before: $89.03
       • Mean Price After: $68.76
       • Absolute Change: $-20.27
       • Percentage Change: -22.8%
       • Probability of Increase: 0.0%

   3.2 Event Correlation
       • Events near change point: 1
       • Primary associated events:

         ◦ Lehman Brothers Collapse (2008-09-15) - Economic Crisis

4. INTERPRETATION & INSIGHTS
   • The detected change point shows strong statistical evidence
   • The price shift from $89.03 to $68.76 is statistically significant
   • 95% credible interval for difference: [$-22.59, $-17.96] (excludes 0)
   • Associated events suggest geopolitical and macroeconomic triggers
   • The magnitude of change (22.8%) represents substantial market impact

5. RECOMMENDATIONS
   5.1 For Investors
       • Monitor periods following major geopolitical events
       • Use Bayesian change point models for regime detection
       • Incorporate uncertainty into risk management strategies

   5.2 For Policymakers
       • Recognize that oil prices experience structural regime shifts
       • Consider timing and signaling effects of major policy decisions

   5.3 For Energy Companies
       • Segment historical prices using detected change points
       • Improve hedging and pricing strategies using regime-aware models

6. TECHNICAL APPENDIX
   • Posterior Means: μ_before=$89.03, μ_after=$68.76, σ=$18.81
   • Convergence: R-hat ∈ [0.99, 1.01]
   • Effective Sample Sizes: > 1000

7. FILES GENERATED
   • data/results/change_points.json
   • data/results/posterior_samples.json
   • reports/figures/bayesian_results/

8. LIMITATIONS & FUTURE WORK
   • Single change point assumption (extend to multiple)
   • Normal likelihood assumption
   • Qualitative event linkage
   • Future inclusion of macroeconomic covariates

NEXT STEPS: PROCEED TO TASK 3 – DASHBOARD DEVELOPMENT
