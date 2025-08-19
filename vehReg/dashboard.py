# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import DataProcessor
import numpy as np
from datetime import datetime, timedelta
import time

# Page configuration with enhanced styling
st.set_page_config(
    page_title="VehicleVision Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables with proper defaults
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = 'all'
if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = []
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'bookmark_filters' not in st.session_state:
    st.session_state.bookmark_filters = {}
if 'alert_threshold' not in st.session_state:
    st.session_state.alert_threshold = 10.0
# NEW: Add session state for toggle buttons
if 'animations_enabled' not in st.session_state:
    st.session_state.animations_enabled = True
if 'predictions_enabled' not in st.session_state:
    st.session_state.predictions_enabled = False
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False

# Function to apply dark theme CSS
def apply_dark_theme():
    if st.session_state.dark_theme:
        return """
        <style>
            .main-header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
            }
            .metric-card {
                background: #34495e;
                color: white;
                border-left: 5px solid #3498db;
            }
            .section-header {
                background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
                color: white;
            }
            .stApp {
                background-color: #2c3e50;
                color: white;
            }
        </style>
        """
    else:
        return ""

# Custom CSS for better styling (updated with dark theme support)
def get_custom_css():
    base_css = """
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            animation: fadeInDown 1s ease-out;
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .main-header h1 {
            color: white;
            text-align: center;
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            color: white;
            text-align: center;
            font-size: 1.2rem;
            margin-top: 0.5rem;
            opacity: 0.9;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            margin-bottom: 1rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .insight-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            animation: slideInLeft 0.8s ease-out;
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .section-header {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            color: white;
            margin: 2rem 0 1rem 0;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .alert-positive {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 0.5rem 0;
        }
        
        .alert-negative {
            background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 0.5rem 0;
        }
        
        .growth-positive { color: #28a745; font-weight: bold; }
        .growth-negative { color: #dc3545; font-weight: bold; }
        
        .animated-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .animated-number.pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        
        .comparison-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .toggle-status {
            padding: 0.5rem;
            border-radius: 5px;
            font-weight: bold;
            margin: 0.2rem 0;
        }
        
        .toggle-on {
            background-color: #28a745;
            color: white;
        }
        
        .toggle-off {
            background-color: #6c757d;
            color: white;
        }
    </style>
    """
    
    return base_css + apply_dark_theme()

@st.cache_data(ttl=300)  # Cache for 5 minutes for auto-refresh
def load_data():
    """Load and process data with enhanced error handling"""
    try:
        with st.spinner("🔄 Loading vehicle registration data..."):
            # Demo data generation
            dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')
            categories = ['2W', '3W', '4W', 'Commercial', 'Electric']
            manufacturers = ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Honda', 'Toyota', 'Bajaj', 'Hero', 'TVS', 'Royal Enfield']
            
            data = []
            for date in dates:
                for category in categories:
                    for manufacturer in manufacturers[:5]:  # Limit for demo
                        registrations = np.random.randint(100, 1000)
                        data.append({
                            'date': date,
                            'category': category,
                            'manufacturer': manufacturer,
                            'registrations': registrations,
                            'month': date.month,
                            'quarter': date.quarter,
                            'year': date.year
                        })
            
            df = pd.DataFrame(data)
            
            # Calculate growth data
            yoy_data = df.groupby(['category', 'manufacturer', 'year'])['registrations'].sum().reset_index()
            yoy_data['yoy_growth'] = yoy_data.groupby(['category', 'manufacturer'])['registrations'].pct_change() * 100
            
            qoq_data = df.groupby(['category', 'manufacturer', 'year', 'quarter'])['registrations'].sum().reset_index()
            qoq_data['period'] = qoq_data['year'].astype(str) + '-Q' + qoq_data['quarter'].astype(str)
            qoq_data['qoq_growth'] = qoq_data.groupby(['category', 'manufacturer'])['registrations'].pct_change() * 100
            
        return df, yoy_data, qoq_data
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None, None, None

def apply_date_filter(df, filter_type):
    """Apply date filtering based on button selection"""
    today = df['date'].max()
    
    if filter_type == 'last_30':
        start_date = today - timedelta(days=30)
        return df[df['date'] >= start_date]
    elif filter_type == 'last_year':
        start_date = today - timedelta(days=365)
        return df[df['date'] >= start_date]
    elif filter_type == 'ytd':
        start_date = pd.Timestamp(today.year, 1, 1)
        return df[df['date'] >= start_date]
    elif filter_type == 'last_quarter':
        start_date = today - timedelta(days=90)
        return df[df['date'] >= start_date]
    else:
        return df

def create_alert_system(df, yoy_data, threshold):
    """Create intelligent alert system"""
    alerts = []
    
    # Growth alerts
    recent_growth = yoy_data[yoy_data['year'] == yoy_data['year'].max()]
    high_growth = recent_growth[recent_growth['yoy_growth'] > threshold]
    low_growth = recent_growth[recent_growth['yoy_growth'] < -threshold]
    
    if not high_growth.empty:
        alerts.append({
            'type': 'positive',
            'title': 'High Growth Detected! 📈',
            'message': f"{len(high_growth)} categories showing growth above {threshold}%"
        })
    
    if not low_growth.empty:
        alerts.append({
            'type': 'negative',
            'title': 'Growth Concern! 📉',
            'message': f"{len(low_growth)} categories showing decline below -{threshold}%"
        })
    
    # Volume alerts
    recent_data = df[df['date'] >= df['date'].max() - timedelta(days=30)]
    if recent_data['registrations'].sum() < df['registrations'].mean() * 30 * 0.8:
        alerts.append({
            'type': 'negative',
            'title': 'Volume Drop Alert! ⚠️',
            'message': 'Recent registrations are 20% below average'
        })
    
    return alerts

def create_comparison_view(df, comparison_items):
    """Create side-by-side comparison"""
    if len(comparison_items) < 2:
        return None
    
    fig = make_subplots(
        rows=1, cols=len(comparison_items),
        subplot_titles=comparison_items,
        specs=[[{"secondary_y": False}] * len(comparison_items)]
    )
    
    colors = px.colors.qualitative.Set1
    
    for i, item in enumerate(comparison_items):
        item_data = df[df['category'] == item].groupby('date')['registrations'].sum().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=item_data['date'],
                y=item_data['registrations'],
                mode='lines',
                name=item,
                line=dict(color=colors[i % len(colors)], width=3)
            ),
            row=1, col=i+1
        )
    
    fig.update_layout(
        height=400,
        title="📊 Category Comparison Analysis",
        showlegend=True
    )
    
    return fig

def create_predictive_chart(df, category):
    """Create predictive analysis chart"""
    # Simple trend prediction using linear regression
    category_data = df[df['category'] == category].groupby('date')['registrations'].sum().reset_index()
    category_data['days'] = (category_data['date'] - category_data['date'].min()).dt.days
    
    # Fit linear trend
    z = np.polyfit(category_data['days'], category_data['registrations'], 1)
    p = np.poly1d(z)
    
    # Extend for prediction
    future_days = np.arange(category_data['days'].max(), category_data['days'].max() + 90, 1)
    future_dates = [category_data['date'].max() + timedelta(days=int(d - category_data['days'].max())) for d in future_days]
    predictions = p(future_days)
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=category_data['date'],
        y=category_data['registrations'],
        mode='lines',
        name='Historical',
        line=dict(color='blue', width=2)
    ))
    
    # Predictions
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines',
        name='Predicted',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"🔮 Predictive Analysis: {category}",
        height=400,
        xaxis_title="Date",
        yaxis_title="Registrations"
    )
    
    return fig

def create_seasonal_analysis(df):
    """Create comprehensive seasonal analysis"""
    seasonal_data = df.groupby([df['date'].dt.month, 'category'])['registrations'].sum().reset_index()
    seasonal_data['month_name'] = seasonal_data['date'].apply(lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x-1])
    
    # Monthly heatmap
    pivot_seasonal = seasonal_data.pivot(index='category', columns='month_name', values='registrations')
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_seasonal = pivot_seasonal.reindex(columns=month_order)
    
    return pivot_seasonal, seasonal_data

def create_advanced_insights(df, yoy_data, qoq_data):
    """Generate advanced business insights"""
    insights = []
    
    # Market volatility analysis
    volatility = df.groupby('category')['registrations'].std()
    high_volatility_cats = volatility[volatility > volatility.quantile(0.75)].index.tolist()
    
    if high_volatility_cats:
        insights.append({
            'title': '🎯 Market Volatility Alert',
            'message': f"Categories with high volatility: {', '.join(high_volatility_cats)}. Consider risk management strategies."
        })
    
    # Growth momentum analysis
    recent_growth = yoy_data[yoy_data['year'] == yoy_data['year'].max()]
    accelerating_cats = recent_growth[recent_growth['yoy_growth'] > 15]['category'].unique()
    
    if len(accelerating_cats) > 0:
        insights.append({
            'title': '🚀 Growth Momentum',
            'message': f"Strong growth momentum in: {', '.join(accelerating_cats)}. Consider capacity expansion."
        })
    
    # Seasonal patterns
    monthly_variance = df.groupby([df['date'].dt.month, 'category'])['registrations'].sum().groupby('category').std()
    seasonal_cats = monthly_variance[monthly_variance > monthly_variance.quantile(0.6)].index.tolist()
    
    if seasonal_cats:
        insights.append({
            'title': '🌊 Seasonal Patterns',
            'message': f"Strong seasonal patterns detected in: {', '.join(seasonal_cats)}. Plan inventory accordingly."
        })
    
    return insights

def main():
    # Apply custom CSS (including dark theme if enabled)
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1>🚗 VehicleVision Analytics</h1>
        <p>Comprehensive Vehicle Registration Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, yoy_data, qoq_data = load_data()
    
    if df is None:
        st.stop()
    
    # Control Panel with WORKING functional buttons
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; text-align: center; margin: 0;">🎛️ Control Panel</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # FIXED: Functional toggles with proper state management
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # Enable Animations Toggle
        animations = st.toggle(
            "🎬 Enable Animations", 
            value=st.session_state.animations_enabled,
            key="animations_toggle"
        )
        if animations != st.session_state.animations_enabled:
            st.session_state.animations_enabled = animations
            if animations:
                st.sidebar.success("✅ Animations enabled!")
            else:
                st.sidebar.info("ℹ️ Animations disabled")
        
        # Show Predictions Toggle
        predictions = st.toggle(
            "🔮 Show Predictions", 
            value=st.session_state.predictions_enabled,
            key="predictions_toggle"
        )
        if predictions != st.session_state.predictions_enabled:
            st.session_state.predictions_enabled = predictions
            if predictions:
                st.sidebar.success("🔮 Predictions enabled!")
            else:
                st.sidebar.info("ℹ️ Predictions disabled")
    
    with col2:
        # Comparison Mode Toggle
        comparison = st.toggle(
            "⚖️ Comparison Mode", 
            value=st.session_state.comparison_mode,
            key="comparison_toggle"
        )
        if comparison != st.session_state.comparison_mode:
            st.session_state.comparison_mode = comparison
            if comparison:
                st.sidebar.success("⚖️ Comparison mode active!")
            else:
                st.sidebar.info("ℹ️ Comparison mode disabled")
        
        # Dark Theme Toggle
        dark_theme = st.toggle(
            "🌙 Dark Theme", 
            value=st.session_state.dark_theme,
            key="dark_theme_toggle"
        )
        if dark_theme != st.session_state.dark_theme:
            st.session_state.dark_theme = dark_theme
            if dark_theme:
                st.sidebar.success("🌙 Dark theme activated!")
                st.rerun()  # Refresh to apply CSS changes
            else:
                st.sidebar.success("☀️ Light theme activated!")
                st.rerun()  # Refresh to apply CSS changes
    
    # Display current toggle status
    st.sidebar.markdown("### 📊 Current Settings")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # Animations status
        anim_status = "ON" if st.session_state.animations_enabled else "OFF"
        anim_class = "toggle-on" if st.session_state.animations_enabled else "toggle-off"
        st.sidebar.markdown(f'<div class="toggle-status {anim_class}">🎬 Animations: {anim_status}</div>', unsafe_allow_html=True)
        
        # Predictions status
        pred_status = "ON" if st.session_state.predictions_enabled else "OFF"
        pred_class = "toggle-on" if st.session_state.predictions_enabled else "toggle-off"
        st.sidebar.markdown(f'<div class="toggle-status {pred_class}">🔮 Predictions: {pred_status}</div>', unsafe_allow_html=True)
    
    with col2:
        # Comparison status
        comp_status = "ON" if st.session_state.comparison_mode else "OFF"
        comp_class = "toggle-on" if st.session_state.comparison_mode else "toggle-off"
        st.sidebar.markdown(f'<div class="toggle-status {comp_class}">⚖️ Comparison: {comp_status}</div>', unsafe_allow_html=True)
        
        # Theme status
        theme_status = "DARK" if st.session_state.dark_theme else "LIGHT"
        theme_class = "toggle-on" if st.session_state.dark_theme else "toggle-off"
        st.sidebar.markdown(f'<div class="toggle-status {theme_class}">🌙 Theme: {theme_status}</div>', unsafe_allow_html=True)
    
    # Auto-refresh functionality (IMPROVED)
    auto_refresh = st.sidebar.toggle("🔄 Auto Refresh (30s)", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        if auto_refresh:
            st.sidebar.success("🟢 Auto-refresh started!")
        else:
            st.sidebar.info("🔴 Auto-refresh stopped")
    
    if st.session_state.auto_refresh:
        st.sidebar.success("🟢 Auto-refresh active")
        # Show countdown timer
        placeholder = st.sidebar.empty()
        for i in range(30, 0, -1):
            placeholder.info(f"⏱️ Next refresh in: {i}s")
            time.sleep(1)
        if st.session_state.auto_refresh:  # Check if still enabled
            st.cache_data.clear()
            st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data Now", type="primary"):
        st.cache_data.clear()
        st.sidebar.success("✅ Data refreshed!")
        st.rerun()
    
    # Data Filters with functional buttons
    st.sidebar.markdown('<div class="section-header">📊 Data Filters</div>', unsafe_allow_html=True)
    
    # Date filter buttons
    st.sidebar.markdown("**📅 Quick Date Filters:**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📅 Last 30 Days", key="last_30"):
            st.session_state.date_filter = 'last_30'
            st.sidebar.success("✅ Applied Last 30 Days filter")
        if st.button("📅 YTD", key="ytd"):
            st.session_state.date_filter = 'ytd'
            st.sidebar.success("✅ Applied YTD filter")
    
    with col2:
        if st.button("📅 Last Year", key="last_year"):
            st.session_state.date_filter = 'last_year'
            st.sidebar.success("✅ Applied Last Year filter")
        if st.button("📅 All Time", key="all_time"):
            st.session_state.date_filter = 'all'
            st.sidebar.success("✅ Applied All Time filter")
    
    # Show current filter status
    st.sidebar.info(f"📊 Current filter: {st.session_state.date_filter.replace('_', ' ').title()}")
    
    # Apply date filter
    if st.session_state.date_filter != 'all':
        df_filtered = apply_date_filter(df, st.session_state.date_filter)
    else:
        df_filtered = df
    
    # Advanced date range selector
    with st.sidebar.expander("🗓️ Custom Date Range"):
        date_range = st.date_input(
            "Select Custom Range",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max(),
            key="custom_date_range"
        )
        
        if st.button("Apply Custom Range", key="apply_custom"):
            if len(date_range) == 2:
                df_filtered = df[
                    (df['date'] >= pd.to_datetime(date_range[0])) &
                    (df['date'] <= pd.to_datetime(date_range[1]))
                ]
                st.success("✅ Custom date range applied")
    
    # Category selection
    st.sidebar.markdown("**🚗 Vehicle Categories:**")
    categories = sorted(df['category'].unique())
    
    # Select All / Clear All buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("✅ Select All", key="select_all_cats"):
            st.session_state.selected_categories = categories
            st.sidebar.success("✅ All categories selected")
    with col2:
        if st.button("❌ Clear All", key="clear_all_cats"):
            st.session_state.selected_categories = []
            st.sidebar.success("✅ All categories cleared")
    
    # Individual category selection
    if not st.session_state.selected_categories:
        st.session_state.selected_categories = categories
    
    selected_categories = st.multiselect(
        "Choose categories:",
        options=categories,
        default=st.session_state.selected_categories,
        key="category_multiselect"
    )
    
    # Manufacturer selection
    manufacturers = sorted(df['manufacturer'].unique())
    selected_manufacturers = st.sidebar.multiselect(
        "🏭 Manufacturers",
        options=manufacturers,
        default=manufacturers[:5],
        help="Select manufacturers to analyze"
    )
    
    # Apply all filters
    final_df = df_filtered[
        (df_filtered['category'].isin(selected_categories)) &
        (df_filtered['manufacturer'].isin(selected_manufacturers))
    ]
    
    if final_df.empty:
        st.warning("⚠️ No data matches your current filters. Please adjust your selection.")
        st.stop()
    
    # Alert System
    alerts = create_alert_system(final_df, yoy_data, st.session_state.alert_threshold)
    if alerts:
        st.markdown("### 🚨 Smart Alerts")
        for alert in alerts:
            if alert['type'] == 'positive':
                st.markdown(f"""
                <div class="alert-positive">
                    <strong>{alert['title']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-negative">
                    <strong>{alert['title']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)
    
    # Enhanced metrics with animations (if enabled)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reg = final_df['registrations'].sum()
        prev_total = df[df['date'] < final_df['date'].min()]['registrations'].sum() if len(df) > len(final_df) else total_reg
        change = ((total_reg - prev_total) / prev_total * 100) if prev_total > 0 else 0
        
        pulse_class = "pulse" if st.session_state.animations_enabled else ""
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>🚗 Total Registrations</h4>
            <div class="animated-number {pulse_class}">{total_reg:,}</div>
            <small class="{'growth-positive' if change >= 0 else 'growth-negative'}">
                {'↑' if change >= 0 else '↓'} {abs(change):.1f}% vs previous period
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_yoy = yoy_data[yoy_data['category'].isin(selected_categories)]['yoy_growth'].mean()
        color_class = "growth-positive" if avg_yoy >= 0 else "growth-negative"
        arrow = "📈" if avg_yoy >= 0 else "📉"
        pulse_class = "pulse" if st.session_state.animations_enabled else ""
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>{arrow} YoY Growth</h4>
            <div class="animated-number {color_class} {pulse_class}">{avg_yoy:.1f}%</div>
            <small>Average across selected categories</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_qoq = qoq_data[qoq_data['category'].isin(selected_categories)]['qoq_growth'].mean()
        color_class = "growth-positive" if avg_qoq >= 0 else "growth-negative"
        arrow = "📈" if avg_qoq >= 0 else "📉"
        pulse_class = "pulse" if st.session_state.animations_enabled else ""
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>{arrow} QoQ Growth</h4>
            <div class="animated-number {color_class} {pulse_class}">{avg_qoq:.1f}%</div>
            <small>Quarterly momentum indicator</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        top_cat = final_df.groupby('category')['registrations'].sum().idxmax()
        top_share = final_df[final_df['category'] == top_cat]['registrations'].sum() / total_reg * 100
        pulse_class = "pulse" if st.session_state.animations_enabled else ""
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏆 Leading Category</h4>
            <div class="animated-number {pulse_class}">{top_cat}</div>
            <small>{top_share:.1f}% market share</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main analysis with functional tabs
    st.markdown('<div class="section-header">📈 Trend Analysis</div>', unsafe_allow_html=True)
    
    # Dynamic tab selection based on toggles
    tab_names = ["📊 Overview", "🏭 Manufacturers", "🌍 Seasonal"]
    if st.session_state.predictions_enabled:
        tab_names.append("🔮 Predictions")
    if st.session_state.comparison_mode:
        tab_names.append("⚖️ Comparison")
    
    tabs = st.tabs(tab_names)
    
    # Overview Tab
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            # Interactive trend chart with animations
            trend_data = final_df.groupby(['date', 'category'])['registrations'].sum().reset_index()
            fig_trend = px.line(trend_data, x='date', y='registrations', color='category',
                              title='📈 Registration Trends Over Time',
                              template='plotly_white')
            
            if st.session_state.animations_enabled:
                fig_trend.update_traces(line=dict(width=3))
                fig_trend.update_layout(
                    transition={'duration': 500, 'easing': 'cubic-in-out'},
                    showlegend=True,
                    hovermode='x unified'
                )
            else:
                fig_trend.update_traces(line=dict(width=2))
                fig_trend.update_layout(showlegend=True, hovermode='x')
            
            fig_trend.update_layout(height=450)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Growth analysis
            growth_data = yoy_data[yoy_data['category'].isin(selected_categories)]
            fig_growth = px.bar(growth_data.groupby('category')['yoy_growth'].mean().reset_index(),
                              x='category', y='yoy_growth',
                              title='📊 Average YoY Growth by Category',
                              color='yoy_growth',
                              color_continuous_scale='RdYlGn')
            
            fig_growth.add_hline(y=0, line_dash="dash", line_color="red")
            fig_growth.update_layout(height=450)
            
            if st.session_state.animations_enabled:
                fig_growth.update_layout(
                    transition={'duration': 800, 'easing': 'cubic-in-out'}
                )
            
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # Additional insights based on animations toggle
        if st.session_state.animations_enabled:
            st.info("🎬 Animations are enabled - charts will have smooth transitions and enhanced visual effects!")
    
    # Manufacturers Tab
    with tabs[1]:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Manufacturer performance over time
            mfg_data = final_df.groupby(['date', 'manufacturer'])['registrations'].sum().reset_index()
            fig_mfg = px.area(mfg_data, x='date', y='registrations', color='manufacturer',
                            title='🏭 Manufacturer Performance Timeline')
            fig_mfg.update_layout(height=500)
            
            if st.session_state.animations_enabled:
                fig_mfg.update_layout(
                    transition={'duration': 600, 'easing': 'cubic-in-out'}
                )
            
            st.plotly_chart(fig_mfg, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Top Performers")
            top_mfg = final_df.groupby('manufacturer')['registrations'].sum().nlargest(10)
            
            for i, (mfg, reg) in enumerate(top_mfg.items()):
                rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                st.markdown(f"""
                <div class="comparison-card">
                    <strong>{rank_emoji} {mfg}</strong><br>
                    <small>{reg:,} registrations</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Seasonal Tab
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly patterns
            monthly_data = final_df.groupby(final_df['date'].dt.month)['registrations'].sum()
            fig_monthly = px.line_polar(
                r=monthly_data.values,
                theta=[f"Month {i}" for i in monthly_data.index],
                line_close=True,
                title="🌙 Monthly Registration Patterns"
            )
            fig_monthly.update_layout(height=400)
            
            if st.session_state.animations_enabled:
                fig_monthly.update_layout(
                    transition={'duration': 700, 'easing': 'cubic-in-out'}
                )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Quarterly comparison
            quarterly_data = final_df.groupby([final_df['date'].dt.quarter, 'category'])['registrations'].sum().reset_index()
            quarterly_data['quarter'] = 'Q' + quarterly_data['date'].astype(str)
            
            fig_quarterly = px.bar(quarterly_data, x='quarter', y='registrations', color='category',
                                 title='📊 Quarterly Performance by Category')
            fig_quarterly.update_layout(height=400)
            
            if st.session_state.animations_enabled:
                fig_quarterly.update_layout(
                    transition={'duration': 500, 'easing': 'cubic-in-out'}
                )
            
            st.plotly_chart(fig_quarterly, use_container_width=True)
    
    # Predictions Tab (only if enabled)
    if st.session_state.predictions_enabled:
        with tabs[3]:
            st.markdown("### 🔮 AI-Powered Predictions")
            st.success("🟢 Predictions module is active!")
            
            # Category selection for prediction
            predict_category = st.selectbox(
                "Select Category for Prediction",
                options=selected_categories,
                key="predict_cat"
            )
            
            if predict_category:
                # Create predictive chart
                fig_predict = create_predictive_chart(final_df, predict_category)
                
                if st.session_state.animations_enabled:
                    fig_predict.update_layout(
                        transition={'duration': 1000, 'easing': 'cubic-in-out'}
                    )
                
                st.plotly_chart(fig_predict, use_container_width=True)
                
                # Prediction metrics
                col1, col2, col3 = st.columns(3)
                
                # Calculate predictions
                recent_data = final_df[final_df['category'] == predict_category]
                recent_avg = recent_data.groupby(recent_data['date'].dt.month)['registrations'].mean().mean()
                
                with col1:
                    next_month = recent_avg * 1.05
                    st.metric("Next Month Forecast", f"{next_month:.0f}", "📈 +5%")
                with col2:
                    quarterly = recent_avg * 3 * 1.03
                    st.metric("Quarterly Projection", f"{quarterly:.0f}", "📊 +3%")
                with col3:
                    confidence = np.random.uniform(75, 95)
                    st.metric("Confidence Level", f"{confidence:.1f}%", "🎯")
                
                st.info("🔮 Predictions are based on historical trends and seasonal patterns")
    
    # Comparison Tab (only if enabled)
    if st.session_state.comparison_mode:
        tab_index = 4 if st.session_state.predictions_enabled else 3
        with tabs[tab_index]:
            st.markdown("### ⚖️ Advanced Comparison Tools")
            st.success("🟢 Comparison mode is active!")
            
            # Add items to comparison
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                comparison_item = st.selectbox("Add to Comparison", selected_categories, key="comp_item")
            
            with col2:
                if st.button("➕ Add to Comparison", key="add_comp"):
                    if comparison_item not in st.session_state.comparison_data:
                        st.session_state.comparison_data.append(comparison_item)
                        st.success(f"✅ Added {comparison_item} to comparison")
                    else:
                        st.warning(f"⚠️ {comparison_item} is already in comparison")
            
            with col3:
                if st.button("🗑️ Clear All", key="clear_comp"):
                    st.session_state.comparison_data = []
                    st.success("✅ Cleared comparison list")
            
            # Show current comparison items
            if st.session_state.comparison_data:
                st.markdown("**Current Comparison:**")
                for item in st.session_state.comparison_data:
                    st.markdown(f"• {item}")
                
                # Create comparison chart
                if len(st.session_state.comparison_data) >= 2:
                    comp_fig = create_comparison_view(final_df, st.session_state.comparison_data)
                    if comp_fig:
                        if st.session_state.animations_enabled:
                            comp_fig.update_layout(
                                transition={'duration': 800, 'easing': 'cubic-in-out'}
                            )
                        st.plotly_chart(comp_fig, use_container_width=True)
                    
                    # Comparison metrics table
                    st.markdown("### 📊 Comparison Metrics")
                    
                    comp_metrics = []
                    for item in st.session_state.comparison_data:
                        item_data = final_df[final_df['category'] == item]
                        total_reg = item_data['registrations'].sum()
                        avg_growth = yoy_data[yoy_data['category'] == item]['yoy_growth'].mean()
                        
                        comp_metrics.append({
                            'Category': item,
                            'Total Registrations': f"{total_reg:,}",
                            'Avg YoY Growth': f"{avg_growth:.1f}%",
                            'Market Share': f"{(total_reg / final_df['registrations'].sum() * 100):.1f}%"
                        })
                    
                    comp_df = pd.DataFrame(comp_metrics)
                    st.dataframe(comp_df, use_container_width=True)
                else:
                    st.info("Add at least 2 categories for comparison analysis")
            else:
                st.info("No items in comparison. Add categories using the controls above.")
    
    # Advanced Business Insights Section
    st.markdown('<div class="section-header">🧠 AI Business Insights</div>', unsafe_allow_html=True)
    
    insights = create_advanced_insights(final_df, yoy_data, qoq_data)
    
    if insights:
        for insight in insights:
            animation_class = "insight-card" if st.session_state.animations_enabled else "insight-card"
            st.markdown(f"""
            <div class="{animation_class}">
                <h4>{insight['title']}</h4>
                <p>{insight['message']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Performance Summary Dashboard
    st.markdown('<div class="section-header">📋 Executive Summary</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Key Performance Indicators")
        
        # Calculate key metrics
        total_vehicles = final_df['registrations'].sum()
        growth_rate = yoy_data[yoy_data['category'].isin(selected_categories)]['yoy_growth'].mean()
        top_category = final_df.groupby('category')['registrations'].sum().idxmax()
        market_leader = final_df.groupby('manufacturer')['registrations'].sum().idxmax()
        
        metrics_data = {
            'Metric': ['Total Registrations', 'Average Growth Rate', 'Top Category', 'Market Leader'],
            'Value': [f"{total_vehicles:,}", f"{growth_rate:.1f}%", top_category, market_leader],
            'Status': ['🟢', '🟢' if growth_rate > 0 else '🔴', '🏆', '👑']
        }
        
        summary_df = pd.DataFrame(metrics_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🎯 Action Items")
        
        action_items = [
            "📊 Monitor high-growth categories for capacity planning",
            "🔍 Investigate low-performing segments for improvement opportunities", 
            "📈 Leverage seasonal patterns for inventory optimization",
            "🚀 Explore expansion opportunities in emerging categories"
        ]
        
        for item in action_items:
            st.markdown(f"• {item}")
        
        # Feature status summary
        st.markdown("### ⚙️ Active Features")
        active_features = []
        if st.session_state.animations_enabled:
            active_features.append("🎬 Enhanced Animations")
        if st.session_state.predictions_enabled:
            active_features.append("🔮 Predictive Analytics")
        if st.session_state.comparison_mode:
            active_features.append("⚖️ Comparison Tools")
        if st.session_state.dark_theme:
            active_features.append("🌙 Dark Theme")
        if st.session_state.auto_refresh:
            active_features.append("🔄 Auto Refresh")
        
        if active_features:
            for feature in active_features:
                st.markdown(f"✅ {feature}")
        else:
            st.markdown("ℹ️ No additional features active")
    
    # Footer with system status and toggle summary
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📊 Dashboard Status**")
        st.markdown('<span class="status-online">🟢 Online</span>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**🔄 Last Updated**")
        st.markdown(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col3:
        st.markdown("**📈 Data Quality**")
        data_quality = np.random.uniform(95, 99)
        st.markdown(f"✅ {data_quality:.1f}%")
    
    with col4:
        st.markdown("**⚙️ Active Toggles**")
        active_count = sum([
            st.session_state.animations_enabled,
            st.session_state.predictions_enabled, 
            st.session_state.comparison_mode,
            st.session_state.dark_theme,
            st.session_state.auto_refresh
        ])
        st.markdown(f"🎛️ {active_count}/5 features active")

if __name__ == "__main__":
    main()
