# 🏛️ End-to-End GHMC Civic Grievance & SLA Performance Analytics

An enterprise-grade Data Engineering and Analytics project that automates the ingestion, transformation, and interactive visualization of civic complaint streams for the **Greater Hyderabad Municipal Corporation (GHMC)**. 

This project simulates a live city-wide data infrastructure to track municipal operational efficiency, calculate Service-Level Agreement (SLA) turnaround paces, and uncover departmental bottlenecks.

---

## 🚀 Project Architecture & Data Flow

[Messy Raw CSV Source]
│
▼
[ETL Ingestion Pipeline] ──► (Text Cleaning, Regex Formatting, Null Filling)
│
▼
[SQLite Data Warehouse] ──► (Relational Star Schema: Fact & Dimension Tables)
│
▼
[Interactive BI Dashboard] ──► (Dynamic Dropdowns, Plotly Operational Charts)
## 🛠️ The Tech Stack
* **Language:** Python 3
* **Data Processing & Engineering:** Pandas, NumPy
* **Data Warehouse Storage:** SQLite3 Relational Database
* **Interactive Visualization Layer:** Streamlit, Plotly Express

---

## ⚙️ Core Technical Features

### 1. Advanced ETL & Text Standardization
Raw civic grievance inputs contain human-error anomalies (e.g., mismatched casing, trail spaces, duplicate naming formats like `LB Nagar`, `l.b. nagar`, and `LB_Nagar`). The pipeline cleans these variables programmatically into standardized canonical dimensions before any calculation occurs.

### 2. Relational Star Schema Model
To optimize query performance, data is restructured out of a flat spreadsheet format into a high-performance relational warehouse schema:
* `dim_location`: Maps Circle names and Ward numbers to indexed dimension keys.
* `dim_category`: Organizes distinct administrative municipal departments.
* `fact_complaints`: The core transactional ledger containing natural record keys mapped to dimension tables via surrogate integer IDs.

### 3. Operational SLA Turnaround Engine
The engine computes vectorized day intervals (`Days_To_Resolve`) between case open and closure stamps. It evaluates performance against a strict city-mandated **7-day SLA resolution window**, stamping resolved records dynamically as `COMPLIANT` or `BREACHED`.

---

## 📊 Analytical Insights

Running the querying matrix against the production warehouse surfaces business-critical metrics:
* **Zone Load Tracking:** Identifies exact case volume distribution profiles across municipal regions.
* **Citizen Satisfaction Matrix:** Evaluates average customer review weights grouped by department type.
* **Pipeline Backlog:** Tracks operational friction points by isolating active `Open` and `In Progress` bottlenecks.

---

## 🖥️ How to Run the System Locally

1. Install required dependencies:
   ```bash
   pip install pandas numpy streamlit plotly
   ```
2. Run the ETL pipeline to process raw data and construct your relational database:
   ```bash
   python3 etl_pipeline.py
   ```
3. Boot up the control tower analytics web interface:
   ```bash
   streamlit run app.py
   ```