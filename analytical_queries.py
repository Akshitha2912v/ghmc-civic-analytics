import sqlite3
import pandas as pd

def run_analytics():
    db_file = 'ghmc_civic.db'
    conn = sqlite3.connect(db_file)
    
    print("\n" + "="*50)
    print("      GHMC CIVIC ANALYTICAL REPORT ENGINE")
    print("="*50)
    
    # Query 1: Complaint Breakdown by Circle (Volume Tracking)
    query_circles = """
    SELECT l.Circle, COUNT(f.Complaint_ID) AS Total_Complaints
    FROM fact_complaints f
    JOIN dim_location l ON f.Location_ID = l.Location_ID
    GROUP BY l.Circle
    ORDER BY Total_Complaints DESC;
    """
    print("\n📊 1. COMPLAINT VOLUMES BY MUNICIPAL CIRCLE:")
    df_circles = pd.read_sql_query(query_circles, conn)
    print(df_circles.to_string(index=False))
    
    # Query 2: Performance Evaluation (Average Feedback Score per Category)
    query_feedback = """
    SELECT c.Category_Name, 
           ROUND(AVG(f.Feedback_Rating), 2) AS Avg_Citizen_Rating,
           COUNT(f.Complaint_ID) AS Resolved_Count
    FROM fact_complaints f
    JOIN dim_category c ON f.Category_ID = c.Category_ID
    WHERE f.Status IN ('Resolved', 'Closed')
    GROUP BY c.Category_Name
    ORDER BY Avg_Citizen_Rating ASC;
    """
    print("\n⭐️ 2. CITIZEN SATISFACTION BY PERFORMANCE CATEGORY (Lowest to Highest):")
    df_feedback = pd.read_sql_query(query_feedback, conn)
    print(df_feedback.to_string(index=False))

    # Query 3: Operational Status Matrix
    query_status = """
    SELECT Status, COUNT(Complaint_ID) AS Count
    FROM fact_complaints
    GROUP BY Status;
    """
    print("\n⚙️ 3. OPERATIONAL PIPELINE BREAKDOWN:")
    df_status = pd.read_sql_query(query_status, conn)
    print(df_status.to_string(index=False))

    conn.close()

if __name__ == '__main__':
    run_analytics()
