"""
Event data compilation and management
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os

class EventManager:
    """
    Manage geopolitical and economic events for oil market analysis
    """
    
    def __init__(self):
        """Initialize event manager"""
        self.events_df = None
        
    def compile_events(self) -> pd.DataFrame:
        """
        Compile major events affecting oil prices
        
        Returns:
            DataFrame with events
        """
        print("📚 Compiling major events...")
        
        events_data = [
            # 1990s
            {
                'Date': '1990-08-02',
                'Event': 'Iraq Invades Kuwait',
                'Type': 'Geopolitical Conflict',
                'Description': 'Start of Gulf War, major oil supply disruption',
                'Impact_Expected': 'High',
                'Region': 'Middle East',
                'Oil_Production_Impact': 'Supply Disruption'
            },
            {
                'Date': '1991-01-17',
                'Event': 'Operation Desert Storm',
                'Type': 'Military Action',
                'Description': 'Coalition intervention in Gulf War',
                'Impact_Expected': 'High',
                'Region': 'Middle East',
                'Oil_Production_Impact': 'Supply Uncertainty'
            },
            {
                'Date': '1997-07-02',
                'Event': 'Asian Financial Crisis',
                'Type': 'Economic Crisis',
                'Description': 'Regional economic collapse affecting demand',
                'Impact_Expected': 'Medium',
                'Region': 'Asia',
                'Oil_Production_Impact': 'Demand Shock'
            },
            {
                'Date': '1999-04-01',
                'Event': 'OPEC Production Cut (1.7M bpd)',
                'Type': 'Policy Decision',
                'Description': 'Supply reduction to boost prices',
                'Impact_Expected': 'High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Supply Reduction'
            },
            
            # 2000s
            {
                'Date': '2001-09-11',
                'Event': '9/11 Terrorist Attacks',
                'Type': 'Geopolitical Shock',
                'Description': 'Global uncertainty and security concerns',
                'Impact_Expected': 'High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Demand Uncertainty'
            },
            {
                'Date': '2003-03-20',
                'Event': 'Iraq War Begins',
                'Type': 'Geopolitical Conflict',
                'Description': 'Major Middle East conflict affecting supply',
                'Impact_Expected': 'High',
                'Region': 'Middle East',
                'Oil_Production_Impact': 'Supply Disruption'
            },
            {
                'Date': '2005-08-29',
                'Event': 'Hurricane Katrina',
                'Type': 'Natural Disaster',
                'Description': 'US Gulf Coast production disruption',
                'Impact_Expected': 'Medium',
                'Region': 'North America',
                'Oil_Production_Impact': 'Supply Disruption'
            },
            {
                'Date': '2008-09-15',
                'Event': 'Lehman Brothers Collapse',
                'Type': 'Economic Crisis',
                'Description': 'Global Financial Crisis begins',
                'Impact_Expected': 'Very High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Demand Collapse'
            },
            {
                'Date': '2008-12-01',
                'Event': 'OPEC Production Cut (2.2M bpd)',
                'Type': 'Policy Decision',
                'Description': 'Response to falling demand',
                'Impact_Expected': 'High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Supply Reduction'
            },
            
            # 2010s
            {
                'Date': '2010-04-20',
                'Event': 'Deepwater Horizon Spill',
                'Type': 'Environmental Disaster',
                'Description': 'Major US oil spill, regulatory impacts',
                'Impact_Expected': 'Medium',
                'Region': 'North America',
                'Oil_Production_Impact': 'Regulatory Impact'
            },
            {
                'Date': '2011-02-15',
                'Event': 'Arab Spring',
                'Type': 'Geopolitical Conflict',
                'Description': 'Middle East instability',
                'Impact_Expected': 'High',
                'Region': 'Middle East',
                'Oil_Production_Impact': 'Supply Uncertainty'
            },
            {
                'Date': '2014-06-01',
                'Event': 'OPEC Maintains Production',
                'Type': 'Policy Decision',
                'Description': 'Market share strategy despite oversupply',
                'Impact_Expected': 'High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Supply Glut'
            },
            {
                'Date': '2016-01-01',
                'Event': 'Paris Agreement Signed',
                'Type': 'Policy Decision',
                'Description': 'Climate commitments affect long-term outlook',
                'Impact_Expected': 'Low',
                'Region': 'Global',
                'Oil_Production_Impact': 'Long-term Demand Impact'
            },
            
            # 2020s
            {
                'Date': '2020-03-11',
                'Event': 'COVID-19 Pandemic Declared',
                'Type': 'Global Crisis',
                'Description': 'Unprecedented demand collapse',
                'Impact_Expected': 'Very High',
                'Region': 'Global',
                'Oil_Production_Impact': 'Demand Collapse'
            },
            {
                'Date': '2022-02-24',
                'Event': 'Russia Invades Ukraine',
                'Type': 'Geopolitical Conflict',
                'Description': 'Major supply disruptions and sanctions',
                'Impact_Expected': 'Very High',
                'Region': 'Europe/Asia',
                'Oil_Production_Impact': 'Supply Disruption'
            }
        ]
        
        self.events_df = pd.DataFrame(events_data)
        self.events_df['Date'] = pd.to_datetime(self.events_df['Date'])
        
        print(f"✅ Compiled {len(self.events_df)} events")
        print(f"📅 Event date range: {self.events_df['Date'].min().date()} to {self.events_df['Date'].max().date()}")
        
        return self.events_df
    
    def enrich_with_price_data(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price information to events
        
        Args:
            price_df: DataFrame with price data (must have Date and Price columns)
            
        Returns:
            Enriched events DataFrame
        """
        if self.events_df is None:
            self.compile_events()
        
        print("📈 Enriching events with price data...")
        
        # Make sure price_df has Date as datetime
        price_df = price_df.copy()
        if 'Date' in price_df.columns:
            price_df['Date'] = pd.to_datetime(price_df['Date'])
            price_df.set_index('Date', inplace=True)
        
        # Add price at event date
        self.events_df['Price_At_Event'] = self.events_df['Date'].apply(
            lambda x: price_df.loc[x, 'Price'] if x in price_df.index else None
        )
        
        # Add price change windows (30 days before/after)
        for idx, event in self.events_df.iterrows():
            event_date = event['Date']
            
            # Get price window
            before_window = price_df.loc[event_date - pd.Timedelta(days=30):event_date]
            after_window = price_df.loc[event_date:event_date + pd.Timedelta(days=30)]
            
            if len(before_window) > 0 and len(after_window) > 0:
                # Calculate price changes
                self.events_df.at[idx, 'Price_Before_30d'] = before_window['Price'].mean()
                self.events_df.at[idx, 'Price_After_30d'] = after_window['Price'].mean()
                self.events_df.at[idx, 'Price_Change_30d'] = (
                    self.events_df.at[idx, 'Price_After_30d'] - 
                    self.events_df.at[idx, 'Price_Before_30d']
                )
                self.events_df.at[idx, 'Pct_Change_30d'] = (
                    self.events_df.at[idx, 'Price_Change_30d'] / 
                    self.events_df.at[idx, 'Price_Before_30d'] * 100
                )
        
        print("✅ Events enriched with price data")
        return self.events_df
    
    def save_events(self, output_path: str) -> None:
        """
        Save events to CSV
        
        Args:
            output_path: Path to save events data
        """
        if self.events_df is None:
            self.compile_events()
        
        try:
            self.events_df.to_csv(output_path, index=False)
            print(f"✅ Events saved to {output_path}")
        except Exception as e:
            print(f"❌ Error saving events: {str(e)}")
            raise
    
    def get_events_by_type(self, event_type: str = None) -> pd.DataFrame:
        """
        Get events filtered by type
        
        Args:
            event_type: Type of events to filter (None for all)
            
        Returns:
            Filtered DataFrame
        """
        if self.events_df is None:
            self.compile_events()
        
        if event_type:
            filtered = self.events_df[self.events_df['Type'] == event_type]
            print(f"📊 Found {len(filtered)} events of type: {event_type}")
            return filtered
        else:
            return self.events_df
    
    def get_event_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics for events
        
        Returns:
            Dictionary with event summary
        """
        if self.events_df is None:
            self.compile_events()
        
        summary = {
            'total_events': len(self.events_df),
            'event_types': self.events_df['Type'].value_counts().to_dict(),
            'impact_levels': self.events_df['Impact_Expected'].value_counts().to_dict(),
            'regions': self.events_df['Region'].value_counts().to_dict(),
            'date_range': {
                'start': self.events_df['Date'].min().strftime('%Y-%m-%d'),
                'end': self.events_df['Date'].max().strftime('%Y-%m-%d')
            }
        }
        
        if 'Pct_Change_30d' in self.events_df.columns:
            summary['price_changes'] = {
                'max_increase': self.events_df['Pct_Change_30d'].max(),
                'max_decrease': self.events_df['Pct_Change_30d'].min(),
                'avg_change': self.events_df['Pct_Change_30d'].mean(),
                'positive_changes': (self.events_df['Pct_Change_30d'] > 0).sum(),
                'negative_changes': (self.events_df['Pct_Change_30d'] < 0).sum()
            }
        
        return summary

# Example usage
if __name__ == "__main__":
    event_manager = EventManager()
    events_df = event_manager.compile_events()
    
    # Print summary
    summary = event_manager.get_event_summary()
    print(f"\n📋 Event Summary:")
    print(f"   Total Events: {summary['total_events']}")
    print(f"   Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"   Event Types: {summary['event_types']}")