"""
Mock Data Generator for Greater Hyderabad Municipal Corporation (GHMC) Civic Grievances.

This script generates a realistic, messy dataset representing citizen complaints logged
across various GHMC administrative circles and intake channels. It introduces common
real-world data quality issues (dirty strings, inconsistent phone formatting, mixed case,
missing values) while strictly enforcing domain business logic.

Specifications:
- 5,000 rows exported to 'raw_ghmc_complaints.csv'
- Required columns:
    1. Complaint_ID (Format: GHMC-2026XXXXX)
    2. Citizen_Name
    3. Citizen_Phone
    4. Circle (Charminar, Khairatabad, Secunderabad, Serilingampally, Kukatpally, L.B. Nagar, etc.)
    5. Ward_Number (1 to 150)
    6. Category (Sanitation, Street Lights, Potholes, Water Supply, etc.)
    7. Status (Open, In Progress, Resolved, Closed)
    8. Source_Channel (GHMC App, Twitter/X, Dial 100, etc.)
    9. Created_At
    10. Resolved_At
    11. Feedback_Rating (1-5)
- Business Logic:
    - Status in ('Open', 'In Progress') -> Resolved_At and Feedback_Rating MUST be NaN/missing.
    - Status in ('Resolved', 'Closed')  -> Resolved_At is 1 to 14 days after Created_At.
                                        Feedback_Rating is an integer 1-5 (or optional NaN if citizen skipped rating).
"""

import argparse
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Master Reference Pools & Constants (GHMC Specific)
# ---------------------------------------------------------------------------

CIRCLES_CANONICAL = [
    "Charminar",
    "Khairatabad",
    "Secunderabad",
    "Serilingampally",
    "Kukatpally",
    "L.B. Nagar",
]

CATEGORIES_CANONICAL = [
    "Sanitation",
    "Street Lights",
    "Potholes",
    "Water Supply",
    "Drainage & Sewage",
    "Garbage Dumping",
    "Stray Dog Menace",
    "Illegal Encroachment",
]

SOURCE_CHANNELS_CANONICAL = [
    "GHMC App",
    "Twitter/X",
    "Dial 100",
    "Toll Free 21111111",
    "Ward Office Walk-in",
]

STATUS_CHOICES = ["Resolved", "Closed", "In Progress", "Open"]
STATUS_WEIGHTS = [0.45, 0.25, 0.18, 0.12]

FIRST_NAMES = [
    "Sai", "Venkat", "Rahul", "Priya", "Ananya", "Mohammed", "Fatima",
    "Suresh", "Ramesh", "Sneha", "Lakshmi", "Srikanth", "Divya", "Ayesha",
    "Vikram", "Pradeep", "Swathi", "Harish", "Bhavani", "Arvind", "Syed",
    "Naveen", "Keerthi", "Rajesh", "Manisha", "Abdul", "Akhil", "Pooja",
    "Karthik", "Sunitha", "Kavitha", "Naresh", "Deepa", "Santosh", "Noor",
    "Kranthi", "Manoj", "Sravani", "Jagadeesh", "Asma", "Chaitanya", "Vamshi",
    "Meenakshi", "Pavan", "Tarun", "Rohit", "Swapna", "Goutham", "Shabana"
]

LAST_NAMES = [
    "Reddy", "Rao", "Goud", "Sharma", "Khan", "Begum", "Varma", "Chowdary",
    "Patel", "Chary", "Yadav", "Ahmed", "Murthy", "Raju", "Naidu", "Ali",
    "Kumar", "Joshi", "Kulkarni", "Shaik", "Gupta", "Mishra", "Deshmukh"
]


# ---------------------------------------------------------------------------
# Generator Functions with Realistic Messiness
# ---------------------------------------------------------------------------

def generate_citizen_name() -> str | float:
    """Generate a realistic citizen name with dirty text variations or missingness."""
    roll = random.random()
    if roll < 0.025:
        # Missing value
        return np.nan

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    full_name = f"{first} {last}"

    # Add realistic dirty data variations
    style_roll = random.random()
    if style_roll < 0.10:
        # ALL CAPS
        return full_name.upper()
    elif style_roll < 0.17:
        # all lowercase
        return full_name.lower()
    elif style_roll < 0.24:
        # Accidental leading / trailing whitespace
        pad_left = " " * random.randint(1, 3)
        pad_right = " " * random.randint(1, 2)
        return f"{pad_left}{full_name}{pad_right}"
    elif style_roll < 0.29:
        # Formal prefix / honorific
        salutation = random.choice(["Mr.", "Mrs.", "Dr.", "Smt.", "Sri."])
        return f"{salutation} {full_name}"
    else:
        # Standard Title Case
        return full_name


def generate_citizen_phone() -> str | float:
    """Generate a realistic Indian 10-digit mobile number with various input format noise."""
    roll = random.random()
    if roll < 0.035:
        # Missing phone number (anonymous / unrecorded)
        return np.nan

    # Indian mobile prefixes (starts with 6, 7, 8, or 9)
    lead_digit = random.choice(["6", "7", "8", "9"])
    remaining_digits = "".join([str(random.randint(0, 9)) for _ in range(9)])
    raw_10 = f"{lead_digit}{remaining_digits}"

    format_roll = random.random()
    if format_roll < 0.35:
        # Clean 10 digits
        return raw_10
    elif format_roll < 0.55:
        # International code +91
        sep = random.choice([" ", "-", ""])
        return f"+91{sep}{raw_10}"
    elif format_roll < 0.70:
        # Grouped with spaces or hyphen: 98490 12345 or 98490-12345
        return f"{raw_10[:5]}{random.choice([' ', '-'])}{raw_10[5:]}"
    elif format_roll < 0.82:
        # Leading zero e.g. 09849012345
        return f"0{raw_10}"
    elif format_roll < 0.92:
        # Messy trailing/leading whitespace
        return f" {raw_10} "
    else:
        # Malformed / incomplete (e.g. 9 digits or truncated) - realistic entry errors
        return raw_10[:9]


def generate_circle() -> str | float:
    """Pick circle with realistic casing, spacing, and abbreviation inconsistencies."""
    roll = random.random()
    if roll < 0.015:
        return np.nan

    circle = random.choice(CIRCLES_CANONICAL)
    noise_roll = random.random()
    if noise_roll < 0.06:
        # Whitespace artifact
        return f" {circle} "
    elif noise_roll < 0.10:
        # Lowercase / uppercase inconsistency
        return circle.lower() if random.random() < 0.5 else circle.upper()
    elif noise_roll < 0.16 and circle == "L.B. Nagar":
        # Variation in punctuation for LB Nagar
        return random.choice(["LB Nagar", "L B Nagar", "LB_Nagar"])
    return circle


def generate_ward_number() -> int | float:
    """Pick GHMC Ward number (1 to 150) with occasional missing data."""
    if random.random() < 0.02:
        return np.nan
    return random.randint(1, 150)


def generate_category() -> str | float:
    """Pick complaint category with realistic text noise."""
    if random.random() < 0.015:
        return np.nan

    cat = random.choice(CATEGORIES_CANONICAL)
    noise_roll = random.random()
    if noise_roll < 0.06:
        return cat.lower()
    elif noise_roll < 0.11:
        return f" {cat} "
    elif noise_roll < 0.15 and cat == "Street Lights":
        return "Street Light"  # Singular vs plural mismatch
    elif noise_roll < 0.19 and cat == "Potholes":
        return "Pothole"
    return cat


def generate_source_channel() -> str | float:
    """Select reporting channel with real-world label variations."""
    if random.random() < 0.01:
        return np.nan

    # Heavy emphasis on GHMC App, Twitter/X, and Dial 100 as specified
    primary_channels = ["GHMC App", "Twitter/X", "Dial 100"]
    channel = random.choices(
        primary_channels + ["Toll Free 21111111", "Ward Office Walk-in"],
        weights=[0.45, 0.25, 0.20, 0.06, 0.04],
        k=1
    )[0]

    # Realistic variation
    if channel == "Twitter/X" and random.random() < 0.20:
        return random.choice(["Twitter", "X", "Twitter / X"])
    elif channel == "GHMC App" and random.random() < 0.15:
        return random.choice(["ghmc app", "GHMC Mobile App", "GHMC_App"])
    elif channel == "Dial 100" and random.random() < 0.15:
        return "Dial-100"
    return channel


def generate_created_at(start_date: datetime, end_date: datetime) -> tuple[datetime, str]:
    """Generate a random created datetime and a formatted string."""
    time_delta = end_date - start_date
    random_seconds = random.randint(0, int(time_delta.total_seconds()))
    created_dt = start_date + timedelta(seconds=random_seconds)
    formatted = created_dt.strftime("%Y-%m-%d %H:%M:%S")
    return created_dt, formatted


def generate_resolved_at(status: str, created_dt: datetime) -> tuple[datetime | None, str | float]:
    """
    Enforce resolution date business logic:
    - Status in ('Open', 'In Progress') -> NaN / None
    - Status in ('Resolved', 'Closed')  -> strictly 1 to 14 days after Created_At
    """
    if status in ["Open", "In Progress"]:
        return None, np.nan

    # Random resolution delta: strictly between 1 day (86,400s) and 14 days (1,209,600s)
    resolution_seconds = random.randint(86400, 14 * 86400)
    resolved_dt = created_dt + timedelta(seconds=resolution_seconds)
    formatted = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")

    return resolved_dt, formatted


def generate_feedback_rating(status: str) -> float:
    """
    Enforce feedback rating business logic:
    - Status in ('Open', 'In Progress') -> NaN
    - Status in ('Resolved', 'Closed')  -> Integer 1-5 (with realistic missing feedback for some resolved tickets)
    """
    if status in ["Open", "In Progress"]:
        return np.nan

    # For resolved/closed tickets, not all citizens submit feedback (~25% skip rating)
    if random.random() < 0.25:
        return np.nan

    # Rating from 1 to 5 (skewed slightly realistic: civic complaints often get polarized reviews)
    return float(random.choices([1, 2, 3, 4, 5], weights=[0.20, 0.15, 0.20, 0.25, 0.20])[0])


# ---------------------------------------------------------------------------
# Main Dataset Builder
# ---------------------------------------------------------------------------

def generate_ghmc_complaints(
    num_rows: int = 5000,
    seed: int | None = 42
) -> pd.DataFrame:
    """
    Generate a pandas DataFrame containing mock GHMC Civic Grievance records.

    Parameters:
        num_rows: Number of complaint records to generate (default: 5000)
        seed: Random seed for deterministic reproducibility (optional)

    Returns:
        pd.DataFrame with 11 specified columns and realistic messy values.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    records = []
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    end_date = datetime(2026, 10, 15, 23, 59, 59)

    for i in range(1, num_rows + 1):
        # Format: GHMC-2026XXXXX (5-digit padded identifier)
        complaint_id = f"GHMC-2026{i:05d}"

        # Status determination based on realistic distribution
        status = random.choices(STATUS_CHOICES, weights=STATUS_WEIGHTS, k=1)[0]

        # Citizen info
        citizen_name = generate_citizen_name()
        citizen_phone = generate_citizen_phone()

        # Administrative / Location info
        circle = generate_circle()
        ward_number = generate_ward_number()

        # Grievance category & source channel
        category = generate_category()
        source_channel = generate_source_channel()

        # Timestamps
        created_dt, created_str = generate_created_at(start_date, end_date)
        _, resolved_str = generate_resolved_at(status, created_dt)

        # Feedback Rating
        feedback_rating = generate_feedback_rating(status)

        records.append({
            "Complaint_ID": complaint_id,
            "Citizen_Name": citizen_name,
            "Citizen_Phone": citizen_phone,
            "Circle": circle,
            "Ward_Number": ward_number,
            "Category": category,
            "Status": status,
            "Source_Channel": source_channel,
            "Created_At": created_str,
            "Resolved_At": resolved_str,
            "Feedback_Rating": feedback_rating,
        })

    df = pd.DataFrame(records)
    return df


def validate_dataset(df: pd.DataFrame) -> bool:
    """Validate that the generated DataFrame satisfies all user-specified requirements."""
    print("\n" + "=" * 60)
    print("DATASET VALIDATION CHECKS")
    print("=" * 60)

    # Check 1: Row Count
    assert len(df) == 5000, f"Expected 5,000 rows, found {len(df)}"
    print(f"✓ Row Count: Exactly {len(df):,} rows generated.")

    # Check 2: Required Columns
    expected_cols = [
        "Complaint_ID", "Citizen_Name", "Citizen_Phone", "Circle",
        "Ward_Number", "Category", "Status", "Source_Channel",
        "Created_At", "Resolved_At", "Feedback_Rating"
    ]
    assert list(df.columns) == expected_cols, f"Column mismatch. Expected: {expected_cols}"
    print(f"✓ Columns: All {len(expected_cols)} required columns present in exact order.")

    # Check 3: Complaint_ID format
    id_pattern_valid = df["Complaint_ID"].str.match(r"^GHMC-2026\d{5}$").all()
    assert id_pattern_valid, "Invalid Complaint_ID format detected!"
    print(f"✓ Complaint_ID Format: All IDs strictly match 'GHMC-2026XXXXX'.")

    # Check 4: Open / In Progress must have NaN Resolved_At and NaN Feedback_Rating
    unresolved_mask = df["Status"].isin(["Open", "In Progress"])
    unresolved_resolved_at_null = df.loc[unresolved_mask, "Resolved_At"].isna().all()
    unresolved_feedback_null = df.loc[unresolved_mask, "Feedback_Rating"].isna().all()

    assert unresolved_resolved_at_null, "Found non-null Resolved_At for Open/In Progress status!"
    assert unresolved_feedback_null, "Found non-null Feedback_Rating for Open/In Progress status!"
    print("✓ Business Logic (Unresolved): 100% of 'Open'/'In Progress' have NaN Resolved_At & Feedback_Rating.")

    # Check 5: Resolved / Closed must have resolution date 1 to 14 days after Created_At
    resolved_mask = df["Status"].isin(["Resolved", "Closed"])
    resolved_df = df[resolved_mask].copy()
    assert resolved_df["Resolved_At"].notna().all(), "Found NaN Resolved_At for Resolved/Closed status!"

    created_parsed = pd.to_datetime(resolved_df["Created_At"])
    resolved_parsed = pd.to_datetime(resolved_df["Resolved_At"])
    diff_days = (resolved_parsed - created_parsed).dt.total_seconds() / 86400.0

    min_days = diff_days.min()
    max_days = diff_days.max()
    assert min_days >= 1.0, f"Resolution delta below 1 day: {min_days}"
    assert max_days <= 14.0, f"Resolution delta exceeded 14 days: {max_days}"
    print(f"✓ Business Logic (Resolved/Closed): All resolution times are between {min_days:.2f} and {max_days:.2f} days after creation.")

    # Check 6: Feedback Ratings must be 1-5 or NaN
    valid_ratings = df["Feedback_Rating"].dropna().isin([1.0, 2.0, 3.0, 4.0, 5.0]).all()
    assert valid_ratings, "Invalid Feedback_Rating values detected!"
    print("✓ Feedback_Rating Range: Validated in range 1-5.")

    print("=" * 60 + "\n")
    return True


# ---------------------------------------------------------------------------
# CLI Execution Block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a realistic, messy dataset for GHMC Civic Grievances."
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=5000,
        help="Number of grievance records to generate (default: 5000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="raw_ghmc_complaints.csv",
        help="Target output CSV file path (default: raw_ghmc_complaints.csv)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    print(f"Generating {args.rows:,} GHMC grievance records (seed={args.seed})...")
    df_complaints = generate_ghmc_complaints(num_rows=args.rows, seed=args.seed)

    # Validate against all functional specifications
    validate_dataset(df_complaints)

    # Save to CSV
    df_complaints.to_csv(args.output, index=False)
    print(f"Successfully saved {len(df_complaints):,} rows to '{args.output}'.\n")

    # Display dataset preview and quick statistics
    print("Dataset Summary:")
    print("-" * 50)
    print(f"Dimensions: {df_complaints.shape[0]} rows x {df_complaints.shape[1]} columns")
    print("\nStatus Distribution:")
    print(df_complaints["Status"].value_counts(dropna=False))
    print("\nMissing Values per Column:")
    print(df_complaints.isna().sum())
    print("\nSample Records (First 5):")
    print(df_complaints.head())
