"""
General helper functions for Brent oil analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from typing import Any, Dict, List, Optional, Union

def create_directory(path: str) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to JSON file
    """
    create_directory(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary with loaded data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def format_currency(value: float) -> str:
    """
    Format number as currency
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted currency string
    """
    return f"${value:,.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage
    
    Args:
        value: Numeric value (0.1 = 10%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value*100:.{decimals}f}%"

def calculate_date_range(start_date: str, end_date: str, freq: str = 'D') -> pd.DatetimeIndex:
    """
    Generate date range
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        freq: Frequency ('D' for daily, 'M' for monthly)
        
    Returns:
        DatetimeIndex
    """
    return pd.date_range(start=start_date, end=end_date, freq=freq)

def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> Dict[str, Any]:
    """
    Detect outliers using IQR method
    
    Args:
        series: Input series
        multiplier: IQR multiplier (default 1.5)
        
    Returns:
        Dictionary with outlier information
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    
    return {
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'outliers': outliers,
        'outlier_count': len(outliers),
        'outlier_percentage': len(outliers) / len(series) * 100,
        'method': f'IQR (multiplier={multiplier})'
    }

def calculate_returns(prices: pd.Series, method: str = 'log') -> pd.Series:
    """
    Calculate returns from price series
    
    Args:
        prices: Price series
        method: 'log' for log returns, 'simple' for simple returns
        
    Returns:
        Returns series
    """
    if method == 'log':
        return np.log(prices / prices.shift(1))
    elif method == 'simple':
        return prices.pct_change()
    else:
        raise ValueError(f"Unknown method: {method}")

def calculate_volatility(returns: pd.Series, window: int = 30, annualize: bool = True) -> pd.Series:
    """
    Calculate rolling volatility
    
    Args:
        returns: Returns series
        window: Rolling window size
        annualize: Whether to annualize volatility
        
    Returns:
        Volatility series
    """
    volatility = returns.rolling(window=window).std()
    
    if annualize:
        # Annualize assuming 252 trading days
        volatility = volatility * np.sqrt(252)
    
    return volatility

def print_table(data: List[Dict], headers: List[str] = None, title: str = None) -> None:
    """
    Print data as formatted table
    
    Args:
        data: List of dictionaries
        headers: Column headers (uses dict keys if None)
        title: Table title
    """
    if not data:
        print("No data to display")
        return
    
    if headers is None:
        headers = list(data[0].keys())
    
    # Calculate column widths
    col_widths = []
    for header in headers:
        max_len = len(str(header))
        for row in data:
            max_len = max(max_len, len(str(row.get(header, ''))))
        col_widths.append(max_len + 2)
    
    # Print title
    if title:
        print(f"\n{title}")
        print("=" * sum(col_widths))
    
    # Print headers
    header_row = "".join([f"{header:<{width}}" for header, width in zip(headers, col_widths)])
    print(header_row)
    print("-" * sum(col_widths))
    
    # Print data rows
    for row in data:
        row_str = "".join([f"{str(row.get(header, '')):<{width}}" for header, width in zip(headers, col_widths)])
        print(row_str)

def get_project_root() -> str:
    """
    Get project root directory
    
    Returns:
        Project root path
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels from src/utils
    return os.path.dirname(os.path.dirname(current_dir))

def setup_logging(log_file: str = None, level: str = 'INFO') -> None:
    """
    Setup logging configuration
    
    Args:
        log_file: Log file path (optional)
        level: Logging level
    """
    import logging
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            filename=log_file,
            filemode='a',
            format=log_format,
            level=getattr(logging, level)
        )
    else:
        logging.basicConfig(
            format=log_format,
            level=getattr(logging, level)
        )

# Test the functions
if __name__ == "__main__":
    # Test outlier detection
    test_series = pd.Series([1, 2, 3, 4, 5, 100])
    outliers = detect_outliers_iqr(test_series)
    print(f"Outliers detected: {outliers['outlier_count']}")
    
    # Test returns calculation
    prices = pd.Series([100, 105, 102, 108])
    log_returns = calculate_returns(prices, method='log')
    print(f"Log returns: {log_returns.tolist()}")