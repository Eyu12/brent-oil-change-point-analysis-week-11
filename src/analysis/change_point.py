"""
Change point detection and analysis utilities
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class ChangePointAnalyzer:
    """
    Traditional (non-Bayesian) change point detection methods
    """
    
    def __init__(self):
        """Initialize change point analyzer"""
        pass
    
    def detect_cusum(self, series: pd.Series, threshold: float = None) -> Dict[str, Any]:
        """
        Detect change points using CUSUM method
        
        Args:
            series: Time series data
            threshold: Detection threshold (default: 2 * std)
            
        Returns:
            Dictionary with change point information
        """
        values = series.values
        n = len(values)
        
        if n < 10:
            return {'error': 'Series too short for CUSUM analysis'}
        
        # Calculate CUSUM
        mean = np.mean(values)
        cusum = np.zeros(n)
        
        for i in range(1, n):
            cusum[i] = cusum[i-1] + (values[i] - mean)
        
        # Set threshold if not provided
        if threshold is None:
            threshold = 2 * np.std(values)
        
        # Find change points where CUSUM exceeds threshold
        change_points = []
        in_change = False
        
        for i in range(1, n):
            if abs(cusum[i]) > threshold and not in_change:
                change_points.append(i)
                in_change = True
            elif abs(cusum[i]) <= threshold and in_change:
                in_change = False
        
        # Calculate statistics for each segment
        segments = []
        prev_cp = 0
        
        for cp in change_points + [n]:  # Add end point
            segment = values[prev_cp:cp]
            if len(segment) > 0:
                segments.append({
                    'start': prev_cp,
                    'end': cp,
                    'length': len(segment),
                    'mean': float(np.mean(segment)),
                    'std': float(np.std(segment)),
                    'values': segment.tolist()
                })
            prev_cp = cp
        
        return {
            'method': 'CUSUM',
            'threshold': threshold,
            'change_points': change_points,
            'cusum_values': cusum.tolist(),
            'segments': segments,
            'n_segments': len(segments)
        }
    
    def detect_rolling_window(self, series: pd.Series, 
                             window_size: int = 30,
                             z_threshold: float = 2.0) -> Dict[str, Any]:
        """
        Detect change points using rolling window method
        
        Args:
            series: Time series data
            window_size: Size of rolling window
            z_threshold: Z-score threshold for detection
            
        Returns:
            Dictionary with change point information
        """
        values = series.values
        n = len(values)
        
        if n < window_size * 2:
            return {'error': f'Series too short for window size {window_size}'}
        
        # Calculate rolling statistics
        rolling_mean = pd.Series(values).rolling(window=window_size, center=True).mean()
        rolling_std = pd.Series(values).rolling(window=window_size, center=True).std()
        
        # Detect change points
        change_points = []
        
        for i in range(window_size, n - window_size):
            # Compare statistics before and after point i
            before_mean = np.mean(values[i-window_size:i])
            after_mean = np.mean(values[i:i+window_size])
            before_std = np.std(values[i-window_size:i])
            
            if before_std > 0:
                z_score = abs(after_mean - before_mean) / before_std
                
                if z_score > z_threshold:
                    # Check if this is a new change point (not too close to previous)
                    if not change_points or (i - change_points[-1]) > window_size:
                        change_points.append(i)
        
        # Calculate segment statistics
        segments = []
        prev_cp = 0
        
        for cp in change_points + [n]:
            segment = values[prev_cp:cp]
            if len(segment) > 0:
                segments.append({
                    'start': prev_cp,
                    'end': cp,
                    'length': len(segment),
                    'mean': float(np.mean(segment)),
                    'std': float(np.std(segment)),
                    'median': float(np.median(segment)),
                    'change_from_previous': None
                })
            prev_cp = cp
        
        # Calculate changes between segments
        for i in range(1, len(segments)):
            prev_mean = segments[i-1]['mean']
            curr_mean = segments[i]['mean']
            change = ((curr_mean - prev_mean) / abs(prev_mean)) * 100 if prev_mean != 0 else 0
            segments[i]['change_from_previous'] = float(change)
        
        return {
            'method': 'Rolling Window',
            'window_size': window_size,
            'z_threshold': z_threshold,
            'change_points': change_points,
            'rolling_mean': rolling_mean.dropna().tolist(),
            'rolling_std': rolling_std.dropna().tolist(),
            'segments': segments,
            'n_segments': len(segments)
        }
    
    def detect_binary_segmentation(self, series: pd.Series, 
                                  max_points: int = 5,
                                  min_segment_length: int = 10) -> Dict[str, Any]:
        """
        Detect change points using binary segmentation
        
        Args:
            series: Time series data
            max_points: Maximum number of change points to find
            min_segment_length: Minimum segment length
            
        Returns:
            Dictionary with change point information
        """
        values = series.values
        n = len(values)
        
        if n < min_segment_length * 2:
            return {'error': f'Series too short for minimum segment length {min_segment_length}'}
        
        def find_best_split(start: int, end: int) -> Tuple[int, float]:
            """Find best split point in segment [start, end)"""
            if end - start < 2 * min_segment_length:
                return -1, 0.0
            
            best_split = -1
            best_score = 0.0
            
            for split in range(start + min_segment_length, end - min_segment_length):
                # Calculate variance reduction
                left_var = np.var(values[start:split])
                right_var = np.var(values[split:end])
                total_var = np.var(values[start:end])
                
                # Score based on variance reduction
                score = total_var - (left_var + right_var)
                
                if score > best_score:
                    best_score = score
                    best_split = split
            
            return best_split, best_score
        
        # Recursive binary segmentation
        def segment_recursive(start: int, end: int, depth: int = 0):
            if depth >= max_points or end - start < 2 * min_segment_length:
                return []
            
            split, score = find_best_split(start, end)
            
            if split == -1 or score == 0:
                return []
            
            left_points = segment_recursive(start, split, depth + 1)
            right_points = segment_recursive(split, end, depth + 1)
            
            return left_points + [split] + right_points
        
        # Find change points
        change_points = segment_recursive(0, n)
        change_points.sort()
        
        # Calculate segment statistics
        segments = []
        prev_cp = 0
        
        for cp in change_points + [n]:
            segment = values[prev_cp:cp]
            if len(segment) > 0:
                segments.append({
                    'start': prev_cp,
                    'end': cp,
                    'length': len(segment),
                    'mean': float(np.mean(segment)),
                    'std': float(np.std(segment)),
                    'variance': float(np.var(segment))
                })
            prev_cp = cp
        
        # Calculate total variance reduction
        total_var = np.var(values)
        segmented_var = sum(seg['variance'] * seg['length'] for seg in segments) / n
        variance_reduction = ((total_var - segmented_var) / total_var) * 100 if total_var > 0 else 0
        
        return {
            'method': 'Binary Segmentation',
            'max_points': max_points,
            'min_segment_length': min_segment_length,
            'change_points': change_points,
            'segments': segments,
            'n_segments': len(segments),
            'variance_reduction_percent': float(variance_reduction),
            'total_variance': float(total_var),
            'segmented_variance': float(segmented_var)
        }
    
    def compare_methods(self, series: pd.Series) -> Dict[str, Any]:
        """
        Compare different change point detection methods
        
        Args:
            series: Time series data
            
        Returns:
            Dictionary with comparison results
        """
        results = {}
        
        # CUSUM method
        try:
            cusum_result = self.detect_cusum(series)
            results['cusum'] = {
                'change_points': cusum_result.get('change_points', []),
                'n_points': len(cusum_result.get('change_points', [])),
                'segments': cusum_result.get('segments', []),
                'n_segments': cusum_result.get('n_segments', 0)
            }
        except Exception as e:
            results['cusum'] = {'error': str(e)}
        
        # Rolling window method
        try:
            window_size = min(30, len(series) // 10)
            rolling_result = self.detect_rolling_window(series, window_size=window_size)
            results['rolling_window'] = {
                'change_points': rolling_result.get('change_points', []),
                'n_points': len(rolling_result.get('change_points', [])),
                'segments': rolling_result.get('segments', []),
                'n_segments': rolling_result.get('n_segments', 0)
            }
        except Exception as e:
            results['rolling_window'] = {'error': str(e)}
        
        # Binary segmentation
        try:
            binary_result = self.detect_binary_segmentation(series)
            results['binary_segmentation'] = {
                'change_points': binary_result.get('change_points', []),
                'n_points': len(binary_result.get('change_points', [])),
                'segments': binary_result.get('segments', []),
                'n_segments': binary_result.get('n_segments', 0),
                'variance_reduction': binary_result.get('variance_reduction_percent', 0)
            }
        except Exception as e:
            results['binary_segmentation'] = {'error': str(e)}
        
        # Find consensus change points
        all_points = []
        for method, result in results.items():
            if 'change_points' in result:
                all_points.extend(result['change_points'])
        
        # Count occurrences
        from collections import Counter
        point_counts = Counter(all_points)
        
        # Consensus points (detected by at least 2 methods)
        consensus_points = [point for point, count in point_counts.items() if count >= 2]
        consensus_points.sort()
        
        results['consensus'] = {
            'points': consensus_points,
            'n_points': len(consensus_points),
            'detection_counts': dict(point_counts)
        }
        
        return results
    
    def calculate_segment_statistics(self, series: pd.Series, 
                                    change_points: List[int]) -> Dict[str, Any]:
        """
        Calculate statistics for segments defined by change points
        
        Args:
            series: Time series data
            change_points: List of change point indices
            
        Returns:
            Dictionary with segment statistics
        """
        values = series.values
        n = len(values)
        
        # Add start and end points
        points = [0] + sorted(change_points) + [n]
        
        segments = []
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            segment = values[start:end]
            
            if len(segment) > 0:
                stats = {
                    'segment_id': i + 1,
                    'start_index': start,
                    'end_index': end,
                    'length': len(segment),
                    'mean': float(np.mean(segment)),
                    'median': float(np.median(segment)),
                    'std': float(np.std(segment)),
                    'min': float(np.min(segment)),
                    'max': float(np.max(segment)),
                    'range': float(np.max(segment) - np.min(segment)),
                    'q1': float(np.percentile(segment, 25)),
                    'q3': float(np.percentile(segment, 75)),
                    'iqr': float(np.percentile(segment, 75) - np.percentile(segment, 25))
                }
                
                # Calculate change from previous segment
                if i > 0:
                    prev_mean = segments[i-1]['mean']
                    curr_mean = stats['mean']
                    stats['change_from_previous'] = float((curr_mean - prev_mean) / abs(prev_mean) * 100 if prev_mean != 0 else 0)
                    stats['absolute_change'] = float(curr_mean - prev_mean)
                else:
                    stats['change_from_previous'] = 0.0
                    stats['absolute_change'] = 0.0
                
                segments.append(stats)
        
        # Calculate overall statistics
        means = [seg['mean'] for seg in segments]
        stds = [seg['std'] for seg in segments]
        
        overall_stats = {
            'n_segments': len(segments),
            'avg_segment_length': np.mean([seg['length'] for seg in segments]),
            'total_length': n,
            'mean_of_means': float(np.mean(means)),
            'std_of_means': float(np.std(means)),
            'avg_std': float(np.mean(stds)),
            'max_mean_change': max([abs(seg['change_from_previous']) for seg in segments[1:]], default=0)
        }
        
        return {
            'segments': segments,
            'overall': overall_stats,
            'change_points': change_points
        }

# Example usage
if __name__ == "__main__":
    # Create sample data with change points
    np.random.seed(42)
    n = 300
    
    # Create a time series with multiple change points
    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    values = np.concatenate([
        np.random.normal(50, 5, 100),   # Segment 1
        np.random.normal(70, 8, 100),   # Segment 2 (change at 100)
        np.random.normal(45, 6, 100)    # Segment 3 (change at 200)
    ])
    
    series = pd.Series(values, index=dates)
    
    # Analyze change points
    analyzer = ChangePointAnalyzer()
    
    # Compare methods
    comparison = analyzer.compare_methods(series)
    
    print("Change Point Detection Comparison")
    print("="*50)
    
    for method, result in comparison.items():
        if method != 'consensus':
            print(f"\n{method.replace('_', ' ').title()}:")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Detected points: {result['change_points']}")
                print(f"  Number of segments: {result['n_segments']}")
    
    # Consensus points
    consensus = comparison['consensus']
    print(f"\nConsensus Change Points:")
    print(f"  Points: {consensus['points']}")
    print(f"  Detection counts: {consensus['detection_counts']}")
    
    # Calculate segment statistics for consensus points
    if consensus['points']:
        stats = analyzer.calculate_segment_statistics(series, consensus['points'])
        
        print(f"\nSegment Statistics:")
        print(f"  Number of segments: {stats['overall']['n_segments']}")
        print(f"  Average segment length: {stats['overall']['avg_segment_length']:.1f}")
        print(f"  Standard deviation of means: {stats['overall']['std_of_means']:.2f}")
        
        print(f"\nIndividual Segments:")
        for seg in stats['segments']:
            print(f"  Segment {seg['segment_id']}: "
                  f"mean={seg['mean']:.2f}, "
                  f"length={seg['length']}, "
                  f"change={seg['change_from_previous']:.1f}%")