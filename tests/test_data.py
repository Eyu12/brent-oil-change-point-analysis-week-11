"""
Tests for data loading and cleaning
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.datas.loader import BrentDataLoader
from src.datas.cleaner import BrentDataCleaner
from src.datas.events import EventManager

class TestBrentDataLoader:
    """Test data loading functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.loader = BrentDataLoader()
        
    def test_loader_initialization(self):
        """Test loader initialization"""
        assert self.loader is not None
        assert hasattr(self.loader, 'data_path')
        assert hasattr(self.loader, 'df')
        
    def test_validate_data_structure(self):
        """Test data structure validation"""
        # Create test data
        test_data = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87'],
            'Price': [18.63, 18.45, 18.50]
        })
        
        validation = self.loader.validate_data(test_data)
        
        assert validation['total_records'] == 3
        assert validation['date_column_exists'] == True
        assert validation['price_column_exists'] == True
        assert validation['missing_prices'] == 0
        assert validation['negative_prices'] == 0
        assert 'price_range' in validation

class TestBrentDataCleaner:
    """Test data cleaning functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.cleaner = BrentDataCleaner()
        
    def test_cleaner_initialization(self):
        """Test cleaner initialization"""
        assert self.cleaner is not None
        
    def test_date_parsing(self):
        """Test date parsing functionality"""
        test_data = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87'],
            'Price': [18.63, 18.45, 18.50]
        })
        
        cleaned = self.cleaner.clean_data(test_data)
        
        assert 'Date' in cleaned.columns
        assert pd.api.types.is_datetime64_any_dtype(cleaned['Date'])
        assert len(cleaned) == 3
        
    def test_missing_value_handling(self):
        """Test missing value handling"""
        test_data = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87', '23-May-87'],
            'Price': [18.63, None, 18.50, None]
        })
        
        cleaned = self.cleaner.clean_data(test_data)
        
        assert cleaned['Price'].isnull().sum() == 0
        assert len(cleaned) == 4
        
    def test_date_features_creation(self):
        """Test creation of date features"""
        test_data = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87'],
            'Price': [18.63, 18.45, 18.50]
        })
        
        cleaned = self.cleaner.clean_data(test_data)
        
        expected_features = ['Year', 'Month', 'Day', 'DayOfWeek', 'WeekOfYear', 'Quarter', 'YearMonth']
        for feature in expected_features:
            assert feature in cleaned.columns
            
    def test_return_calculation(self):
        """Test calculation of returns"""
        test_data = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87', '23-May-87'],
            'Price': [100, 105, 102, 108]
        })
        
        cleaned = self.cleaner.clean_data(test_data)
        
        assert 'Price_Change' in cleaned.columns
        assert 'Pct_Change' in cleaned.columns
        assert 'Log_Return' in cleaned.columns
        
        # Test specific calculations
        expected_change = 105 - 100
        assert cleaned['Price_Change'].iloc[1] == pytest.approx(expected_change, rel=1e-3)
        
        expected_pct = (105/100 - 1) * 100
        assert cleaned['Pct_Change'].iloc[1] == pytest.approx(expected_pct, rel=1e-3)

class TestEventManager:
    """Test event management functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.event_manager = EventManager()
        
    def test_compile_events(self):
        """Test event compilation"""
        events_df = self.event_manager.compile_events()
        
        assert events_df is not None
        assert len(events_df) > 0
        assert 'Date' in events_df.columns
        assert 'Event' in events_df.columns
        assert 'Type' in events_df.columns
        
    def test_event_enrichment(self):
        """Test event enrichment with price data"""
        # Create test price data
        price_data = pd.DataFrame({
            'Date': pd.date_range(start='1990-01-01', end='1990-12-31', freq='D'),
            'Price': np.random.normal(20, 5, 365)
        })
        
        events_df = self.event_manager.compile_events()
        enriched_df = self.event_manager.enrich_with_price_data(price_data)
        
        # Check that enrichment columns were added
        expected_columns = ['Price_At_Event', 'Price_Before_30d', 'Price_After_30d', 
                          'Price_Change_30d', 'Pct_Change_30d']
        
        for col in expected_columns:
            assert col in enriched_df.columns
            
    def test_event_summary(self):
        """Test event summary generation"""
        self.event_manager.compile_events()
        summary = self.event_manager.get_event_summary()
        
        assert 'total_events' in summary
        assert 'event_types' in summary
        assert 'impact_levels' in summary
        assert 'date_range' in summary
        
        assert isinstance(summary['total_events'], int)
        assert summary['total_events'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])