"""
Analysis pipeline for running full analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from pathlib import Path
import json
from typing import Dict, Any
PROJECT_ROOT = Path().resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.datas.loader import BrentDataLoader
from src.datas.cleaner import BrentDataCleaner
from src.datas.events import EventManager
from src.analysis.eda import BrentEDA
from src.analysis.time_series import TimeSeriesAnalyzer
from src.analysis.bayesian import BayesianChangePointAnalyzer
from src.analysis.change_point import ChangePointAnalyzer
from src.visualization.plots import StaticPlotter

class AnalysisPipeline:
    """
    Pipeline for running complete Brent oil analysis
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize analysis pipeline
        
        Args:
            data_path: Path to raw data file
        """
        self.data_path = data_path
        self.results = {}
        
    def run_full_analysis(self, analysis_period: tuple = ('2007-01-01', '2010-12-31')) -> Dict[str, Any]:
        """
        Run complete analysis pipeline
        
        Args:
            analysis_period: Tuple of (start_date, end_date)
            
        Returns:
            Dictionary with all analysis results
        """
        print("="*80)
        print("RUNNING COMPLETE BRENT OIL ANALYSIS PIPELINE")
        print("="*80)
        
        # Step 1: Load and clean data
        print("\n📥 STEP 1: DATA LOADING AND CLEANING")
        print("-" * 40)
        
        loader = BrentDataLoader(self.data_path)
        raw_df = loader.load_raw_data()
        
        cleaner = BrentDataCleaner()
        cleaned_df = cleaner.clean_data(raw_df)
        
        # Save cleaned data
        os.makedirs('data/processed', exist_ok=True)
        cleaner.save_cleaned_data(cleaned_df, 'data/processed/cleaned_prices.csv')
        
        # Step 2: Compile events
        print("\n📚 STEP 2: EVENT COMPILATION")
        print("-" * 40)
        
        event_manager = EventManager()
        events_df = event_manager.compile_events()
        events_df = event_manager.enrich_with_price_data(cleaned_df)
        event_manager.save_events('data/processed/events.csv')
        
        # Step 3: EDA
        print("\n🔍 STEP 3: EXPLORATORY DATA ANALYSIS")
        print("-" * 40)
        
        eda = BrentEDA(cleaned_df)
        eda_results = eda.run_comprehensive_eda(
            save_path='reports/figures/eda_report.png'
        )
        eda.print_summary_report()
        
        # Step 4: Time series analysis
        print("\n📈 STEP 4: TIME SERIES ANALYSIS")
        print("-" * 40)
        
        ts_analyzer = TimeSeriesAnalyzer(cleaned_df['Price'])
        ts_results = ts_analyzer.test_stationarity()
        decomposition = ts_analyzer.decompose(period=365)
        autocorrelation = ts_analyzer.calculate_autocorrelation(max_lag=50)
        
        # Step 5: Focus on analysis period
        print(f"\n🎯 STEP 5: FOCUSING ON ANALYSIS PERIOD {analysis_period}")
        print("-" * 40)
        
        mask = (cleaned_df['Date'] >= analysis_period[0]) & (cleaned_df['Date'] <= analysis_period[1])
        df_period = cleaned_df[mask].copy()
        
        prices = df_period['Price'].values
        dates = df_period['Date'].values
        
        print(f"Selected {len(df_period):,} data points for detailed analysis")
        
        # Step 6: Bayesian change point analysis
        print("\n🔮 STEP 6: BAYESIAN CHANGE POINT ANALYSIS")
        print("-" * 40)
        
        bayesian_analyzer = BayesianChangePointAnalyzer(prices, dates)
        bayesian_results = bayesian_analyzer.run_full_analysis(n_change_points=1)
        
        # Step 7: Traditional change point detection
        print("\n📍 STEP 7: TRADITIONAL CHANGE POINT DETECTION")
        print("-" * 40)
        
        traditional_analyzer = ChangePointAnalyzer()
        series = pd.Series(prices, index=dates)
        traditional_results = traditional_analyzer.compare_methods(series)
        
        # Step 8: Visualization
        print("\n📊 STEP 8: VISUALIZATION")
        print("-" * 40)
        
        plotter = StaticPlotter()
        
        # Plot price series
        plotter.plot_price_series(
            df_period, 
            title=f'Brent Oil Prices ({analysis_period[0]} to {analysis_period[1]})',
            save_path='reports/figures/price_series_focus.png'
        )
        
        # Plot with events
        events_in_period = events_df[
            (events_df['Date'] >= analysis_period[0]) & 
            (events_df['Date'] <= analysis_period[1])
        ]
        
        plotter.plot_price_with_events(
            df_period, 
            events_in_period,
            save_path='reports/figures/price_with_events_focus.png'
        )
        
        # Step 9: Compile results
        print("\n💾 STEP 9: COMPILING RESULTS")
        print("-" * 40)
        
        self.results = {
            'metadata': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_period': analysis_period,
                'data_points': len(df_period),
                'date_range': {
                    'start': df_period['Date'].min().strftime('%Y-%m-%d'),
                    'end': df_period['Date'].max().strftime('%Y-%m-%d')
                }
            },
            'eda': eda_results,
            'time_series': {
                'stationarity': ts_results,
                'decomposition': {k: len(v) for k, v in decomposition.items()},
                'autocorrelation': autocorrelation
            },
            'bayesian': bayesian_results,
            'traditional_change_points': traditional_results,
            'events': {
                'total': len(events_in_period),
                'by_type': events_in_period['Type'].value_counts().to_dict()
            }
        }
        
        # Save results
        os.makedirs('data/results', exist_ok=True)
        with open('data/results/analysis_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save Bayesian posterior samples (limited)
        if hasattr(bayesian_analyzer, 'trace'):
            posterior_samples = {
                'tau': bayesian_analyzer.trace.posterior['tau'].values.flatten()[:1000].tolist(),
                'mu_before': bayesian_analyzer.trace.posterior['mu_before'].values.flatten()[:1000].tolist(),
                'mu_after': bayesian_analyzer.trace.posterior['mu_after'].values.flatten()[:1000].tolist()
            }
            
            with open('data/results/posterior_samples.json', 'w') as f:
                json.dump(posterior_samples, f, indent=2)
        
        print(f"\n✅ Analysis complete! Results saved to data/results/")
        
        return self.results
    
    def generate_report(self) -> str:
        """
        Generate summary report of analysis
        
        Returns:
            Report string
        """
        if not self.results:
            return "No analysis results available. Run analysis first."
        
        meta = self.results['metadata']
        bayesian = self.results.get('bayesian', {})
        
        report = f"""
        BRENT OIL ANALYSIS REPORT
        =========================
        
        Analysis Date: {meta['analysis_date']}
        Period Analyzed: {meta['analysis_period'][0]} to {meta['analysis_period'][1]}
        Data Points: {meta['data_points']:,}
        
        KEY FINDINGS
        ------------
        
        1. Data Characteristics:
           - Date range: {meta['date_range']['start']} to {meta['date_range']['end']}
           - Events analyzed: {self.results.get('events', {}).get('total', 0)}
        
        2. Change Point Analysis:
        """
        
        if 'change_points' in bayesian:
            for cp_name, cp_stats in bayesian['change_points'].items():
                report += f"""
           - {cp_name}: 
             * Most likely date: {cp_stats.get('date_mean', 'N/A')}
             * 95% Credible Interval: {cp_stats.get('date_95ci', ['N/A', 'N/A'])}
        """
        
        if 'impact' in bayesian and 'single_change' in bayesian['impact']:
            impact = bayesian['impact']['single_change']
            report += f"""
             * Mean before change: ${impact['mu_before']['mean']:.2f}
             * Mean after change: ${impact['mu_after']['mean']:.2f}
             * Change: ${impact['difference']['mean']:.2f} ({impact['difference']['percent_change']:.1f}%)
             * Probability of increase: {impact['probability_increase']*100:.1f}%
        """
        
        report += f"""
        
        3. Model Diagnostics:
           - Convergence: {'✅ Good' if bayesian.get('convergence', {}).get('converged', False) else '⚠️ Issues'}
           - R-hat values: {bayesian.get('convergence', {}).get('rhat', {}).get('all_close_to_1', False)}
        
        RECOMMENDATIONS
        ---------------
        1. Monitor periods following detected change points for market shifts
        2. Use Bayesian credible intervals for risk assessment
        3. Consider additional external factors for improved forecasting
        4. Implement regular model updates as new data becomes available
        """
        
        return report

# Main execution
if __name__ == "__main__":
    pipeline = AnalysisPipeline()
    results = pipeline.run_full_analysis()
    report = pipeline.generate_report()
    print(report)