"""
Data validation functions for Brent oil analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """
    Validate data quality and integrity
    """
    
    def __init__(self):
        """Initialize data validator"""
        pass
    
    def validate_dataframe(self, df: pd.DataFrame, 
                          required_columns: List[str] = None,
                          date_column: str = None,
                          numeric_columns: List[str] = None) -> Dict[str, Any]:
        """
        Validate DataFrame structure and content
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            date_column: Name of date column (if any)
            numeric_columns: List of numeric column names
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check if DataFrame is empty
        if df.empty:
            validation_results['is_valid'] = False
            validation_results['errors'].append('DataFrame is empty')
            return validation_results
        
        # Check required columns
        if required_columns:
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f'Missing required columns: {missing_columns}')
        
        # Check date column
        if date_column and date_column in df.columns:
            date_validation = self._validate_date_column(df[date_column], date_column)
            validation_results['stats']['date_validation'] = date_validation
            
            if not date_validation['is_valid']:
                validation_results['is_valid'] = False
                validation_results['errors'].extend(date_validation['errors'])
        
        # Check numeric columns
        if numeric_columns:
            for col in numeric_columns:
                if col in df.columns:
                    numeric_validation = self._validate_numeric_column(df[col], col)
                    validation_results['stats'][f'{col}_validation'] = numeric_validation
                    
                    if not numeric_validation['is_valid']:
                        validation_results['is_valid'] = False
                        validation_results['errors'].extend(numeric_validation['errors'])
        
        # Check for duplicates
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            validation_results['warnings'].append(f'Found {duplicate_rows} duplicate rows')
            validation_results['stats']['duplicate_rows'] = duplicate_rows
        
        # Check for missing values
        missing_stats = df.isnull().sum()
        total_missing = missing_stats.sum()
        
        if total_missing > 0:
            missing_pct = (total_missing / (len(df) * len(df.columns))) * 100
            validation_results['warnings'].append(f'Found {total_missing} missing values ({missing_pct:.2f}%)')
            validation_results['stats']['missing_values'] = {
                'total': int(total_missing),
                'percentage': float(missing_pct),
                'by_column': missing_stats.to_dict()
            }
        
        # Calculate basic statistics
        validation_results['stats']['basic'] = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        return validation_results
    
    def _validate_date_column(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """
        Validate date column
        
        Args:
            series: Date series
            column_name: Name of the column
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check for missing values
        missing_count = series.isnull().sum()
        if missing_count > 0:
            validation['warnings'].append(f'Date column has {missing_count} missing values')
        
        # Try to parse dates
        try:
            parsed_dates = pd.to_datetime(series, errors='coerce')
            invalid_count = parsed_dates.isnull().sum() - missing_count
            
            if invalid_count > 0:
                validation['is_valid'] = False
                validation['errors'].append(f'Date column has {invalid_count} invalid dates')
            
            # Check date range
            valid_dates = parsed_dates.dropna()
            if len(valid_dates) > 0:
                validation['stats']['date_range'] = {
                    'min': valid_dates.min(),
                    'max': valid_dates.max(),
                    'days': (valid_dates.max() - valid_dates.min()).days,
                    'unique_dates': valid_dates.nunique()
                }
                
                # Check for duplicate dates
                duplicate_dates = valid_dates.duplicated().sum()
                if duplicate_dates > 0:
                    validation['warnings'].append(f'Found {duplicate_dates} duplicate dates')
                
                # Check for gaps in dates
                if len(valid_dates) > 1:
                    date_diff = valid_dates.sort_values().diff().dropna()
                    if not date_diff.empty:
                        max_gap = date_diff.max()
                        min_gap = date_diff.min()
                        
                        if max_gap.days > 1:
                            validation['warnings'].append(f'Maximum date gap: {max_gap.days} days')
                        
                        validation['stats']['date_gaps'] = {
                            'max_gap_days': max_gap.days,
                            'min_gap_days': min_gap.days,
                            'avg_gap_days': date_diff.mean().days
                        }
        
        except Exception as e:
            validation['is_valid'] = False
            validation['errors'].append(f'Failed to parse dates: {str(e)}')
        
        return validation
    
    def _validate_numeric_column(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """
        Validate numeric column
        
        Args:
            series: Numeric series
            column_name: Name of the column
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check for missing values
        missing_count = series.isnull().sum()
        if missing_count > 0:
            validation['warnings'].append(f'Numeric column has {missing_count} missing values')
        
        # Get non-missing values
        clean_series = series.dropna()
        
        if len(clean_series) > 0:
            # Check if values are numeric
            try:
                numeric_series = pd.to_numeric(clean_series, errors='coerce')
                non_numeric_count = numeric_series.isnull().sum()
                
                if non_numeric_count > 0:
                    validation['is_valid'] = False
                    validation['errors'].append(f'Column has {non_numeric_count} non-numeric values')
                
                # Calculate statistics
                validation['stats'] = {
                    'count': len(numeric_series),
                    'mean': float(numeric_series.mean()),
                    'std': float(numeric_series.std()),
                    'min': float(numeric_series.min()),
                    'max': float(numeric_series.max()),
                    'median': float(numeric_series.median()),
                    'q25': float(numeric_series.quantile(0.25)),
                    'q75': float(numeric_series.quantile(0.75)),
                    'skewness': float(numeric_series.skew()),
                    'kurtosis': float(numeric_series.kurtosis())
                }
                
                # Check for zeros
                zero_count = (numeric_series == 0).sum()
                if zero_count > 0:
                    validation['warnings'].append(f'Found {zero_count} zero values')
                
                # Check for negative values (if applicable)
                negative_count = (numeric_series < 0).sum()
                if negative_count > 0:
                    validation['warnings'].append(f'Found {negative_count} negative values')
                
                # Check for outliers using IQR method
                Q1 = numeric_series.quantile(0.25)
                Q3 = numeric_series.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    validation['warnings'].append(f'Found {outlier_count} outliers using IQR method')
                    validation['stats']['outliers'] = {
                        'count': outlier_count,
                        'percentage': (outlier_count / len(numeric_series)) * 100,
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    }
            
            except Exception as e:
                validation['is_valid'] = False
                validation['errors'].append(f'Failed to validate numeric column: {str(e)}')
        
        return validation
    
    def check_data_quality_score(self, df: pd.DataFrame, 
                                date_column: str = 'Date',
                                price_column: str = 'Price') -> Dict[str, Any]:
        """
        Calculate overall data quality score
        
        Args:
            df: DataFrame to evaluate
            date_column: Name of date column
            price_column: Name of price column
            
        Returns:
            Dictionary with quality score and metrics
        """
        quality_metrics = {
            'completeness': 0.0,
            'validity': 0.0,
            'consistency': 0.0,
            'timeliness': 0.0,
            'overall_score': 0.0,
            'issues': []
        }
        
        total_records = len(df)
        if total_records == 0:
            return quality_metrics
        
        # 1. Completeness (missing values)
        missing_total = df.isnull().sum().sum()
        completeness = 1 - (missing_total / (total_records * len(df.columns)))
        quality_metrics['completeness'] = completeness * 100
        
        if missing_total > 0:
            quality_metrics['issues'].append(f'Missing values: {missing_total}')
        
        # 2. Validity (data format and ranges)
        validity_score = 0
        validity_checks = 0
        
        # Check date column
        if date_column in df.columns:
            validity_checks += 1
            try:
                parsed_dates = pd.to_datetime(df[date_column], errors='coerce')
                invalid_dates = parsed_dates.isnull().sum()
                if invalid_dates == 0:
                    validity_score += 1
                else:
                    quality_metrics['issues'].append(f'Invalid dates: {invalid_dates}')
            except:
                quality_metrics['issues'].append('Date parsing failed')
        
        # Check price column
        if price_column in df.columns:
            validity_checks += 1
            try:
                prices = pd.to_numeric(df[price_column], errors='coerce')
                invalid_prices = prices.isnull().sum()
                negative_prices = (prices < 0).sum()
                
                if invalid_prices == 0 and negative_prices == 0:
                    validity_score += 1
                else:
                    if invalid_prices > 0:
                        quality_metrics['issues'].append(f'Invalid prices: {invalid_prices}')
                    if negative_prices > 0:
                        quality_metrics['issues'].append(f'Negative prices: {negative_prices}')
            except:
                quality_metrics['issues'].append('Price validation failed')
        
        quality_metrics['validity'] = (validity_score / max(validity_checks, 1)) * 100
        
        # 3. Consistency (no duplicates, logical consistency)
        duplicate_rows = df.duplicated().sum()
        consistency = 1 - (duplicate_rows / total_records)
        quality_metrics['consistency'] = consistency * 100
        
        if duplicate_rows > 0:
            quality_metrics['issues'].append(f'Duplicate rows: {duplicate_rows}')
        
        # 4. Timeliness (data is up-to-date)
        if date_column in df.columns:
            try:
                latest_date = pd.to_datetime(df[date_column]).max()
                days_since_update = (pd.Timestamp.now() - latest_date).days
                
                if days_since_update <= 7:
                    timeliness = 1.0
                elif days_since_update <= 30:
                    timeliness = 0.7
                elif days_since_update <= 90:
                    timeliness = 0.4
                else:
                    timeliness = 0.1
                
                quality_metrics['timeliness'] = timeliness * 100
                quality_metrics['days_since_update'] = days_since_update
                
                if days_since_update > 30:
                    quality_metrics['issues'].append(f'Data is {days_since_update} days old')
            
            except:
                quality_metrics['timeliness'] = 0.0
        
        # Calculate overall score (weighted average)
        weights = {
            'completeness': 0.3,
            'validity': 0.3,
            'consistency': 0.2,
            'timeliness': 0.2
        }
        
        overall_score = (
            quality_metrics['completeness'] * weights['completeness'] +
            quality_metrics['validity'] * weights['validity'] +
            quality_metrics['consistency'] * weights['consistency'] +
            quality_metrics['timeliness'] * weights['timeliness']
        ) / sum(weights.values())
        
        quality_metrics['overall_score'] = overall_score
        
        # Add rating
        if overall_score >= 90:
            quality_metrics['rating'] = 'Excellent'
        elif overall_score >= 80:
            quality_metrics['rating'] = 'Good'
        elif overall_score >= 70:
            quality_metrics['rating'] = 'Fair'
        elif overall_score >= 60:
            quality_metrics['rating'] = 'Poor'
        else:
            quality_metrics['rating'] = 'Unacceptable'
        
        return quality_metrics

# Example usage
if __name__ == "__main__":
    # Create test data
    test_data = {
        'Date': ['2023-01-01', '2023-01-02', 'invalid', '2023-01-04'],
        'Price': [100, 105, 'invalid', 108],
        'Volume': [1000, 1100, 1200, None]
    }
    
    df = pd.DataFrame(test_data)
    
    # Validate DataFrame
    validator = DataValidator()
    validation = validator.validate_dataframe(
        df,
        required_columns=['Date', 'Price'],
        date_column='Date',
        numeric_columns=['Price', 'Volume']
    )
    
    print(f"Is valid: {validation['is_valid']}")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")
    
    # Calculate quality score
    quality = validator.check_data_quality_score(df, date_column='Date', price_column='Price')
    print(f"\nData Quality Score: {quality['overall_score']:.1f}% ({quality['rating']})")