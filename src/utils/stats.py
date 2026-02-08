"""
Statistical functions for Brent oil analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, dict, any
import warnings
warnings.filterwarnings('ignore')

def calculate_descriptive_stats(series: pd.Series) -> dict[str, float]:
    """
    Calculate descriptive statistics
    
    Args:
        series: Input series
        
    Returns:
        dictionary with descriptive statistics
    """
    stats_dict = {
        'count': len(series),
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'variance': float(series.var()),
        'min': float(series.min()),
        'max': float(series.max()),
        'range': float(series.max() - series.min()),
        'q1': float(series.quantile(0.25)),
        'q3': float(series.quantile(0.75)),
        'iqr': float(series.quantile(0.75) - series.quantile(0.25)),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis()),
        'cv': float(series.std() / series.mean() if series.mean() != 0 else np.nan)  # Coefficient of variation
    }
    
    return stats_dict

def test_normality(series: pd.Series, tests: list = ['shapiro', 'dagostino', 'jarque_bera']) -> dict[str, any]:
    """
    Test for normality using multiple tests
    
    Args:
        series: Input series
        tests: List of tests to perform
        
    Returns:
        dictionary with test results
    """
    series_clean = series.dropna()
    if len(series_clean) < 3:
        return {'error': 'Insufficient data for normality tests'}
    
    results = {}
    
    for test_name in tests:
        if test_name == 'shapiro':
            if len(series_clean) < 5000:  # Shapiro-Wilk works up to 5000 samples
                stat, p_value = stats.shapiro(series_clean)
                results['shapiro_wilk'] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'is_normal': p_value > 0.05
                }
        
        elif test_name == 'dagostino':
            stat, p_value = stats.normaltest(series_clean)
            results['dagostino'] = {
                'statistic': stat,
                'p_value': p_value,
                'is_normal': p_value > 0.05
            }
        
        elif test_name == 'jarque_bera':
            stat, p_value = stats.jarque_bera(series_clean)
            results['jarque_bera'] = {
                'statistic': stat,
                'p_value': p_value,
                'is_normal': p_value > 0.05
            }
        
        elif test_name == 'anderson':
            result = stats.anderson(series_clean, dist='norm')
            results['anderson_darling'] = {
                'statistic': result.statistic,
                'critical_values': result.critical_values,
                'significance_levels': result.significance_level,
                'is_normal': result.statistic < result.critical_values[2]  # 5% level
            }
    
    # Overall conclusion
    normal_tests = [v.get('is_normal', False) for v in results.values() if 'is_normal' in v]
    if normal_tests:
        results['overall_conclusion'] = 'Normal' if all(normal_tests) else 'Not Normal'
    
    return results

def calculate_correlation(x: pd.Series, y: pd.Series, method: str = 'pearson') -> dict[str, any]:
    """
    Calculate correlation between two series
    
    Args:
        x: First series
        y: Second series
        method: 'pearson', 'spearman', or 'kendall'
        
    Returns:
        dictionary with correlation results
    """
    # Align series and drop NaN
    df = pd.DataFrame({'x': x, 'y': y}).dropna()
    
    if len(df) < 2:
        return {'error': 'Insufficient data for correlation'}
    
    if method == 'pearson':
        corr, p_value = stats.pearsonr(df['x'], df['y'])
    elif method == 'spearman':
        corr, p_value = stats.spearmanr(df['x'], df['y'])
    elif method == 'kendall':
        corr, p_value = stats.kendalltau(df['x'], df['y'])
    else:
        raise ValueError(f"Unknown correlation method: {method}")
    
    # Calculate confidence interval
    n = len(df)
    z = 1.96  # 95% confidence
    se = 1 / np.sqrt(n - 3)
    ci_lower = np.tanh(np.arctanh(corr) - z * se)
    ci_upper = np.tanh(np.arctanh(corr) + z * se)
    
    # Interpret strength
    abs_corr = abs(corr)
    if abs_corr >= 0.8:
        strength = 'Very Strong'
    elif abs_corr >= 0.6:
        strength = 'Strong'
    elif abs_corr >= 0.4:
        strength = 'Moderate'
    elif abs_corr >= 0.2:
        strength = 'Weak'
    else:
        strength = 'Very Weak'
    
    return {
        'method': method,
        'correlation': corr,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'confidence_interval': (ci_lower, ci_upper),
        'strength': strength,
        'sample_size': n
    }

def perform_ttest(sample1: pd.Series, sample2: pd.Series, alternative: str = 'two-sided') -> dict[str, any]:
    """
    Perform t-test between two samples
    
    Args:
        sample1: First sample
        sample2: Second sample
        alternative: 'two-sided', 'less', or 'greater'
        
    Returns:
        dictionary with t-test results
    """
    # Clean and align samples
    df = pd.DataFrame({'sample1': sample1, 'sample2': sample2}).dropna()
    
    if len(df) < 2:
        return {'error': 'Insufficient data for t-test'}
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(df['sample1'], df['sample2'], 
                                      equal_var=False,  # Welch's t-test
                                      alternative=alternative)
    
    # Calculate effect size (Cohen's d)
    n1 = len(df['sample1'])
    n2 = len(df['sample2'])
    mean1 = df['sample1'].mean()
    mean2 = df['sample2'].mean()
    var1 = df['sample1'].var()
    var2 = df['sample2'].var()
    
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (mean1 - mean2) / pooled_std if pooled_std != 0 else 0
    
    # Interpret effect size
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        effect_size = 'Large'
    elif abs_d >= 0.5:
        effect_size = 'Medium'
    elif abs_d >= 0.2:
        effect_size = 'Small'
    else:
        effect_size = 'Negligible'
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'cohens_d': cohens_d,
        'effect_size': effect_size,
        'sample1_stats': {
            'n': n1,
            'mean': mean1,
            'std': np.sqrt(var1)
        },
        'sample2_stats': {
            'n': n2,
            'mean': mean2,
            'std': np.sqrt(var2)
        },
        'alternative': alternative
    }

def calculate_confidence_interval(series: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for mean
    
    Args:
        series: Input series
        confidence: Confidence level (0.95 for 95%)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    series_clean = series.dropna()
    n = len(series_clean)
    
    if n < 2:
        return (np.nan, np.nan)
    
    mean = series_clean.mean()
    std = series_clean.std()
    sem = std / np.sqrt(n)  # Standard error of the mean
    
    # Calculate critical value (t-distribution for small samples)
    if n < 30:
        from scipy.stats import t
        critical_value = t.ppf((1 + confidence) / 2, df=n-1)
    else:
        from scipy.stats import norm
        critical_value = norm.ppf((1 + confidence) / 2)
    
    margin_of_error = critical_value * sem
    
    return (mean - margin_of_error, mean + margin_of_error)

def calculate_regression_stats(x: pd.Series, y: pd.Series) -> dict[str, any]:
    """
    Calculate linear regression statistics
    
    Args:
        x: Independent variable
        y: Dependent variable
        
    Returns:
        dictionary with regression results
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_squared_error
    
    # Align and clean data
    df = pd.DataFrame({'x': x, 'y': y}).dropna()
    
    if len(df) < 2:
        return {'error': 'Insufficient data for regression'}
    
    X = df['x'].values.reshape(-1, 1)
    y_values = df['y'].values
    
    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y_values)
    
    # Predictions
    y_pred = model.predict(X)
    
    # Calculate statistics
    r2 = r2_score(y_values, y_pred)
    mse = mean_squared_error(y_values, y_pred)
    rmse = np.sqrt(mse)
    
    # Calculate standard errors
    residuals = y_values - y_pred
    n = len(y_values)
    p = 1  # Number of predictors
    
    # Standard error of coefficients
    if n > p + 1:
        residual_variance = np.sum(residuals ** 2) / (n - p - 1)
        x_mean = np.mean(X)
        x_var = np.var(X)
        se_intercept = np.sqrt(residual_variance * (1/n + x_mean**2/(n * x_var))) if x_var > 0 else np.nan
        se_slope = np.sqrt(residual_variance / (n * x_var)) if x_var > 0 else np.nan
    else:
        se_intercept = se_slope = np.nan
    
    return {
        'intercept': model.intercept_,
        'slope': model.coef_[0],
        'r_squared': r2,
        'mse': mse,
        'rmse': rmse,
        'se_intercept': se_intercept,
        'se_slope': se_slope,
        'n_observations': n,
        'predictions': y_pred.tolist()
    }

# Test the functions
if __name__ == "__main__":
    # Create test data
    np.random.seed(42)
    n = 100
    x = pd.Series(np.random.randn(n))
    y = pd.Series(2 * x + np.random.randn(n) * 0.5)
    
    # Test descriptive stats
    stats = calculate_descriptive_stats(x)
    print(f"Mean: {stats['mean']:.4f}")
    print(f"Std: {stats['std']:.4f}")
    
    # Test normality
    normality = test_normality(x, tests=['shapiro', 'dagostino'])
    print(f"Normal: {normality.get('overall_conclusion', 'Unknown')}")
    
    # Test correlation
    corr = calculate_correlation(x, y, method='pearson')
    print(f"Correlation: {corr['correlation']:.4f} ({corr['strength']})")
    
    # Test t-test
    ttest = perform_ttest(x[:50], x[50:])
    print(f"T-test p-value: {ttest['p_value']:.4f}")
    
    # Test confidence interval
    ci = calculate_confidence_interval(x)
    print(f"95% CI: ({ci[0]:.4f}, {ci[1]:.4f})")