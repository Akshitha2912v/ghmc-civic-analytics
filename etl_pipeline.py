import pandas as pd
import sqlite3
import os
import numpy as np

def run_etl_pipeline():
    csv_file = 'raw_ghmc_complaints.csv'
    db_file = 'ghmc_civic.db'
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    print("Step 1: Extracting raw data from CSV...")
    df = pd.read_csv(csv_file)
    
    print("Step 2: Advanced Transforming & text cleaning...")
    df = df.dropna(subset=['Circle', 'Category'])
    
    # Standardize names
    df['Circle'] = df['Circle'].astype(str).str.upper().str.strip()
    df['Circle'] = df['Circle'].replace({
        'LB NAGAR': 'L.B. NAGAR', 'L B NAGAR': 'L.B. NAGAR', 'LB_NAGAR': 'L.B. NAGAR'
    })
    
    df['Category'] = df['Category'].astype(str).str.upper().str.strip()
    df['Category'] = df['Category'].replace({
        'STREET LIGHT': 'STREET LIGHTS', 
        'POTHOLE': 'POTHOLES/ROAD REPAIR', 
        'POTHOLES': 'POTHOLES/ROAD REPAIR',
        'GARBAGE DUMPING': 'GARBAGE DUMP CLEARANCE',
        'STRAY DOG MENACE': 'STRAY ANIMALS',
        'DRAINAGE & SEWAGE': 'WATER SUPPLY'
    })
    
    # Process Timestamps
    df['Created_At'] = pd.to_datetime(df['Created_At'])
    df['Resolved_At_Parsed'] = pd.to_datetime(df['Resolved_At'], errors='coerce')
    
    # --- NEW: ADVANCED RECRUITER METRICS ---
    # Calculate operational resolution turnaround time
    df['Days_To_Resolve'] = (df['Resolved_At_Parsed'] - df['Created_At']).dt.total_seconds() / (24 * 3600)
    df['Days_To_Resolve'] = df['Days_To_Resolve'].round(1).fillna(-1) # -1 represents open cases
    
    # Enforce a strict 7-day SLA rule
    df['SLA_Status'] = np.where(
        df['Status'].isin(['Resolved', 'Closed']),
        np.where(df['Days_To_Resolve'] > 7.0, 'BREACHED', 'COMPLIANT'),
        'PENDING'
    )
    
    # Fill remaining administrative nulls safely
    df['Resolved_At'] = df['Resolved_At'].fillna('N/A')
    df['Feedback_Rating'] = df['Feedback_Rating'].fillna(0).astype(int)
    
    print("Step 3: Remodeling data into perfect Dimensional Layout...")
    unique_categories = df['Category'].unique()
    dim_category = pd.DataFrame({
        'Category_ID': range(1, len(unique_categories) + 1),
        'Category_Name': unique_categories
    })
    
    dim_location = df[['Circle', 'Ward_Number']].drop_duplicates().reset_index(drop=True)
    dim_location.insert(0, 'Location_ID', range(1, len(dim_location) + 1))
    
    fact_df = df.merge(dim_category, left_on='Category', right_on='Category_Name') \
                .merge(dim_location, on=['Circle', 'Ward_Number'])
    
    fact_complaints = fact_df[[
        'Complaint_ID', 'Citizen_Name', 'Citizen_Phone', 'Location_ID', 
        'Category_ID', 'Status', 'Source_Channel', 'Created_At', 'Resolved_At', 
        'Feedback_Rating', 'Days_To_Resolve', 'SLA_Status'
    ]]
    
    print(f"Step 4: Re-loading clean tables into SQLite database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS fact_complaints;")
    cursor.execute("DROP TABLE IF EXISTS dim_category;")
    cursor.execute("DROP TABLE IF EXISTS dim_location;")
    
    dim_category.to_sql('dim_category', conn, if_exists='replace', index=False)
    dim_location.to_sql('dim_location', conn, if_exists='replace', index=False)
    fact_complaints.to_sql('fact_complaints', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    print("✓ Success! Re-engineered database created with operational SLA records.")

if __name__ == '__main__':
    run_etl_pipeline()
