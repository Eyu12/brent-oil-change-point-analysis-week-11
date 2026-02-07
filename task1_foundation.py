"""
Task 1: Laying the Foundation for Analysis
Complete implementation of all Task 1 deliverables
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import textwrap

class Task1Foundation:
    """Generate all Task 1 deliverables"""
    
    def __init__(self):
        # Directories
        self.csv_dir = Path("data/event")
        self.txt_dir = Path("reports/task1_foundation")
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)
        
    def create_event_dataset(self):
        """Create structured event dataset (CSV file)"""
        events = [
            ('2014-06-01', 'OPEC Maintains Production Despite Price Drop', 
             'Supply Decision', 'OPEC decides to keep output at 30M bpd despite falling prices',
             'Global', 'High', 'Medium-term', 'OPEC Minutes'),
            
            ('2015-07-14', 'Iran Nuclear Deal Implementation', 'Geopolitical',
             'Joint Comprehensive Plan of Action takes effect, lifting Iranian oil sanctions',
             'Middle East', 'Medium', 'Long-term', 'UN Documents'),
            
            ('2016-11-30', 'OPEC+ Vienna Agreement', 'Supply Decision',
             'OPEC and non-OPEC agree to cut 1.8M bpd for 6 months',
             'Global', 'High', 'Medium-term', 'OPEC Press Release'),
            
            ('2018-05-08', 'US Withdraws from Iran Nuclear Deal', 'Geopolitical',
             'US reinstates sanctions on Iranian oil exports',
             'Middle East', 'Medium', 'Medium-term', 'White House Statement'),
            
            ('2020-03-06', 'OPEC+ Price War Begins', 'Supply Decision',
             'Saudi Arabia and Russia fail to agree on cuts, sparking price war',
             'Global', 'Very High', 'Short-term', 'OPEC+ Meeting Notes'),
            
            ('2020-03-23', 'Global COVID-19 Lockdowns Begin', 'Economic Shock',
             'Major economies impose lockdowns, crushing oil demand',
             'Global', 'Extreme', 'Short-term', 'WHO Reports'),
            
            ('2020-04-20', 'WTI Futures Go Negative', 'Market Anomaly',
             'May 2020 WTI contract expires at -$37.63 due to storage crisis',
             'North America', 'Extreme', 'Immediate', 'CME Data'),
            
            ('2021-03-23', 'Suez Canal Blockage', 'Supply Disruption',
             'Ever Given container ship blocks canal for 6 days',
             'Middle East', 'Medium', 'Very short-term', 'Shipping Reports'),
            
            ('2022-02-24', 'Russia Invades Ukraine', 'Geopolitical',
             'Full-scale invasion leads to sanctions and supply disruptions',
             'Europe', 'Very High', 'Long-term', 'UN Resolutions'),
            
            ('2022-10-05', 'OPEC+ Announces 2M bpd Cut', 'Supply Decision',
             'Largest cut since 2020 pandemic response',
             'Global', 'High', 'Medium-term', 'OPEC Announcement'),
            
            ('2023-04-02', 'OPEC+ Voluntary Production Cuts', 'Supply Decision',
             'Multiple members announce 1.6M bpd in voluntary cuts',
             'Global', 'Medium', 'Medium-term', 'OPEC+ Statement'),
            
            ('2023-10-07', 'Israel-Hamas Conflict Escalates', 'Geopolitical',
             'Major conflict raises Middle East supply concerns',
             'Middle East', 'Medium', 'Medium-term', 'News Reports'),
            
            ('2023-11-30', 'OPEC+ Extends Production Cuts', 'Supply Decision',
             'Existing cuts extended through Q1 2024',
             'Global', 'Low', 'Short-term', 'OPEC+ Meeting'),
            
            ('2024-01-12', 'US/UK Strikes on Houthi Targets', 'Geopolitical',
             'Military action in Red Sea affects shipping routes',
             'Middle East', 'Medium', 'Ongoing', 'Pentagon Briefing'),
            
            ('2024-03-03', 'OPEC+ Extends Voluntary Cuts', 'Supply Decision',
             'Cuts extended through Q2 2024',
             'Global', 'Low', 'Short-term', 'OPEC+ Announcement')
        ]
        
        columns = [
            'Event_Date', 'Event_Name', 'Event_Type', 'Description',
            'Region', 'Impact_Magnitude', 'Impact_Duration', 'Data_Source'
        ]
        
        df = pd.DataFrame(events, columns=columns)
        df['Event_Date'] = pd.to_datetime(df['Event_Date'])
        
        # Save to CSV in data/event/
        csv_path = self.csv_dir / 'brent_oil_market_events.csv'
        df.to_csv(csv_path, index=False)
        
        print(f"✅ Event dataset created: {csv_path}")
        return df
    
    def generate_analysis_plan(self):
        """Generate 1-2 page analysis plan document"""
        plan = textwrap.dedent("""\
        ====================================================================
        TASK 1: ANALYSIS PLAN FOR BRENT OIL PRICE ANALYSIS
        Generated: {date}
        ====================================================================

        1. DATA ANALYSIS WORKFLOW
        -------------------------
        
        1.1 Data Collection & Preparation (Weeks 1-2)
            Sources:
            - Brent crude prices: EIA API (2000-present, daily)
            - Event data: Manual compilation (15 key events)
            - Macro indicators: FRED, World Bank
            
            Processing:
            1. Price cleaning (handle holidays, outliers)
            2. Returns calculation (log returns for normality)
            3. Event-date alignment with trading calendar
            4. Feature engineering (rolling stats, volatility)
            
        1.2 Exploratory Analysis (Week 3)
            Diagnostics:
            - Stationarity: ADF, KPSS tests
            - Volatility: ARCH-LM test, rolling volatility
            - Distribution: Skewness, kurtosis, normality tests
            
            Visualizations:
            - Price timeline with event markers
            - Returns distribution vs normal
            - Autocorrelation plots (ACF, PACF)
            
        1.3 Change Point Detection (Weeks 4-5)
            Methods:
            1. Bayesian Change Point (probabilistic)
            2. PELT algorithm (optimal segmentation)
            3. CUSUM method (real-time detection)
            
            Validation:
            - Compare with known historical events
            - Bootstrap confidence intervals
            - Sensitivity analysis
            
        1.4 Event Impact Analysis (Weeks 6-7)
            Methodology:
            - Event windows: [-10, +10] trading days
            - Abnormal returns: Market model adjusted
            - Statistical tests: t-test, sign test, Wilcoxon
            
            Categorization:
            - By event type (supply, demand, geopolitical)
            - By impact magnitude (low, medium, high)
            - By duration (short, medium, long-term)
            
        1.5 Insight Generation (Week 8)
            Outputs:
            1. Structural break timeline
            2. Event impact ranking
            3. Volatility regime classification
            4. Risk assessment dashboard
            
        2. ASSUMPTIONS AND LIMITATIONS
        ------------------------------
        
        2.1 Key Assumptions
            Statistical:
            - Market efficiency (semi-strong form)
            - Returns stationarity (tested empirically)
            - Event exogeneity (debatable - noted)
            
            Modeling:
            - Linear additive effects (checked with interactions)
            - Parameter stability within regimes
            - Normally distributed errors (after transformations)
            
        2.2 Critical Limitations
            CORRELATION VS. CAUSATION:
            This is the most important limitation. We explicitly acknowledge that:
            - Statistical association does not prove causation
            - Events may coincide with price changes without causing them
            - Confounding variables may drive both events and prices
            
            Specific limitations:
            1. Confounding factors (multiple simultaneous events)
            2. Market anticipation effects (pre-event price movements)
            3. Data frequency (daily misses intraday dynamics)
            4. Model specification risk (algorithm choice affects results)
            5. Multiple testing (false discovery rate with many events)
            
        3. COMMUNICATION CHANNELS
        -------------------------
        
        Stakeholder Matrix:
        
        | Stakeholder        | Primary Channel      | Format                    | Frequency     |
        |--------------------|----------------------|---------------------------|---------------|
        | Executive Team     | Monthly Briefing     | PDF + Executive Summary   | Monthly       |
        | Trading Desk       | Real-time Dashboard  | Web Application           | Daily         |
        | Risk Management    | Alert System         | Email/SMS + Dashboard     | Event-driven  |
        | Research Team      | Technical Paper      | Jupyter Notebook          | Quarterly     |
        | External Clients   | Market Commentary    | 2-page Brief              | Bi-weekly     |
        | Media              | Press Release        | Standard Template         | Major Events  |
        
        4. UNDERSTANDING MODEL & DATA
        -----------------------------
        
        4.1 Time Series Properties
        
        Expected Characteristics:
        - Trend: Long-term upward with cyclical components
        - Stationarity: Non-stationary in levels, stationary in returns
        - Volatility: Clustering (high volatility follows high volatility)
        - Seasonality: Moderate (demand patterns)
        
        Analysis Approach:
        1. Trend Analysis: Hodrick-Prescott filter decomposition
        2. Stationarity Testing: ADF (unit root), KPSS (stationarity)
        3. Volatility Patterns: GARCH model diagnostics
        4. Structural Breaks: Multiple change point algorithms
        
        4.2 Change Point Models
        
        Purpose:
        - Identify structural breaks in data-generating process
        - Separate different market regimes
        - Validate against known historical events
        
        Expected Outputs:
        - Break dates with confidence intervals
        - Regime parameters (mean, volatility)
        - Probabilistic assessment
        
        Limitations to Disclose:
        - Model dependence (results vary by algorithm)
        - Multiple testing issues
        - Distinguishing temporary vs permanent breaks
        
        5. EXPECTED OUTPUTS
        -------------------
        
        From Change Point Analysis:
        - Dates of significant structural changes
        - Parameter estimates for each regime
        - Statistical confidence measures
        
        From Event Impact Analysis:
        - Abnormal returns around each event
        - Cumulative impact measures
        - Statistical significance tests
        ====================================================================
        NEXT STEPS: Begin Task 2 - Data Pipeline Implementation
        ====================================================================
        """).format(date=datetime.now().strftime('%Y-%m-%d'))
        
        plan_path = self.txt_dir / 'analysis_plan.txt'
        with open(plan_path, 'w') as f:
            f.write(plan)
        print(f"✅ Analysis plan created: {plan_path}")
        return plan
    
    def create_assumptions_document(self):
        """Detailed assumptions and limitations document"""
        assumptions = textwrap.dedent("""\
        ====================================================================
        DETAILED ASSUMPTIONS AND LIMITATIONS
        Brent Oil Price Analysis - Task 1
        ====================================================================
               CRITICAL DISCLAIMER: CORRELATION ≠ CAUSATION
        --------------------------------------------
        
        The most important limitation of this analysis is the distinction between
        statistical correlation and causal impact. We explicitly state that:
        
        1. TEMPORAL ASSOCIATION IS NOT CAUSAL PROOF
           - Events may precede price changes without causing them
           - Both events and price changes may be driven by third factors
           - Coincidence of timing does not establish causality
        
        2. EVIDENCE REQUIRED FOR CAUSAL INFERENCE (NOT PROVIDED HERE):
           - Controlled experiments (impossible in financial markets)
           - Strong theoretical mechanism explaining the relationship
           - Exclusion of alternative explanations
           - Consistent findings across multiple methodologies
        
        3. OUR ANALYSIS PROVIDES:
           - Statistical associations between events and price changes
           - Evidence-informed insights about potential impacts
           - Quantitative measures of temporal relationships
        
        Stakeholders MUST interpret results as:
          "Event X was associated with price change Y"
        NOT as:
          "Event X caused price change Y"
        
        DETAILED ASSUMPTIONS
        --------------------
        
        A. MARKET STRUCTURE ASSUMPTIONS
          1. Semi-strong form market efficiency
          2. No arbitrage opportunities persist
          3. Market participants act rationally on available information
          4. Liquidity is sufficient for price discovery
        
        B. STATISTICAL ASSUMPTIONS
          1. Returns are stationary (tested via ADF/KPSS)
          2. Error terms are normally distributed (after transformations)
          3. Observations are independent (checked via autocorrelation)
          4. Homoscedasticity within regimes (volatility tests)
        
        C. MODELING ASSUMPTIONS
          1. Linear relationships (checked with residual plots)
          2. Parameter stability within detected regimes
          3. Additive effects of events (interaction terms tested)
          4. Correct model specification (multiple specifications tested)
        
        D. DATA ASSUMPTIONS
          1. Price data is accurate and consistent
          2. Event dates reflect market awareness timing
          3. No systematic missing data patterns
          4. Historical patterns are informative about future
        
        DETAILED LIMITATIONS
        --------------------
        
        1. CONFOUNDING VARIABLES
           - Multiple events often occur simultaneously
           - Macroeconomic factors (interest rates, GDP) not fully controlled
           - Weather patterns, inventory levels not included
        
        2. MEASUREMENT ISSUES
           - Event impact duration estimates are subjective
           - Event classification may be ambiguous
           - Price data frequency (daily) misses intraday dynamics
        
        3. MODEL SPECIFICATION
           - Change point detection results depend on algorithm choice
           - Window sizes for event studies affect results
           - Parameter choices (thresholds, penalties) are subjective
        
        4. TEMPORAL ISSUES
           - Market anticipation: Prices may move before official event dates
           - Delayed impacts: Some events have lagged effects
           - Persistence: Difficult to distinguish temporary vs permanent shocks
        
        5. EXTERNAL VALIDITY
           - Historical period may not represent future market structure
           - Structural changes (shale revolution) affect relationships
           - Geopolitical relationships evolve over time
        
        MITIGATION STRATEGIES
        ---------------------
        
        1. Robustness Checks:
           - Multiple change point algorithms
           - Different event window specifications
           - Alternative model specifications
        
        2. Transparency:
           - Full disclosure of all assumptions
           - Clear labeling of statistical vs causal claims
           - Documentation of all methodological choices
        
        3. Validation:
           - Out-of-sample testing where possible
           - Expert validation with domain specialists
           - Comparison with alternative data sources
        
        ====================================================================
        This document should accompany all analysis outputs to ensure
        proper interpretation of results.
        ====================================================================
        """)
        
        assumptions_path = self.txt_dir / 'assumptions_limitations.txt'
        with open(assumptions_path, 'w') as f:
            f.write(assumptions)
        print(f"✅ Assumptions document created: {assumptions_path}")
        return assumptions
    
    def create_summary_report(self):
        """Create executive summary of Task 1 deliverables"""
        summary = f"""\
        TASK 1 COMPLETION REPORT
        ========================
        Project: Brent Oil Price Analysis
        Task: 1 - Laying the Foundation
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Deliverables completed and saved to folders.
        """
        
        summary_path = self.txt_dir / 'task1_summary.txt'
        with open(summary_path, 'w') as f:
            f.write(summary)
        print(f"✅ Summary report created: {summary_path}")
        return summary
    
    def run_complete_task1(self):
        """Execute all Task 1 deliverables"""
        print("="*60)
        events_df = self.create_event_dataset()
        plan = self.generate_analysis_plan()
        assumptions = self.create_assumptions_document()
        summary = self.create_summary_report()
        print("="*60)
        print(f"\n✅ Task 1 complete!")
        print(f"📁 CSV saved in: {self.csv_dir}")
        print(f"📁 TXT files saved in: {self.txt_dir}")
        print("="*60)
        

def main():
    task1 = Task1Foundation()
    task1.run_complete_task1()


if __name__ == "__main__":
    main()
