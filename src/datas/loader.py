"""
Data loading module for Brent oil prices
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class BrentDataLoader:
    """
    Load and manage Brent oil price data
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize data loader
        
        Args:
            data_path: Path to data directory
        """
        if data_path is None:
            # Default to project data directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_path = os.path.join(current_dir, 'data', 'raw', 'brent_oil_prices.csv')
        
        self.data_path = data_path
        self.df = None
        
    def load_raw_data(self) -> pd.DataFrame:
        """
        Load raw Brent oil price data from CSV
        
        Returns:
            DataFrame with raw data
        """
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✅ Data loaded successfully from {self.data_path}")
            print(f"📊 Shape: {self.df.shape}")
            print(f"📅 Date range: {self.df['Date'].min()} to {self.df['Date'].max()}")
            return self.df
        except FileNotFoundError:
            print(f"❌ File not found: {self.data_path}")
            raise
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise
    
    def validate_data(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Validate data quality and completeness
        
        Args:
            df: DataFrame to validate (uses self.df if None)
            
        Returns:
            Dictionary with validation results
        """
        if df is None:
            df = self.df
            
        if df is None:
            raise ValueError("No data to validate. Load data first.")
        
        validation_results = {
            'total_records': len(df),
            'date_column_exists': 'Date' in df.columns,
            'price_column_exists': 'Price' in df.columns,
            'missing_dates': 0,
            'missing_prices': df['Price'].isnull().sum(),
            'duplicate_dates': 0,
            'negative_prices': (df['Price'] < 0).sum(),
            'zero_prices': (df['Price'] == 0).sum(),
            'date_format_valid': True,
            'price_range': {
                'min': float(df['Price'].min()),
                'max': float(df['Price'].max()),
                'mean': float(df['Price'].mean()),
                'std': float(df['Price'].std())
            }
        }
        
        # Check date parsing
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
            validation_results['date_format_valid'] = True
        except:
            validation_results['date_format_valid'] = False
            
        # Check for missing dates if dates can be parsed
        if validation_results['date_format_valid']:
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
            date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='D')
            validation_results['missing_dates'] = len(date_range.difference(df['Date']))
            validation_results['duplicate_dates'] = df['Date'].duplicated().sum()
            
        return validation_results
    
    def print_validation_report(self, validation_results: Dict[str, Any]) -> None:
        """
        Print formatted validation report
        
        Args:
            validation_results: Dictionary from validate_data()
        """
        print("\n" + "="*60)
        print("DATA VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 Basic Information:")
        print(f"   Total Records: {validation_results['total_records']:,}")
        print(f"   Date Column: {'✅ Present' if validation_results['date_column_exists'] else '❌ Missing'}")
        print(f"   Price Column: {'✅ Present' if validation_results['price_column_exists'] else '❌ Missing'}")
        
        print(f"\n🔍 Data Quality:")
        print(f"   Missing Prices: {validation_results['missing_prices']}")
        print(f"   Negative Prices: {validation_results['negative_prices']}")
        print(f"   Zero Prices: {validation_results['zero_prices']}")
        print(f"   Date Format Valid: {'✅ Yes' if validation_results['date_format_valid'] else '❌ No'}")
        
        if validation_results['date_format_valid']:
            print(f"   Missing Dates: {validation_results['missing_dates']}")
            print(f"   Duplicate Dates: {validation_results['duplicate_dates']}")
        
        print(f"\n📈 Price Statistics:")
        stats = validation_results['price_range']
        print(f"   Minimum: ${stats['min']:.2f}")
        print(f"   Maximum: ${stats['max']:.2f}")
        print(f"   Mean: ${stats['mean']:.2f}")
        print(f"   Std Dev: ${stats['std']:.2f}")
        
        print("\n" + "="*60)

# Example usage
if __name__ == "__main__":
    loader = BrentDataLoader()
    df = loader.load_raw_data()
    validation = loader.validate_data(df)
    loader.print_validation_report(validation)