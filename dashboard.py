import streamlit as st
import requests
import pandas as pd
import time

# Firebase URL (Same as your project)
DB_URL = "https://hackathon-project-333b5-default-rtdb.firebaseio.com/live_monitoring.json"

st.set_page_config(page_title="Rakshak AI Dashboard", layout="wide")
st.title("🛡️ Rakshak AI - Live Security Monitor")

# Sidebar for status
st.sidebar.success("System Status: Online")
st.sidebar.info("Monitoring for: Weapon, Fire, Motion")

placeholder = st.empty()

while True:
    try:
        response = requests.get(DB_URL)
        data = response.json()
        
        if data:
            # Data ko table format mein convert karna
            df = pd.DataFrame.from_dict(data, orient='index')
            # Naya data upar dikhane ke liye reverse karna
            df = df.iloc[::-1]
            
            with placeholder.container():
                st.subheader("Live Logs from Cloud")
                st.dataframe(df, use_container_width=True)
                
                # Alerts highlight karna
                latest_event = df.iloc[0]['event']
                if latest_event == "WEAPON":
                    st.error(f"⚠️ CRITICAL: {latest_event} Detected!")
                elif latest_event == "FIRE":
                    st.warning(f"🔥 ALERT: {latest_event} Detected!")
        else:
            st.write("No logs found yet.")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")
    
    time.sleep(2) # Har 2 second mein refresh