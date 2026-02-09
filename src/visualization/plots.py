"""
Static plotting functions for Brent oil analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class StaticPlotter:
    """
    Create static plots for Brent oil analysis
    """
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize plotter
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        sns.set_palette("husl")
        self.figures = {}
    
    def plot_price_series(self, df: pd.DataFrame, 
                         price_col: str = 'Price',
                         date_col: str = 'Date',
                         title: str = 'Brent Oil Price History',
                         figsize: Tuple[int, int] = (15, 6),
                         save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot price series over time
        
        Args:
            df: DataFrame with price data
            price_col: Name of price column
            date_col: Name of date column
            title: Plot title
            figsize: Figure size
            save_path: Path to save figure (optional)
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot price
        ax.plot(df[date_col], df[price_col], 
               color='steelblue', linewidth=1.5, alpha=0.8)
        
        # Add rolling mean
        rolling_mean = df[price_col].rolling(window=30).mean()
        ax.plot(df[date_col], rolling_mean, 
               color='darkred', linewidth=2, alpha=0.7, 
               label='30-Day Rolling Mean')
        
        # Formatting
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Price (USD per barrel)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        
        self.figures['price_series'] = fig
        return fig
    
    def plot_price_with_events(self, df: pd.DataFrame, 
                              events_df: pd.DataFrame,
                              price_col: str = 'Price',
                              date_col: str = 'Date',
                              figsize: Tuple[int, int] = (16, 8),
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot price series with event markers
        
        Args:
            df: DataFrame with price data
            events_df: DataFrame with event data
            price_col: Name of price column
            date_col: Name of date column
            figsize: Figure size
            save_path: Path to save figure (optional)
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot price
        ax.plot(df[date_col], df[price_col], 
               color='steelblue', linewidth=1, alpha=0.7, 
               label='Brent Oil Price')
        
        # Define event colors by type
        event_colors = {
            'Geopolitical Conflict': 'red',
            'Economic Crisis': 'orange',
            'Policy Decision': 'green',
            'Natural Disaster': 'brown',
            'Environmental Disaster': 'darkgreen',
            'Military Action': 'darkred',
            'Global Crisis': 'black',
            'Geopolitical Shock': 'purple'
        }
        
        # Plot events
        for _, event in events_df.iterrows():
            event_date = event['Date']
            event_type = event['Type']
            
            # Find closest date in price data
            date_diff = abs(df[date_col] - event_date)
            closest_idx = date_diff.idxmin()
            event_price = df.loc[closest_idx, price_col]
            
            # Get color for event type
            color = event_colors.get(event_type, 'gray')
            
            # Plot event marker
            ax.scatter(event_date, event_price, 
                      color=color, s=100, zorder=5, alpha=0.8,
                      label=event_type if event_type not in ax.get_legend_handles_labels()[1] else "")
            
            # Add annotation for major events
            if event.get('Impact_Expected', '') in ['High', 'Very High']:
                ax.annotate(event['Event'][:20], 
                           xy=(event_date, event_price),
                           xytext=(10, 10), 
                           textcoords='offset points',
                           fontsize=9, color=color,
                           arrowprops=dict(arrowstyle='->', 
                                         color=color, alpha=0.7))
        
        # Create custom legend for event types
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='steelblue', linewidth=2, label='Brent Price'),
            Line2D([0], [0], color='darkred', linewidth=2, label='30-Day Rolling Mean')
        ]
        
        for event_type, color in event_colors.items():
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor=color, markersize=10, label=event_type)
            )
        
        # Formatting
        ax.set_title('Brent Oil Prices with Major Events', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Price (USD per barrel)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        
        self.figures['price_with_events'] = fig
        return fig
    
    def plot_bayesian_results(self, trace, 
                             dates: pd.DatetimeIndex = None,
                             prices: np.ndarray = None,
                             figsize: Tuple[int, int] = (15, 10),
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot Bayesian change point analysis results
        
        Args:
            trace: PyMC trace or ArviZ InferenceData
            dates: Date index for x-axis
            prices: Original price data
            figsize: Figure size
            save_path: Path to save figure (optional)
            
        Returns:
            Matplotlib figure
        """
        import arviz as az
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # 1. Trace plot for tau
        if hasattr(trace, 'posterior') and 'tau' in trace.posterior:
            tau_samples = trace.posterior['tau'].values.flatten()
            
            axes[0, 0].plot(tau_samples[:1000], alpha=0.7)
            axes[0, 0].set_title('Trace Plot: Change Point (τ)', fontsize=11)
            axes[0, 0].set_xlabel('Sample')
            axes[0, 0].set_ylabel('τ')
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Posterior distribution of tau
        if hasattr(trace, 'posterior') and 'tau' in trace.posterior:
            axes[0, 1].hist(tau_samples, bins=50, edgecolor='black', alpha=0.7)
            axes[0, 1].set_title('Posterior Distribution: τ', fontsize=11)
            axes[0, 1].set_xlabel('τ (index)')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Before/After means
        if hasattr(trace, 'posterior'):
            mu_params = [var for var in trace.posterior.data_vars if var.startswith('mu_')]
            if len(mu_params) >= 2:
                mu_before = trace.posterior[mu_params[0]].values.flatten()
                mu_after = trace.posterior[mu_params[1]].values.flatten()
                
                axes[1, 0].hist(mu_before, bins=30, alpha=0.7, 
                               label='Before Change', density=True)
                axes[1, 0].hist(mu_after, bins=30, alpha=0.7, 
                               label='After Change', density=True)
                axes[1, 0].set_title('Posterior: Mean Before vs After', fontsize=11)
                axes[1, 0].set_xlabel('Mean Price (USD)')
                axes[1, 0].set_ylabel('Density')
                axes[1, 0].legend()
                axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Price series with change point
        if prices is not None and dates is not None:
            if hasattr(trace, 'posterior') and 'tau' in trace.posterior:
                tau_mean = np.mean(tau_samples)
                change_idx = int(tau_mean)
                
                if change_idx < len(dates):
                    axes[1, 1].plot(dates, prices, color='steelblue', linewidth=1)
                    axes[1, 1].axvline(dates[change_idx], color='red', 
                                      linestyle='--', linewidth=2,
                                      label=f'Change Point: {dates[change_idx].date()}')
                    axes[1, 1].set_title('Price Series with Change Point', fontsize=11)
                    axes[1, 1].set_xlabel('Date')
                    axes[1, 1].set_ylabel('Price (USD)')
                    axes[1, 1].legend()
                    axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        
        self.figures['bayesian_results'] = fig
        return fig
    
    def plot_distribution_comparison(self, before_data: np.ndarray,
                                   after_data: np.ndarray,
                                   labels: Tuple[str, str] = ('Before', 'After'),
                                   figsize: Tuple[int, int] = (12, 5),
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distribution comparison before and after change
        
        Args:
            before_data: Data before change
            after_data: Data after change
            labels: Labels for before/after
            figsize: Figure size
            save_path: Path to save figure (optional)
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # 1. Histograms
        axes[0].hist(before_data, bins=30, alpha=0.7, 
                    label=labels[0], density=True)
        axes[0].hist(after_data, bins=30, alpha=0.7, 
                    label=labels[1], density=True)
        axes[0].set_title('Distribution Comparison', fontsize=11)
        axes[0].set_xlabel('Value')
        axes[0].set_ylabel('Density')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 2. Box plots
        data_to_plot = [before_data, after_data]
        bp = axes[1].boxplot(data_to_plot, labels=labels, patch_artist=True)
        
        # Color the boxes
        colors = ['lightblue', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        axes[1].set_title('Box Plot Comparison', fontsize=11)
        axes[1].set_ylabel('Value')
        axes[1].grid(True, alpha=0.3)
        
        # 3. Violin plots
        vp = axes[2].violinplot(data_to_plot, showmeans=True)
        axes[2].set_xticks([1, 2])
        axes[2].set_xticklabels(labels)
        axes[2].set_title('Violin Plot Comparison', fontsize=11)
        axes[2].set_ylabel('Value')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        
        self.figures['distribution_comparison'] = fig
        return fig
    
    def plot_correlation_matrix(self, df: pd.DataFrame,
                               columns: List[str] = None,
                               figsize: Tuple[int, int] = (10, 8),
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot correlation matrix
        
        Args:
            df: DataFrame with numeric columns
            columns: Columns to include (all numeric if None)
            figsize: Figure size
            save_path: Path to save figure (optional)
            
        Returns:
            Matplotlib figure
        """
        if columns is None:
            # Select only numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            columns = numeric_cols[:10]  # Limit to 10 columns
        
        # Calculate correlation matrix
        corr_matrix = df[columns].corr()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Correlation', rotation=-90, va="bottom")
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(columns)))
        ax.set_yticks(np.arange(len(columns)))
        ax.set_xticklabels(columns, rotation=45, ha='right')
        ax.set_yticklabels(columns)
        
        # Add correlation values
        for i in range(len(columns)):
            for j in range(len(columns)):
                value = corr_matrix.iloc[i, j]
                color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', 
                       ha='center', va='center', color=color,
                       fontsize=9)
        
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")
        
        self.figures['correlation_matrix'] = fig
        return fig
    
    def save_all_figures(self, directory: str) -> None:
        """
        Save all generated figures
        
        Args:
            directory: Directory to save figures
        """
        import os
        os.makedirs(directory, exist_ok=True)
        
        for name, fig in self.figures.items():
            filepath = os.path.join(directory, f'{name}.png')
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved {name} to {filepath}")

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    prices = 50 + np.random.randn(100).cumsum()
    
    df = pd.DataFrame({
        'Date': dates,
        'Price': prices,
        'Volume': np.random.randint(1000, 5000, 100)
    })
    
    # Create sample events
    events_df = pd.DataFrame({
        'Date': [dates[30], dates[70]],
        'Event': ['Event 1', 'Event 2'],
        'Type': ['Geopolitical Conflict', 'Economic Crisis'],
        'Impact_Expected': ['High', 'Medium']
    })
    events_df['Date'] = pd.to_datetime(events_df['Date'])
    
    # Create plots
    plotter = StaticPlotter()
    
    # Plot price series
    plotter.plot_price_series(df, title='Sample Price Series')
    
    # Plot with events
    plotter.plot_price_with_events(df, events_df)
    
    # Show plots
    plt.show()