"""
Data cleaning and preprocessing for Brent oil prices
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class BrentDataCleaner:
    """
    Clean and preprocess Brent oil price data
    """
    
    def __init__(self):
        """Initialize data cleaner"""
        pass
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw Brent oil price data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        print("🧹 Cleaning data...")
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # 1. Parse dates
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='%d-%b-%y', errors='coerce')
        
        # 2. Remove rows with invalid dates
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['Date'])
        removed_invalid_dates = initial_count - len(df_clean)
        
        if removed_invalid_dates > 0:
            print(f"   Removed {removed_invalid_dates} rows with invalid dates")
        
        # 3. Sort by date
        df_clean = df_clean.sort_values('Date').reset_index(drop=True)
        
        # 4. Handle missing prices
        missing_before = df_clean['Price'].isnull().sum()
        if missing_before > 0:
            # Forward fill for missing prices
            df_clean['Price'] = df_clean['Price'].fillna(method='ffill')
            print(f"   Forward-filled {missing_before} missing prices")
        
        # 5. Remove duplicate dates (keep first occurrence)
        duplicates = df_clean['Date'].duplicated().sum()
        if duplicates > 0:
            df_clean = df_clean[~df_clean['Date'].duplicated(keep='first')]
            print(f"   Removed {duplicates} duplicate dates")
        
        # 6. Create date features
        df_clean = self._create_date_features(df_clean)
        
        # 7. Calculate returns
        df_clean = self._calculate_returns(df_clean)
        
        print(f"✅ Data cleaning complete. Final shape: {df_clean.shape}")
        
        return df_clean
    
    def _create_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create date-based features
        
        Args:
            df: DataFrame with Date column
            
        Returns:
            DataFrame with additional features
        """
        df = df.copy()
        
        # Set Date as index
        df.set_index('Date', inplace=True)
        
        # Date features
        df['Year'] = df.index.year
        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['DayOfWeek'] = df.index.dayofweek
        df['WeekOfYear'] = df.index.isocalendar().week
        df['Quarter'] = df.index.quarter
        df['YearMonth'] = df.index.to_period('M')
        
        # Reset index to keep Date as column
        df.reset_index(inplace=True)
        
        return df
    
    def _calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price returns
        
        Args:
            df: DataFrame with Price column
            
        Returns:
            DataFrame with return columns
        """
        df = df.copy()
        
        # Ensure sorted by date
        df = df.sort_values('Date')
        
        # Calculate returns
        df['Price_Change'] = df['Price'].diff()
        df['Pct_Change'] = df['Price'].pct_change() * 100
        df['Log_Return'] = np.log(df['Price'] / df['Price'].shift(1))
        
        # Calculate rolling statistics
        df['Rolling_Mean_30'] = df['Price'].rolling(window=30).mean()
        df['Rolling_Std_30'] = df['Price'].rolling(window=30).std()
        df['Rolling_Vol_30'] = df['Log_Return'].rolling(window=30).std() * np.sqrt(252)
        
        return df
    
    def save_cleaned_data(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save cleaned data to CSV
        
        Args:
            df: Cleaned DataFrame
            output_path: Path to save cleaned data
        """
        try:
            df.to_csv(output_path, index=False)
            print(f"✅ Cleaned data saved to {output_path}")
        except Exception as e:
            print(f"❌ Error saving cleaned data: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    from loader import BrentDataLoader
    
    # Load data
    loader = BrentDataLoader()
    raw_df = loader.load_raw_data()
    
    # Clean data
    cleaner = BrentDataCleaner()
    cleaned_df = cleaner.clean_data(raw_df)
    
    # Save cleaned data
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output_path = os.path.join(current_dir, 'data', 'processed', 'cleaned_prices.csv')
    cleaner.save_cleaned_data(cleaned_df, output_path)