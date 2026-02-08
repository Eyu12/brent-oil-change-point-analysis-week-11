"""
Time series analysis for Brent oil prices
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesAnalyzer:
    """
    Analyze time series properties of Brent oil prices
    """
    
    def __init__(self, series: pd.Series = None):
        """
        Initialize time series analyzer
        
        Args:
            series: Time series data
        """
        self.series = series
        self.results = {}
    
    def set_series(self, series: pd.Series) -> None:
        """Set time series for analysis"""
        self.series = series
    
    def test_stationarity(self) -> Dict[str, Any]:
        """
        Test stationarity using ADF and KPSS tests
        
        Returns:
            Dictionary with test results
        """
        if self.series is None:
            raise ValueError("No series provided")
        
        results = {}
        
        # ADF Test
        adf_result = adfuller(self.series.dropna())
        results['adf'] = {
            'statistic': adf_result[0],
            'p_value': adf_result[1],
            'critical_values': adf_result[4],
            'is_stationary': adf_result[1] < 0.05
        }
        
        # KPSS Test
        try:
            kpss_result = kpss(self.series.dropna(), regression='c')
            results['kpss'] = {
                'statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'critical_values': kpss_result[3],
                'is_stationary': kpss_result[1] > 0.05
            }
        except:
            results['kpss'] = {
                'error': 'Test failed - series may have zero variance'
            }
        
        # Overall assessment
        adf_stationary = results['adf']['is_stationary']
        kpss_stationary = results['kpss'].get('is_stationary', False)
        
        if adf_stationary and kpss_stationary:
            results['conclusion'] = 'Stationary'
        elif not adf_stationary and not kpss_stationary:
            results['conclusion'] = 'Non-stationary'
        elif adf_stationary and not kpss_stationary:
            results['conclusion'] = 'Trend stationary'
        else:
            results['conclusion'] = 'Difference stationary'
        
        self.results['stationarity'] = results
        return results
    
    def decompose(self, period: int = 365, model: str = 'additive') -> Dict[str, pd.Series]:
        """
        Decompose time series into trend, seasonal, and residual components
        
        Args:
            period: Seasonal period
            model: 'additive' or 'multiplicative'
            
        Returns:
            Dictionary with decomposition components
        """
        if self.series is None:
            raise ValueError("No series provided")
        
        # Handle missing values
        series_clean = self.series.dropna()
        
        if len(series_clean) < period * 2:
            print(f"Warning: Series length ({len(series_clean)}) is less than 2 periods ({period*2})")
            period = min(30, len(series_clean) // 2)
        
        try:
            decomposition = seasonal_decompose(
                series_clean,
                period=period,
                model=model,
                extrapolate_trend='freq'
            )
            
            results = {
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'observed': decomposition.observed
            }
            
            self.results['decomposition'] = results
            return results
            
        except Exception as e:
            print(f"Decomposition failed: {e}")
            # Return simple decomposition
            rolling_mean = series_clean.rolling(window=min(30, len(series_clean)//10)).mean()
            trend = rolling_mean
            seasonal = series_clean - trend
            residual = seasonal - seasonal.mean()
            
            results = {
                'trend': trend,
                'seasonal': seasonal,
                'residual': residual,
                'observed': series_clean
            }
            
            self.results['decomposition'] = results
            return results
    
    def calculate_autocorrelation(self, max_lag: int = 50) -> Dict[str, Any]:
        """
        Calculate autocorrelation and partial autocorrelation
        
        Args:
            max_lag: Maximum lag to calculate
            
        Returns:
            Dictionary with ACF and PACF results
        """
        if self.series is None:
            raise ValueError("No series provided")
        
        series_clean = self.series.dropna()
        
        # Calculate ACF
        acf_values = []
        for lag in range(max_lag + 1):
            if lag == 0:
                acf_values.append(1.0)
            else:
                corr = series_clean.autocorr(lag=lag)
                acf_values.append(corr if not pd.isna(corr) else 0.0)
        
        # Calculate simple PACF approximation
        pacf_values = [1.0]  # Lag 0
        for lag in range(1, min(10, max_lag) + 1):  # Simple approximation for first 10 lags
            if lag < len(series_clean):
                # Simple partial correlation calculation
                try:
                    # Using OLS approximation for PACF
                    from sklearn.linear_model import LinearRegression
                    
                    X = np.zeros((len(series_clean) - lag, lag))
                    for i in range(lag):
                        X[:, i] = series_clean.shift(i + 1).dropna().values[:len(X)]
                    
                    y = series_clean.values[lag:]
                    X = X[:len(y)]
                    
                    if len(y) > lag + 1:
                        model = LinearRegression()
                        model.fit(X, y)
                        pacf = model.coef_[-1]  # Last coefficient
                        pacf_values.append(pacf)
                    else:
                        pacf_values.append(0.0)
                except:
                    pacf_values.append(0.0)
            else:
                pacf_values.append(0.0)
        
        # Pad PACF if needed
        if len(pacf_values) < max_lag + 1:
            pacf_values.extend([0.0] * (max_lag + 1 - len(pacf_values)))
        
        results = {
            'lags': list(range(max_lag + 1)),
            'acf': acf_values,
            'pacf': pacf_values[:max_lag + 1],
            'significant_lags': {
                'acf': [i for i, val in enumerate(acf_values) if abs(val) > 1.96/np.sqrt(len(series_clean))],
                'pacf': [i for i, val in enumerate(pacf_values[:max_lag + 1]) if abs(val) > 1.96/np.sqrt(len(series_clean))]
            }
        }
        
        self.results['autocorrelation'] = results
        return results
    
    def calculate_rolling_statistics(self, window: int = 30) -> Dict[str, pd.Series]:
        """
        Calculate rolling statistics
        
        Args:
            window: Rolling window size
            
        Returns:
            Dictionary with rolling statistics
        """
        if self.series is None:
            raise ValueError("No series provided")
        
        series_clean = self.series.dropna()
        
        results = {
            'mean': series_clean.rolling(window=window).mean(),
            'std': series_clean.rolling(window=window).std(),
            'min': series_clean.rolling(window=window).min(),
            'max': series_clean.rolling(window=window).max(),
            'median': series_clean.rolling(window=window).median(),
            'quantile_25': series_clean.rolling(window=window).quantile(0.25),
            'quantile_75': series_clean.rolling(window=window).quantile(0.75)
        }
        
        self.results['rolling_stats'] = results
        return results
    
    def detect_structural_breaks(self, method: str = 'cusum') -> Dict[str, Any]:
        """
        Detect structural breaks in time series
        
        Args:
            method: Detection method ('cusum' or 'rolling')
            
        Returns:
            Dictionary with break points
        """
        if self.series is None:
            raise ValueError("No series provided")
        
        series_clean = self.series.dropna()
        n = len(series_clean)
        
        if method == 'cusum':
            # CUSUM method for structural breaks
            mean = series_clean.mean()
            std = series_clean.std()
            
            # Calculate CUSUM
            cusum = np.zeros(n)
            for i in range(1, n):
                cusum[i] = cusum[i-1] + (series_clean.iloc[i] - mean)
            
            # Find break points where CUSUM changes sign significantly
            cusum_abs = np.abs(cusum)
            threshold = 2 * std * np.sqrt(n)
            
            break_points = []
            for i in range(1, n-1):
                if cusum_abs[i] > threshold and cusum[i] * cusum[i+1] < 0:
                    break_points.append(i)
            
            results = {
                'method': 'CUSUM',
                'break_points': break_points,
                'break_dates': [series_clean.index[i] for i in break_points] if hasattr(series_clean, 'index') else break_points,
                'threshold': threshold,
                'cusum_values': cusum
            }
            
        elif method == 'rolling':
            # Rolling window comparison method
            window = min(60, n // 10)
            rolling_mean = series_clean.rolling(window=window).mean()
            rolling_std = series_clean.rolling(window=window).std()
            
            # Detect significant changes in rolling statistics
            break_points = []
            for i in range(window, n - window):
                before_mean = rolling_mean.iloc[i-window:i].mean()
                after_mean = rolling_mean.iloc[i:i+window].mean()
                before_std = rolling_std.iloc[i-window:i].mean()
                
                # Test for significant change
                if before_std > 0:
                    z_score = abs(after_mean - before_mean) / before_std
                    if z_score > 2.0:  # 95% confidence
                        break_points.append(i)
            
            results = {
                'method': 'Rolling Window',
                'break_points': break_points,
                'break_dates': [series_clean.index[i] for i in break_points] if hasattr(series_clean, 'index') else break_points,
                'window_size': window
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        self.results['structural_breaks'] = results
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive time series summary
        
        Returns:
            Dictionary with all analysis results
        """
        summary = {
            'basic_stats': {
                'length': len(self.series) if self.series is not None else 0,
                'mean': float(self.series.mean()) if self.series is not None else None,
                'std': float(self.series.std()) if self.series is not None else None,
                'min': float(self.series.min()) if self.series is not None else None,
                'max': float(self.series.max()) if self.series is not None else None,
                'skewness': float(self.series.skew()) if self.series is not None else None,
                'kurtosis': float(self.series.kurtosis()) if self.series is not None else None
            }
        }
        
        # Add other results if available
        for key in ['stationarity', 'autocorrelation', 'structural_breaks']:
            if key in self.results:
                summary[key] = self.results[key]
        
        return summary

# Example usage
if __name__ == "__main__":
    # Create sample time series
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    values = 50 + np.random.randn(100).cumsum()
    series = pd.Series(values, index=dates)
    
    # Analyze
    analyzer = TimeSeriesAnalyzer(series)
    
    # Test stationarity
    stationarity = analyzer.test_stationarity()
    print(f"Stationarity: {stationarity['conclusion']}")
    
    # Decompose
    decomposition = analyzer.decompose(period=30)
    
    # Get autocorrelation
    acf = analyzer.calculate_autocorrelation(max_lag=20)
    
    # Get summary
    summary = analyzer.get_summary()
    print(f"Time series length: {summary['basic_stats']['length']}")
    print(f"Mean: {summary['basic_stats']['mean']:.2f}")