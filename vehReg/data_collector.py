# data_collector.py
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

class VahanDataCollector:
    def __init__(self):
        self.base_url = "https://vahan.parivahan.gov.in/vahan4dashboard"
        self.session = requests.Session()
        
    def get_vehicle_data(self, state_code="DL", start_date="2020-04-01", end_date="2024-03-31"):
        """
        Collect vehicle registration data from Vahan Dashboard
        Note: This is a simplified version - actual implementation may require handling CAPTCHA
        """
        # Sample data structure - in real implementation, you'd scrape from the actual API
        sample_data = self._generate_sample_data()
        return sample_data
    
    def _generate_sample_data(self):
        """
        Generate realistic sample data based on Vahan Dashboard structure
        """
        import random
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Vehicle categories
        categories = ['2W', '3W', '4W']
        manufacturers = {
            '2W': ['Hero MotoCorp', 'Honda', 'TVS', 'Bajaj', 'Yamaha'],
            '3W': ['Bajaj', 'TVS', 'Mahindra', 'Piaggio'],
            '4W': ['Maruti Suzuki', 'Hyundai', 'Tata', 'Mahindra', 'Toyota']
        }
        
        data = []
        start_date = datetime(2020, 4, 1)
        end_date = datetime(2024, 3, 31)
        
        current_date = start_date
        while current_date <= end_date:
            for category in categories:
                for manufacturer in manufacturers[category]:
                    # Generate realistic registration numbers with growth trends
                    base_registrations = {
                        '2W': random.randint(5000, 15000),
                        '3W': random.randint(500, 2000),
                        '4W': random.randint(2000, 8000)
                    }
                    
                    # Add some seasonal and growth trends
                    month_factor = 1 + 0.1 * (current_date.month % 4)  # Seasonal variation
                    year_factor = 1 + 0.05 * (current_date.year - 2020)  # YoY growth
                    
                    registrations = int(base_registrations[category] * month_factor * year_factor * random.uniform(0.8, 1.2))
                    
                    data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'category': category,
                        'manufacturer': manufacturer,
                        'registrations': registrations,
                        'year': current_date.year,
                        'quarter': f"Q{((current_date.month - 1) // 3) + 1}",
                        'month': current_date.month
                    })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return pd.DataFrame(data)

# Usage
collector = VahanDataCollector()
df = collector.get_vehicle_data()
df.to_csv('vehicle_registration_data.csv', index=False)