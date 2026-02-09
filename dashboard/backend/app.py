"""
Flask Backend API for Brent Oil Dashboard
Task 3: Developing an Interactive Dashboard for Data Analysis Results
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load data
def load_data():
    """Load all preprocessed data for the dashboard"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Load price data
    price_data = pd.read_csv(os.path.join(data_dir, 'dashboard_data.csv'), 
                            parse_dates=['Date'], index_col='Date')
    
    # Load events data
    events_data = pd.read_csv(os.path.join(data_dir, 'dashboard_events.csv'), 
                             parse_dates=['Date'])
    
    # Load change point results
    with open(os.path.join(data_dir, 'change_point_results.json'), 'r') as f:
        change_point_results = json.load(f)
    
    # Load posterior samples
    with open(os.path.join(data_dir, 'posterior_samples.json'), 'r') as f:
        posterior_samples = json.load(f)
    
    return {
        'price_data': price_data,
        'events_data': events_data,
        'change_point_results': change_point_results,
        'posterior_samples': posterior_samples
    }

# Load data once at startup
DATA = load_data()

@app.route('/')
def home():
    """API Home endpoint"""
    return jsonify({
        'message': 'Brent Oil Dashboard API',
        'endpoints': {
            '/api/health': 'Check API health',
            '/api/price': 'Get price data (optional date range)',
            '/api/events': 'Get event data',
            '/api/change-points': 'Get change point analysis results',
            '/api/statistics': 'Get price statistics',
            '/api/volatility': 'Get volatility metrics',
            '/api/event-impact/<event_id>': 'Get impact analysis for specific event'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_points': len(DATA['price_data']),
        'events_count': len(DATA['events_data'])
    })

@app.route('/api/price', methods=['GET'])
def get_price_data():
    """Get price data with optional date filtering"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        price_df = DATA['price_data'].copy()
        
        # Apply date filtering if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            price_df = price_df[price_df.index >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            price_df = price_df[price_df.index <= end_date]
        
        # Convert to JSON-friendly format
        response_data = {
            'dates': price_df.index.strftime('%Y-%m-%d').tolist(),
            'prices': price_df['Price'].tolist(),
            'log_returns': price_df['Log_Return'].tolist() if 'Log_Return' in price_df.columns else []
        }
        
        return jsonify({
            'success': True,
            'data': response_data,
            'count': len(price_df),
            'date_range': {
                'start': price_df.index.min().strftime('%Y-%m-%d'),
                'end': price_df.index.max().strftime('%Y-%m-%d')
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get event data with optional filtering"""
    try:
        event_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        events_df = DATA['events_data'].copy()
        
        # Apply filters
        if event_type and event_type != 'all':
            events_df = events_df[events_df['Type'] == event_type]
        
        if start_date:
            start_date = pd.to_datetime(start_date)
            events_df = events_df[events_df['Date'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            events_df = events_df[events_df['Date'] <= end_date]
        
        # Convert to list of dictionaries
        events_list = events_df.to_dict('records')
        
        # Convert dates to strings
        for event in events_list:
            event['Date'] = event['Date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'events': events_list,
            'count': len(events_list),
            'event_types': DATA['events_data']['Type'].unique().tolist()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get change point analysis results"""
    try:
        # Get main change point results
        cp_results = DATA['change_point_results']
        
        # Get posterior samples
        posterior = DATA['posterior_samples']
        
        # Calculate additional statistics
        price_df = DATA['price_data']
        cp_date = pd.to_datetime(cp_results['change_date'])
        
        # Find price before and after (30-day windows)
        before_window = price_df.loc[cp_date - timedelta(days=30):cp_date]
        after_window = price_df.loc[cp_date:cp_date + timedelta(days=30)]
        
        response_data = {
            'change_point': {
                'date': cp_results['change_date'],
                'mu_before': cp_results['mu_before'],
                'mu_after': cp_results['mu_after'],
                'difference': cp_results['difference'],
                'percentage_change': cp_results['percentage_change'],
                'probability_increase': cp_results['prob_increase']
            },
            'posterior_samples': {
                'tau': posterior['tau'][:500],  # Limit for performance
                'mu_before': posterior['mu_before'][:500],
                'mu_after': posterior['mu_after'][:500],
                'sigma': posterior['sigma'][:500]
            },
            'context': {
                'before_window_avg': float(before_window['Price'].mean()),
                'after_window_avg': float(after_window['Price'].mean()),
                'before_window_std': float(before_window['Price'].std()),
                'after_window_std': float(after_window['Price'].std())
            }
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive price statistics"""
    try:
        price_df = DATA['price_data']
        
        # Calculate statistics
        stats = {
            'overall': {
                'mean': float(price_df['Price'].mean()),
                'median': float(price_df['Price'].median()),
                'std': float(price_df['Price'].std()),
                'min': float(price_df['Price'].min()),
                'max': float(price_df['Price'].max()),
                'count': int(len(price_df))
            },
            'returns': {
                'mean_return': float(price_df['Log_Return'].mean()) if 'Log_Return' in price_df.columns else 0,
                'std_return': float(price_df['Log_Return'].std()) if 'Log_Return' in price_df.columns else 0,
                'annualized_vol': float(price_df['Log_Return'].std() * np.sqrt(252)) if 'Log_Return' in price_df.columns else 0
            },
            'by_year': {},
            'by_month': {}
        }
        
        # Yearly statistics
        price_df['Year'] = price_df.index.year
        yearly_stats = price_df.groupby('Year')['Price'].agg(['mean', 'std', 'min', 'max']).reset_index()
        for _, row in yearly_stats.iterrows():
            stats['by_year'][str(int(row['Year']))] = {
                'mean': float(row['mean']),
                'std': float(row['std']),
                'min': float(row['min']),
                'max': float(row['max'])
            }
        
        # Monthly statistics
        price_df['Month'] = price_df.index.month
        monthly_stats = price_df.groupby('Month')['Price'].mean().reset_index()
        for _, row in monthly_stats.iterrows():
            stats['by_month'][int(row['Month'])] = float(row['Price'])
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'date_range': {
                'start': price_df.index.min().strftime('%Y-%m-%d'),
                'end': price_df.index.max().strftime('%Y-%m-%d')
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    """Get volatility metrics and rolling volatility"""
    try:
        price_df = DATA['price_data']
        
        if 'Log_Return' not in price_df.columns:
            return jsonify({
                'success': False,
                'error': 'Log returns not available in data'
            }), 400
        
        # Calculate rolling volatility (30-day, annualized)
        returns = price_df['Log_Return'].dropna()
        rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
        
        # High volatility periods (top 10%)
        vol_threshold = rolling_vol.quantile(0.9)
        high_vol_periods = rolling_vol[rolling_vol > vol_threshold]
        
        response_data = {
            'rolling_volatility': {
                'dates': rolling_vol.index.strftime('%Y-%m-%d').tolist(),
                'values': rolling_vol.tolist()
            },
            'metrics': {
                'average_volatility': float(rolling_vol.mean()),
                'max_volatility': float(rolling_vol.max()),
                'min_volatility': float(rolling_vol.min()),
                'current_volatility': float(rolling_vol.iloc[-1]) if len(rolling_vol) > 0 else 0
            },
            'high_volatility_periods': [
                {
                    'date': idx.strftime('%Y-%m-%d'),
                    'volatility': float(val)
                }
                for idx, val in high_vol_periods.items()
            ][:20]  # Limit to 20 periods
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/event-impact/<event_name>', methods=['GET'])
def get_event_impact(event_name):
    """Analyze impact of specific event on oil prices"""
    try:
        # Find the event
        events_df = DATA['events_data']
        event = events_df[events_df['Event'].str.contains(event_name, case=False, na=False)]
        
        if len(event) == 0:
            return jsonify({
                'success': False,
                'error': f'Event "{event_name}" not found'
            }), 404
        
        event = event.iloc[0]
        event_date = event['Date']
        
        # Get price data around event
        price_df = DATA['price_data']
        
        # Define windows (30 days before and after)
        before_window = price_df.loc[event_date - timedelta(days=30):event_date]
        after_window = price_df.loc[event_date:event_date + timedelta(days=30)]
        
        # Calculate impact metrics
        if len(before_window) > 0 and len(after_window) > 0:
            before_mean = before_window['Price'].mean()
            after_mean = after_window['Price'].mean()
            price_change = after_mean - before_mean
            percent_change = (price_change / before_mean) * 100
            
            # Statistical significance (t-test)
            from scipy import stats
            t_stat, p_value = stats.ttest_ind(before_window['Price'], after_window['Price'])
            
            impact_data = {
                'event': {
                    'name': event['Event'],
                    'date': event_date.strftime('%Y-%m-%d'),
                    'type': event['Type'],
                    'description': event['Description']
                },
                'impact_metrics': {
                    'price_before': float(before_mean),
                    'price_after': float(after_mean),
                    'absolute_change': float(price_change),
                    'percent_change': float(percent_change),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                },
                'price_data': {
                    'before_dates': before_window.index.strftime('%Y-%m-%d').tolist(),
                    'before_prices': before_window['Price'].tolist(),
                    'after_dates': after_window.index.strftime('%Y-%m-%d').tolist(),
                    'after_prices': after_window['Price'].tolist()
                }
            }
            
            return jsonify({
                'success': True,
                'data': impact_data
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Insufficient data around event date'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/search-events', methods=['GET'])
def search_events():
    """Search events by keyword"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': True,
                'events': [],
                'count': 0
            })
        
        events_df = DATA['events_data']
        
        # Search in Event and Description columns
        mask = (events_df['Event'].str.contains(query, case=False, na=False) |
                events_df['Description'].str.contains(query, case=False, na=False))
        
        results = events_df[mask].to_dict('records')
        
        # Convert dates to strings
        for event in results:
            event['Date'] = event['Date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'events': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)