"""
Verify Task 1 deliverables meet requirements
"""

import pandas as pd
from pathlib import Path

def verify_task1():
    """Verify all Task 1 deliverables"""
    
    print("VERIFYING TASK 1 DELIVERABLES")
    print("="*60)
    
    # Correct directories
    csv_dir = Path("data/event")
    txt_dir = Path("reports/task1_foundation")
    
    # 1. Verify event dataset
    event_file = csv_dir / "brent_oil_market_events.csv"
    if event_file.exists():
        df = pd.read_csv(event_file, parse_dates=['Event_Date'])
        print(f"\n✅ Event dataset: {len(df)} events")
        print(f"   Date range: {df['Event_Date'].min().date()} to {df['Event_Date'].max().date()}")
        print(f"   Event types: {df['Event_Type'].nunique()} types")
        
        if len(df) >= 10:
            print("   ✓ Meets requirement: ≥10 events")
        else:
            print(f"   ✗ Below requirement: {len(df)} < 10 events")
    else:
        print("\n❌ Event dataset file not found")
    
    # 2. Verify analysis plan
    plan_file = txt_dir / "analysis_plan.txt"
    if plan_file.exists():
        with open(plan_file, 'r') as f:
            content = f.read()
            word_count = len(content.split())
            print(f"\n✅ Analysis plan: {word_count} words")
            
            # Check key sections
            sections = ["WORKFLOW", "ASSUMPTIONS", "LIMITATIONS", "COMMUNICATION"]
            found_sections = [section for section in sections if section in content.upper()]
            
            print(f"   Contains sections: {', '.join(found_sections)}")
            if len(found_sections) >= 3:
                print("   ✓ Meets requirement: Key sections present")
            else:
                print(f"   ✗ Missing sections: Need at least 3, found {len(found_sections)}")
    else:
        print("\n❌ Analysis plan file not found")
    
    # 3. Verify assumptions document
    assumptions_file = txt_dir / "assumptions_limitations.txt"
    if assumptions_file.exists():
        with open(assumptions_file, 'r') as f:
            content = f.read()
            if "CORRELATION" in content.upper() and "CAUSATION" in content.upper():
                print("\n✅ Assumptions document includes correlation/causation discussion")
                print("   ✓ Meets critical requirement")
            else:
                print("\n❌ Assumptions document missing correlation/causation discussion")
    else:
        print("\n❌ Assumptions document not found")
    
    # 4. Verify communication channels are documented
    if plan_file.exists():
        with open(plan_file, 'r') as f:
            content = f.read().upper()
            if "COMMUNICATION" in content or "STAKEHOLDER" in content:
                print("\n✅ Communication channels documented")
                print("   ✓ Meets requirement")
            else:
                print("\n❌ Communication channels not documented")
    
    # 5. Verify time series properties discussion
    if plan_file.exists():
        with open(plan_file, 'r') as f:
            content = f.read().upper()
            ts_terms = ["STATIONARITY", "TREND", "VOLATILITY", "CHANGE POINT"]
            found_terms = [term for term in ts_terms if term in content]
            if len(found_terms) >= 2:
                print(f"\n✅ Time series properties discussed: {', '.join(found_terms)}")
                print("   ✓ Meets requirement")
            else:
                print(f"\n❌ Insufficient time series properties discussion")
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    
    return True

if __name__ == "__main__":
    verify_task1()
