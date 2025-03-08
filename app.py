import streamlit as st
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns
import pytz
from datetime import datetime

def process_file_contents(file_contents, timezone):
    """Process text file contents into a structured DataFrame with timezone adjustment"""
    records = []
    current_record = {}
    
    for line in file_contents.split('\n'):
        line = line.strip()
        if line:
            if ': ' in line:
                key, value = line.split(': ', 1)
                current_record[key] = value
            if line.startswith('Adds yours text:'):
                records.append(current_record)
                current_record = {}
    
    try:
        df = pd.DataFrame(records)[['Date', 'Like(s)']]
        df.columns = ['date', 'Likes']
        
        # Convert to datetime with UTC
        df['date'] = pd.to_datetime(df['date'], utc=True)
        
        # Convert to selected timezone
        df['date'] = df['date'].dt.tz_convert(timezone)
        
        df['Likes'] = df['Likes'].astype(int)
        
        # Add time-based columns
        df['day_of_week'] = df['date'].dt.day_name()
        df['time'] = df['date'].dt.time
        df['time_period'] = df['date'].dt.strftime('%p')
        df['hour'] = df['date'].dt.hour
        df['hour_12'] = df['date'].dt.strftime('%I')
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

def create_heatmap(df):
    """Create and return a heatmap figure"""
    df_grouped = df.groupby(['day_of_week', 'hour']).agg({'Likes': 'mean'}).reset_index()
    df_grouped['Likes'] = df_grouped['Likes'].round(2)
    heatmap_data = df_grouped.pivot(index="day_of_week", columns="hour", values="Likes")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, 
                cmap="Purples", 
                fmt=".1f", 
                linewidths=0.5, 
                ax=ax)
    ax.set_title("Heatmap of Likes by Day and Hour")
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Day of the Week")
    return fig

def main():
    # App title and configuration
    st.title("Tiktok Posting Analyzer")
    st.markdown("Upload a text file to analyze like patterns by day and hour")
    
    # Timezone selection
    timezone_list = sorted(pytz.all_timezones)
    selected_timezone = st.selectbox(
        "Select your timezone",
        timezone_list,
        index=timezone_list.index('US/Pacific')  # Default to US/Pacific
    )
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    
    if uploaded_file is not None:
        # Read and display file contents
        file_contents = uploaded_file.read().decode("utf-8")
        
        with st.expander("View File Contents", expanded=False):
            st.text_area("Contents of the file:", file_contents, height=200)
        
        # Process data with selected timezone
        df = process_file_contents(file_contents, selected_timezone)
        
        if df is not None:
            # Display raw data
            with st.expander("View Processed Data", expanded=False):
                st.dataframe(df)
            
            # Display heatmap
            st.subheader("Likes Distribution Heatmap")
            fig = create_heatmap(df)
            st.pyplot(fig)
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            stats=st.container()
            with stats:
                st.metric("Total Likes", df['Likes'].sum())
                st.metric("Average Likes", round(df['Likes'].mean(), 2))
            
            # Show current timezone info
            st.write(f"Data displayed in: {selected_timezone}")

if __name__ == "__main__":
    main()