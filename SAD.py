import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import time

# Function to load Lottie animations safely
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# Load animations
call_icon = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_kfqn7n4h.json")
login_icon = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_ktwnwv5m.json")
security_icon = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_7skesgr9.json")

# Set page layout
st.set_page_config(page_title="Schedule Adherence Dashboard", layout="wide")

# Session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Hardcoded credentials (replace with your authentication system in production)
VALID_CREDENTIALS = {
    "admin": "password123",
    "manager": "schedule456",
    "supervisor": "team789"
}

# Login page
def login_page():
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            width: 100%;
            border: none;
            background-color: #004aad;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #003882;
            transform: translateY(-2px);
        }
        .title {
            text-align: center;
            color: #004aad;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 class='title'>📞 Call Center Analytics</h1>", unsafe_allow_html=True)
            if login_icon:
                st_lottie(login_icon, height=200, key="login_icon")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if username in VALID_CREDENTIALS and password == VALID_CREDENTIALS[username]:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        with st.spinner("Authenticating..."):
                            time.sleep(1)
                        st.success("Login successful! Redirecting...")
                        time.sleep(1)
                        st.rerun()  # Changed from st.experimental_rerun() to st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            if security_icon:
                st_lottie(security_icon, height=100, key="security_icon")
            st.caption("© 2025 Call Center Analytics. All rights reserved.")

# Main dashboard
def main_dashboard():
    # Page title
    st.markdown(f"""<h1 style='text-align: center; color: #004aad;'>📞 Schedule Adherence Dashboard</h1>
                <p style='text-align: center; color: #666;'>Welcome, {st.session_state.username}!</p>""", 
                unsafe_allow_html=True)

    # Sidebar with icons and logout button
    with st.sidebar:
        if call_icon:
            st_lottie(call_icon, height=150, key="call_icon")
        st.write("### Schedule Adherence Dashboard")
        st.write("Use the filters below to explore the data.")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()  # Changed from st.experimental_rerun() to st.rerun()

    # File uploader
    uploaded_file = st.file_uploader("📂 Upload your dataset (CSV/Excel)", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            required_columns = {"Date", "TSA", "TTS", "supervisor", "teamlead", "Campaign"}
            if not required_columns.issubset(df.columns):
                st.error(f"Dataset must contain these columns: {', '.join(required_columns)}")
                st.stop()

            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

            # Sidebar filters
            st.sidebar.write("### 🎛️ Filters")
            week_filter = st.sidebar.multiselect("📅 Select Week", sorted(df["week"].dropna().unique())) if "week" in df.columns else []
            day_filter = st.sidebar.multiselect("📆 Select Days", sorted(df["day"].dropna().unique())) if "day" in df.columns else []

            # Date filter logic
            unique_dates = sorted(df["Date"].dropna().unique())
            if len(unique_dates) == 1:
                selected_date = st.sidebar.date_input("📌 Select Date", unique_dates[0])
            else:
                selected_date = st.sidebar.date_input("📌 Select Date", unique_dates[0], min_value=unique_dates[0], max_value=unique_dates[-1])

            # Apply filters
            filtered_df = df.copy()
            if week_filter:
                filtered_df = filtered_df[filtered_df["week"].isin(week_filter)]
            if day_filter:
                filtered_df = filtered_df[filtered_df["day"].isin(day_filter)]
            filtered_df = filtered_df[filtered_df["Date"] == pd.to_datetime(selected_date)]

            # Display raw data
            st.write("### 📊 Raw Data Preview")
            st.dataframe(filtered_df)

            # Calculate adherence using filtered data
            filtered_df["Adherence %"] = (filtered_df["TSA"] / filtered_df["TTS"]) * 100
            filtered_df["Adherence %"] = filtered_df["Adherence %"].round(2)
            overall_adherence = filtered_df["Adherence %"].mean().round(2)

            # Dashboard layout
            st.write("### 📈 Schedule Adherence Dashboard")
            col1, col2 = st.columns([2, 1])

            with col1:
                fig_donut = px.pie(
                    names=["Adherence", "Non-Adherence"],
                    values=[overall_adherence, 100 - overall_adherence] if not pd.isna(overall_adherence) else [0, 100],
                    hole=0.4,
                    title="Overall Adherence %",
                    color_discrete_sequence=["#004aad", "#FFA500"]
                )
                fig_donut.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_donut, use_container_width=True)

            with col2:
                campaign_adherence = filtered_df.groupby("Campaign")["Adherence %"].mean().reset_index()
                if not campaign_adherence.empty:
                    fig_campaign = px.line(
                        campaign_adherence,
                        x="Campaign",
                        y="Adherence %",
                        title="Campaign-wise Schedule Adherence",
                        markers=True,
                        text="Adherence %",
                        color_discrete_sequence=["#00FF00"]
                    )
                    fig_campaign.update_traces(textposition="top center")
                    st.plotly_chart(fig_campaign, use_container_width=True)

            # Second row of charts
            col3, col4 = st.columns(2)

            with col3:
                sup_adherence = filtered_df.groupby("supervisor")["Adherence %"].mean().reset_index()
                if not sup_adherence.empty:
                    fig_sup = px.bar(
                        sup_adherence,
                        x="supervisor",
                        y="Adherence %",
                        title="Supervisor-wise Schedule Adherence",
                        text="Adherence %",
                        color_discrete_sequence=["#004aad"]
                    )
                    fig_sup.update_traces(textposition="outside")
                    st.plotly_chart(fig_sup, use_container_width=True)

            with col4:
                tl_adherence = filtered_df.groupby("teamlead")["Adherence %"].mean().reset_index()
                if not tl_adherence.empty:
                    fig_tl = px.bar(
                        tl_adherence,
                        x="teamlead",
                        y="Adherence %",
                        title="Team Lead-wise Schedule Adherence",
                        text="Adherence %",
                        color_discrete_sequence=["#FFA500"]
                    )
                    fig_tl.update_traces(textposition="outside")
                    st.plotly_chart(fig_tl, use_container_width=True)

        except Exception as e:
            st.error(f"Error processing the file: {e}")

# App routing
if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()



## use streamlit run app.py to run the app.        