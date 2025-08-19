# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import DataProcessor
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Dashboard",
    page_icon="🚗",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load and process data"""
    try:
        processor = DataProcessor('vehicle_registration_data.csv')
        df = processor.df
        yoy_data = processor.calculate_yoy_growth()
        qoq_data = processor.calculate_qoq_growth()
        return df, yoy_data, qoq_data
    except FileNotFoundError:
        st.error("Data file not found. Please run the data collection script first.")
        return None, None, None

def create_trend_chart(df, metric='registrations'):
    """Create trend charts"""
    fig = px.line(df.groupby(['date', 'category'])[metric].sum().reset_index(),
                  x='date', y=metric, color='category',
                  title=f'{metric.title()} Trend by Vehicle Category')
    fig.update_layout(height=400)
    return fig

def create_growth_chart(growth_data, growth_type='YoY'):
    """Create growth charts"""
    fig = px.bar(growth_data.groupby(['category', 'year' if growth_type == 'YoY' else 'period'])
                 [f'{growth_type.lower()}_growth'].mean().reset_index(),
                 x='year' if growth_type == 'YoY' else 'period', 
                 y=f'{growth_type.lower()}_growth',
                 color='category',
                 title=f'{growth_type} Growth Rate by Category')
    fig.update_layout(height=400, yaxis_title=f'{growth_type} Growth (%)')
    return fig

def create_manufacturer_chart(df, category_filter):
    """Create manufacturer-wise charts"""
    filtered_df = df[df['category'].isin(category_filter)]
    manufacturer_data = filtered_df.groupby(['manufacturer', 'year'])['registrations'].sum().reset_index()
    
    fig = px.line(manufacturer_data, x='year', y='registrations', color='manufacturer',
                  title='Manufacturer-wise Registration Trends')
    fig.update_layout(height=400)
    return fig

def main():
    # Title and header
    st.title("🚗 Vehicle Registration Dashboard")
    st.markdown("### Investor-focused Analytics on Indian Vehicle Registration Data")
    
    # Load data
    df, yoy_data, qoq_data = load_data()
    
    if df is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # Date range selection
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Select Vehicle Categories",
        options=df['category'].unique(),
        default=df['category'].unique()
    )
    
    # Manufacturer filter
    manufacturers = st.sidebar.multiselect(
        "Select Manufacturers",
        options=df['manufacturer'].unique(),
        default=df['manufacturer'].unique()[:10]  # Limit to first 10 for performance
    )
    
    # Filter data based on selection
    if len(date_range) == 2:
        filtered_df = df[
            (df['date'] >= pd.to_datetime(date_range[0])) &
            (df['date'] <= pd.to_datetime(date_range[1])) &
            (df['category'].isin(categories)) &
            (df['manufacturer'].isin(manufacturers))
        ]
    else:
        filtered_df = df[
            (df['category'].isin(categories)) &
            (df['manufacturer'].isin(manufacturers))
        ]
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registrations = filtered_df['registrations'].sum()
        st.metric("Total Registrations", f"{total_registrations:,}")
    
    with col2:
        avg_yoy_growth = yoy_data[yoy_data['category'].isin(categories)]['yoy_growth'].mean()
        st.metric("Avg YoY Growth", f"{avg_yoy_growth:.1f}%")
    
    with col3:
        avg_qoq_growth = qoq_data[qoq_data['category'].isin(categories)]['qoq_growth'].mean()
        st.metric("Avg QoQ Growth", f"{avg_qoq_growth:.1f}%")
    
    with col4:
        top_category = filtered_df.groupby('category')['registrations'].sum().idxmax()
        st.metric("Top Category", top_category)
    
    # Main charts
    st.header("📈 Registration Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_chart = create_trend_chart(filtered_df)
        st.plotly_chart(trend_chart, use_container_width=True)
    
    with col2:
        yoy_chart = create_growth_chart(yoy_data[yoy_data['category'].isin(categories)], 'YoY')
        st.plotly_chart(yoy_chart, use_container_width=True)
    
    # Manufacturer analysis
    st.header("🏭 Manufacturer Analysis")
    manufacturer_chart = create_manufacturer_chart(filtered_df, categories)
    st.plotly_chart(manufacturer_chart, use_container_width=True)
    
    # Growth comparison
    st.header("📊 Growth Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performers (YoY Growth)")
        top_yoy = yoy_data[yoy_data['category'].isin(categories)].nlargest(10, 'yoy_growth')
        st.dataframe(top_yoy[['manufacturer', 'category', 'year', 'yoy_growth']].round(2))
    
    with col2:
        st.subheader("Market Share by Category")
        market_share = filtered_df.groupby('category')['registrations'].sum()
        fig_pie = px.pie(values=market_share.values, names=market_share.index, 
                        title="Market Share by Vehicle Category")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Investment Insights
    st.header("💡 Investment Insights")
    
    insights = [
        "🚗 **4-Wheeler segment** shows consistent growth with premium manufacturers leading",
        "🏍️ **2-Wheeler market** dominates volume but faces saturation in urban areas",
        "🛺 **3-Wheeler segment** shows high volatility but significant opportunity in logistics",
        "📈 **Electric vehicle adoption** is accelerating across all categories",
        "🏭 **Market consolidation** trend visible with top 5 manufacturers gaining share"
    ]
    
    for insight in insights:
        st.markdown(insight)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()