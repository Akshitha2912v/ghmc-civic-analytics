import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GHMC Civic Analytics Dashboard", layout="wide")

st.title("🏛️ Greater Hyderabad Municipal Corporation (GHMC)")
st.subheader("Executive Civic Grievance & SLA Performance Dashboard")
st.markdown("---")

def load_dashboard_data():
    conn = sqlite3.connect('ghmc_civic.db')
    query = """
    SELECT f.Complaint_ID, f.Status, f.Source_Channel, f.Feedback_Rating,
           f.Days_To_Resolve, f.SLA_Status, l.Circle, l.Ward_Number, c.Category_Name
    FROM fact_complaints f
    JOIN dim_location l ON f.Location_ID = l.Location_ID
    JOIN dim_category c ON f.Category_ID = c.Category_ID
    """
    master_df = pd.read_sql_query(query, conn)
    conn.close()
    return master_df

try:
    master_df = load_dashboard_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Settings")
    selected_circle = st.sidebar.selectbox("Select Municipal Circle", ["ALL ZONES"] + list(master_df['Circle'].unique()))

    if selected_circle != "ALL ZONES":
        filtered_df = master_df[master_df['Circle'] == selected_circle]
    else:
        filtered_df = master_df

    # --- KPI METRIC CARDS ---
    total_complaints = len(filtered_df)
    open_cases = len(filtered_df[filtered_df['Status'].isin(['Open', 'In Progress'])])
    
    # Calculate real SLA metrics
    resolved_df = filtered_df[filtered_df['Status'].isin(['Resolved', 'Closed'])]
    total_resolved = len(resolved_df)
    breached_count = len(resolved_df[resolved_df['SLA_Status'] == 'BREACHED'])
    
    sla_compliance_pct = ((total_resolved - breached_count) / total_resolved * 100) if total_resolved > 0 else 0
    avg_resolution_days = resolved_df[resolved_df['Days_To_Resolve'] >= 0]['Days_To_Resolve'].mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="📥 Total Grievances Logged", value=f"{total_complaints:,}")
    kpi2.metric(label="⏳ Active Backlog", value=f"{open_cases:,}")
    kpi3.metric(label="🚨 Target SLA Compliance (Within 7 Days)", value=f"{sla_compliance_pct:.1f}%")
    kpi4.metric(label="⏱️ Avg Resolution Pace", value=f"{avg_resolution_days:.1f} Days")

    st.markdown("---")

    # --- VISUALIZATIONS ---
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 🚨 Operational SLA Breach Risk by Category")
        # Aggregating categories showing breach ratio
        sla_chart_df = filtered_df[filtered_df['Status'].isin(['Resolved', 'Closed'])]
        fig_bar = px.histogram(sla_chart_df, x='Category_Name', color='SLA_Status',
                               barmode='group', color_discrete_map={'COMPLIANT': '#2ecc71', 'BREACHED': '#e74c3c'},
                               template="plotly_dark", labels={'Category_Name': 'Department'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.write("### 📈 Turnaround Efficiency Trend")
        # Scatter layout showing pacing distribution
        fig_scatter = px.scatter(resolved_df, x='Days_To_Resolve', y='Feedback_Rating',
                                 color='SLA_Status', size='Feedback_Rating',
                                 color_discrete_map={'COMPLIANT': '#2ecc71', 'BREACHED': '#e74c3c'},
                                 template="plotly_dark", title="Resolution Pace vs Citizen Rating")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- RAW LOOKUP TABLE ---
    st.markdown("---")
    st.write("### 🔍 Raw Incident Warehouse Lookup (Including Operational Columns)")
    st.dataframe(filtered_df[['Complaint_ID', 'Circle', 'Category_Name', 'Status', 'Days_To_Resolve', 'SLA_Status']], use_container_width=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
