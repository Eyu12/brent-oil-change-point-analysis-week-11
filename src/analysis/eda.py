"""
Exploratory Data Analysis for Brent oil prices
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')

class BrentEDA:
    """
    Perform comprehensive EDA on Brent oil prices
    """
    
    def __init__(self, df: pd.DataFrame = None):
        """
        Initialize EDA analyzer
        
        Args:
            df: DataFrame with price data
        """
        self.df = df
        self.results = {}
        
    def set_data(self, df: pd.DataFrame) -> None:
        """Set data for analysis"""
        self.df = df
    
    def run_comprehensive_eda(self, save_path: str = None) -> dict[str, any]:
        """
        Run comprehensive EDA analysis
        """
        print("🔍 Running Comprehensive EDA...")
        
        if self.df is None:
            raise ValueError("No data provided. Set data first.")
        
        results = {}
        results['basic_stats'] = self._calculate_basic_statistics()
        results['time_series'] = self._analyze_time_series_properties()
        results['distributions'] = self._analyze_distributions()
        results['seasonality'] = self._analyze_seasonality()
        results['volatility'] = self._analyze_volatility()
        results['outliers'] = self._detect_outliers()
        
        if save_path:
            self._create_visualizations(save_path)
        
        self.results = results
        return results
    
    def _calculate_basic_statistics(self) -> dict[str, any]:
        print("   Calculating basic statistics...")
        
        stats_dict = {
            'count': len(self.df),
            'date_range': {
                'start': self.df['Date'].min(),
                'end': self.df['Date'].max(),
                'days': (self.df['Date'].max() - self.df['Date'].min()).days
            },
            'price_stats': {
                'mean': self.df['Price'].mean(),
                'median': self.df['Price'].median(),
                'std': self.df['Price'].std(),
                'min': self.df['Price'].min(),
                'max': self.df['Price'].max(),
                'q25': self.df['Price'].quantile(0.25),
                'q75': self.df['Price'].quantile(0.75),
                'iqr': self.df['Price'].quantile(0.75) - self.df['Price'].quantile(0.25)
            },
            'return_stats': {}
        }
        
        if 'Log_Return' in self.df.columns:
            returns = self.df['Log_Return'].dropna()
            stats_dict['return_stats'] = {
                'mean': returns.mean(),
                'std': returns.std(),
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'shapiro_p': stats.shapiro(returns)[1] if len(returns) < 5000 else None,
                'jarque_bera': stats.jarque_bera(returns)
            }
        
        return stats_dict
    
    def _analyze_time_series_properties(self) -> dict[str, any]:
        print("   Analyzing time series properties...")
        
        ts_dict = {}
        
        if 'Price' in self.df.columns:
            adf_price = adfuller(self.df['Price'].dropna())
            ts_dict['stationarity_price'] = {
                'adf_statistic': adf_price[0],
                'p_value': adf_price[1],
                'is_stationary': adf_price[1] < 0.05,
                'critical_values': adf_price[4]
            }
        
        if 'Log_Return' in self.df.columns:
            returns = self.df['Log_Return'].dropna()
            adf_returns = adfuller(returns)
            ts_dict['stationarity_returns'] = {
                'adf_statistic': adf_returns[0],
                'p_value': adf_returns[1],
                'is_stationary': adf_returns[1] < 0.05,
                'critical_values': adf_returns[4]
            }
            
            autocorr = [returns.autocorr(lag=i) for i in range(1, 21)]
            ts_dict['autocorrelation'] = {
                'lags': list(range(1, 21)),
                'values': autocorr,
                'significant_lags': [
                    i for i, val in enumerate(autocorr, 1)
                    if abs(val) > 2 / np.sqrt(len(returns))
                ]
            }
        
        return ts_dict
    
    def _analyze_distributions(self) -> dict[str, any]:
        print("   Analyzing distributions...")
        
        dist_dict = {
            'price': {
                'skewness': self.df['Price'].skew(),
                'kurtosis': self.df['Price'].kurtosis(),
                'normality_test': stats.normaltest(self.df['Price'].dropna())
            }
        }
        
        if 'Log_Return' in self.df.columns:
            returns = self.df['Log_Return'].dropna()
            dist_dict['returns'] = {
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'normality_test': stats.normaltest(returns),
                'is_normal': stats.normaltest(returns)[1] > 0.05
            }
        
        return dist_dict
    
    def _analyze_seasonality(self) -> dict[str, any]:
        print("   Analyzing seasonality...")
        
        season_dict = {}
        
        if 'Month' in self.df.columns:
            monthly_stats = self.df.groupby('Month')['Price'].agg(['mean', 'std', 'count'])
            season_dict['monthly'] = {
                'means': monthly_stats['mean'].to_dict(),
                'best_month': monthly_stats['mean'].idxmax(),
                'worst_month': monthly_stats['mean'].idxmin()
            }
        
        if 'DayOfWeek' in self.df.columns:
            dow_stats = self.df.groupby('DayOfWeek')['Price'].agg(['mean', 'std'])
            season_dict['day_of_week'] = {
                'means': dow_stats['mean'].to_dict(),
                'best_day': dow_stats['mean'].idxmax(),
                'worst_day': dow_stats['mean'].idxmin()
            }
        
        return season_dict
    
    def _analyze_volatility(self) -> dict[str, any]:
        print("   Analyzing volatility...")
        
        vol_dict = {}
        
        if 'Log_Return' in self.df.columns:
            returns = self.df['Log_Return'].dropna()
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
            
            vol_dict = {
                'annualized_volatility': returns.std() * np.sqrt(252),
                'rolling_volatility': {
                    'mean': rolling_vol.mean(),
                    'max': rolling_vol.max(),
                    'min': rolling_vol.min(),
                    'std': rolling_vol.std()
                },
                'volatility_clusters': len(rolling_vol[rolling_vol > rolling_vol.quantile(0.9)]),
                'high_vol_periods': rolling_vol[rolling_vol > rolling_vol.quantile(0.9)].index.tolist()
            }
        
        return vol_dict
    
    def _detect_outliers(self) -> dict[str, any]:
        print("   Detecting outliers...")
        
        Q1 = self.df['Price'].quantile(0.25)
        Q3 = self.df['Price'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = self.df[
            (self.df['Price'] < lower_bound) |
            (self.df['Price'] > upper_bound)
        ]
        
        return {
            'method': 'IQR',
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': len(outliers),
            'outlier_percentage': len(outliers) / len(self.df) * 100,
            'outlier_dates': outliers['Date'].tolist()
        }
    
    def _create_visualizations(self, save_path: str) -> None:
        print("   Creating visualizations...")
        
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        fig = plt.figure(figsize=(20, 16))
        
        ax1 = plt.subplot(3, 3, 1)
        ax1.plot(self.df['Date'], self.df['Price'], linewidth=1)
        ax1.set_title('Brent Oil Price Trend')
        
        ax2 = plt.subplot(3, 3, 2)
        ax2.hist(self.df['Price'], bins=50, density=True)
        
        if 'Log_Return' in self.df.columns:
            ax3 = plt.subplot(3, 3, 3)
            returns = self.df['Log_Return'].dropna()
            ax3.hist(returns, bins=100, density=True)
        
        if 'Month' in self.df.columns:
            ax4 = plt.subplot(3, 3, 4)
            self.df.groupby('Month')['Price'].mean().plot(kind='bar', ax=ax4)
        
        # ✅ FIXED ROLLING VOLATILITY PLOT (ONLY CHANGE)
        if 'Log_Return' in self.df.columns:
            ax5 = plt.subplot(3, 3, 5)
            rolling_vol = (
                self.df['Log_Return']
                    .rolling(window=30)
                    .std()
                    * np.sqrt(252)
            ).dropna()
            dates = self.df.loc[rolling_vol.index, 'Date']
            ax5.plot(dates, rolling_vol, linewidth=2)
            ax5.fill_between(dates, 0, rolling_vol, alpha=0.3)
            ax5.set_title('30-Day Rolling Volatility')
        
        plt.tight_layout()
        
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   Visualizations saved to {save_path}")
        
        plt.close(fig)
    
    def print_summary_report(self) -> None:
        if not self.results:
            print("No EDA results available.")
            return
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE EDA SUMMARY REPORT")
        print("=" * 80)
        print("✅ EDA COMPLETE")


# Example usage
if __name__ == "__main__":
    # Load and clean data first
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from src.datas.loader import BrentDataLoader
    from src.datas.cleaner import BrentDataCleaner
    
    # Load and clean data
    loader = BrentDataLoader()
    raw_df = loader.load_raw_data()
    
    cleaner = BrentDataCleaner()
    cleaned_df = cleaner.clean_data(raw_df)
    
    # Run EDA
    eda = BrentEDA(cleaned_df)
    results = eda.run_comprehensive_eda(save_path='eda_report.png')
    eda.print_summary_report()