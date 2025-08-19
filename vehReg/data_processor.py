# data_processor.py
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
    def calculate_yoy_growth(self):
        """Calculate Year-over-Year growth"""
        yoy_data = []
        
        for category in self.df['category'].unique():
            for manufacturer in self.df[self.df['category'] == category]['manufacturer'].unique():
                subset = self.df[(self.df['category'] == category) & 
                               (self.df['manufacturer'] == manufacturer)]
                
                yearly_data = subset.groupby('year')['registrations'].sum().reset_index()
                
                for i in range(1, len(yearly_data)):
                    prev_year = yearly_data.iloc[i-1]['registrations']
                    curr_year = yearly_data.iloc[i]['registrations']
                    growth = ((curr_year - prev_year) / prev_year) * 100 if prev_year > 0 else 0
                    
                    yoy_data.append({
                        'category': category,
                        'manufacturer': manufacturer,
                        'year': yearly_data.iloc[i]['year'],
                        'yoy_growth': growth,
                        'current_registrations': curr_year,
                        'previous_registrations': prev_year
                    })
        
        return pd.DataFrame(yoy_data)
    
    def calculate_qoq_growth(self):
        """Calculate Quarter-over-Quarter growth"""
        qoq_data = []
        
        for category in self.df['category'].unique():
            for manufacturer in self.df[self.df['category'] == category]['manufacturer'].unique():
                subset = self.df[(self.df['category'] == category) & 
                               (self.df['manufacturer'] == manufacturer)]
                
                quarterly_data = subset.groupby(['year', 'quarter'])['registrations'].sum().reset_index()
                quarterly_data['period'] = quarterly_data['year'].astype(str) + '-' + quarterly_data['quarter']
                quarterly_data = quarterly_data.sort_values(['year', 'quarter'])
                
                for i in range(1, len(quarterly_data)):
                    prev_quarter = quarterly_data.iloc[i-1]['registrations']
                    curr_quarter = quarterly_data.iloc[i]['registrations']
                    growth = ((curr_quarter - prev_quarter) / prev_quarter) * 100 if prev_quarter > 0 else 0
                    
                    qoq_data.append({
                        'category': category,
                        'manufacturer': manufacturer,
                        'year': quarterly_data.iloc[i]['year'],
                        'quarter': quarterly_data.iloc[i]['quarter'],
                        'period': quarterly_data.iloc[i]['period'],
                        'qoq_growth': growth,
                        'current_registrations': curr_quarter,
                        'previous_registrations': prev_quarter
                    })
        
        return pd.DataFrame(qoq_data)
    
    def get_category_summary(self):
        """Get summary by vehicle category"""
        return self.df.groupby(['category', 'year']).agg({
            'registrations': ['sum', 'count']
        }).reset_index()