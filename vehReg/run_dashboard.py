# run_dashboard.py
"""
Main script to run the vehicle registration dashboard
"""
import os
import subprocess
from data_collector import VahanDataCollector

def setup_and_run():
    """Setup data and run dashboard"""
    print("🚗 Setting up Vehicle Registration Dashboard...")
    
    # Check if data file exists, if not create it
    if not os.path.exists('vehicle_registration_data.csv'):
        print("📊 Generating sample data...")
        collector = VahanDataCollector()
        df = collector.get_vehicle_data()
        df.to_csv('vehicle_registration_data.csv', index=False)
        print("✅ Sample data generated successfully!")
    
    print("🚀 Starting Streamlit dashboard...")
    subprocess.run(["streamlit", "run", "dashboard.py"])

if __name__ == "__main__":
    setup_and_run()