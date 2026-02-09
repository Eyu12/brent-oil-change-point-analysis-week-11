"""
Tests for analysis modules
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path
# Add src to path
PROJECT_ROOT = Path().resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.eda import BrentEDA
from src.analysis.time_series import TimeSeriesAnalyzer
from src.analysis.bayesian import BayesianChangePointAnalyzer

class TestBrentEDA:
    """Test EDA functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create test data
        dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
        prices = 50 + np.random.randn(len(dates)).cumsum()
        
        self.test_df = pd.DataFrame({
            'Date': dates,
            'Price': prices,
            'Log_Return': np.random.randn(len(dates)) * 0.01
        })
        
        self.eda = BrentEDA(self.test_df)
        
    def test_eda_initialization(self):
        """Test EDA initialization"""
        assert self.eda is not None
        assert self.eda.df is not None
        assert len(self.eda.df) > 0
        
    def test_basic_statistics(self):
        """Test basic statistics calculation"""
        results = self.eda.run_comprehensive_eda()
        
        assert 'basic_stats' in results
        basic_stats = results['basic_stats']
        
        assert 'count' in basic_stats
        assert 'date_range' in basic_stats
        assert 'price_stats' in basic_stats
        
        assert basic_stats['count'] == len(self.test_df)
        assert 'mean' in basic_stats['price_stats']
        assert 'std' in basic_stats['price_stats']
        
    def test_time_series_analysis(self):
        """Test time series analysis"""
        results = self.eda.run_comprehensive_eda()
        
        assert 'time_series' in results
        ts_analysis = results['time_series']
        
        # Check stationarity tests are present
        if 'Log_Return' in self.test_df.columns:
            assert 'stationarity_returns' in ts_analysis
            
    def test_distribution_analysis(self):
        """Test distribution analysis"""
        results = self.eda.run_comprehensive_eda()
        
        assert 'distributions' in results
        dist_analysis = results['distributions']
        
        assert 'price' in dist_analysis
        if 'Log_Return' in self.test_df.columns:
            assert 'returns' in dist_analysis
            
    def test_seasonality_analysis(self):
        """Test seasonality analysis"""
        # Add month column for testing
        self.test_df['Month'] = self.test_df['Date'].dt.month
        self.test_df['DayOfWeek'] = self.test_df['Date'].dt.dayofweek
        
        results = self.eda.run_comprehensive_eda()
        
        assert 'seasonality' in results
        season_analysis = results['seasonality']
        
        assert 'monthly' in season_analysis
        assert 'day_of_week' in season_analysis
        
    def test_volatility_analysis(self):
        """Test volatility analysis"""
        results = self.eda.run_comprehensive_eda()
        
        assert 'volatility' in results
        vol_analysis = results['volatility']
        
        if 'Log_Return' in self.test_df.columns:
            assert 'annualized_volatility' in vol_analysis
            
    def test_outlier_detection(self):
        """Test outlier detection"""
        results = self.eda.run_comprehensive_eda()
        
        assert 'outliers' in results
        outliers = results['outliers']
        
        assert 'method' in outliers
        assert 'outlier_count' in outliers
        assert 'outlier_percentage' in outliers

class TestTimeSeriesAnalyzer:
    """Test time series analysis functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create test data
        np.random.seed(42)
        n = 100
        self.test_series = pd.Series(
            50 + np.random.randn(n).cumsum(),
            index=pd.date_range(start='2020-01-01', periods=n, freq='D')
        )
        
        self.analyzer = TimeSeriesAnalyzer(self.test_series)
        
    def test_stationarity_tests(self):
        """Test stationarity tests"""
        results = self.analyzer.test_stationarity()
        
        assert 'adf' in results
        assert 'kpss' in results
        
        adf_result = results['adf']
        assert 'statistic' in adf_result
        assert 'p_value' in adf_result
        assert 'is_stationary' in adf_result
        
    def test_decomposition(self):
        """Test time series decomposition"""
        decomposition = self.analyzer.decompose(period=30)
        
        assert 'trend' in decomposition
        assert 'seasonal' in decomposition
        assert 'residual' in decomposition
        
        # Check all components have same length
        assert len(decomposition['trend']) == len(self.test_series)
        
    def test_autocorrelation(self):
        """Test autocorrelation analysis"""
        acf_result = self.analyzer.calculate_autocorrelation(max_lag=20)
        
        assert 'lags' in acf_result
        assert 'values' in acf_result
        assert len(acf_result['values']) == 21  # Includes lag 0
        
    def test_rolling_statistics(self):
        """Test rolling statistics calculation"""
        window = 30
        rolling_stats = self.analyzer.calculate_rolling_statistics(window=window)
        
        assert 'mean' in rolling_stats
        assert 'std' in rolling_stats
        assert 'min' in rolling_stats
        assert 'max' in rolling_stats
        
        # Check lengths (accounting for window)
        assert len(rolling_stats['mean']) == len(self.test_series) - window + 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])