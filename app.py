import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Gym Management Dashboard",
    page_icon="🏋️",
    layout="wide"
)

st.title("🏋️ Gym Management Dashboard")

# ---------------- GOOGLE SHEET INPUT ----------------
sheet_id = st.text_input(
    "📄 Enter Google Sheet ID",
    help="Copy from the Google Sheet URL"
)

if not sheet_id:
    st.info("👆 Enter Google Sheet ID to load data")
    st.stop()

csv_url = f"https://docs.google.com/spreadsheets/d/1lcUKNcagCEom59UQ9gGahuJVWOpXLb3NqmPIaATJ4sc/export?format=csv"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df["join_date"] = pd.to_datetime(
    df["join_date"],
    dayfirst=True,
    errors="coerce")

    df["expiry_date"] = pd.to_datetime(
        df["expiry_date"],
        dayfirst=True,
        errors="coerce")

    return df

df = load_data(csv_url)

today = datetime.today()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Search User",
        "Earnings (Date Range)",
        "Pending / Expired Users"
    ]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.subheader("📊 Gym Overview")

    today = pd.to_datetime(datetime.today().date())
    current_month = today.month
    current_year = today.year

    # Filters
    this_month_df = df[
        (df["join_date"].dt.month == current_month) &
        (df["join_date"].dt.year == current_year)
    ]

    this_month_earnings = this_month_df["amount_paid"].sum()
    new_users_this_month = len(this_month_df)
    total_users = len(df)

    expired_users = df[df["expiry_date"] < today]
    expired_count = len(expired_users)

    next_15_days = today + pd.Timedelta(days=15)
    expiring_soon = df[
        (df["expiry_date"] >= today) &
        (df["expiry_date"] <= next_15_days)
    ]
    expiring_soon_count = len(expiring_soon)

    # KPI Cards
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("💰 This Month Earnings", f"₹ {this_month_earnings}")
    c2.metric("🆕 New Users (This Month)", new_users_this_month)
    c3.metric("👥 Total Users", total_users)
    c4.metric("❌ Expired Users", expired_count)
    c5.metric("⏳ Expiring in 15 Days", expiring_soon_count)

    # Optional charts
    st.subheader("📈 Monthly Earnings")
    earnings = (
        df.groupby(df["join_date"].dt.to_period("M"))["amount_paid"]
        .sum()
        .reset_index()
    )
    earnings["join_date"] = earnings["join_date"].astype(str)

    fig = px.bar(
        earnings,
        x="join_date",
        y="amount_paid",
        labels={"join_date": "Month", "amount_paid": "Earnings"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⏳ Users Expiring in Next 15 Days")
    st.dataframe(expiring_soon, use_container_width=True)

# if menu == "Dashboard":
#     st.subheader("📊 Overview")

#     total_users = len(df)
#     active_users = df[df["expiry_date"] >= today].shape[0]
#     expired_users = df[df["expiry_date"] < today].shape[0]
#     total_revenue = df["amount_paid"].sum()

#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Total Users", total_users)
#     c2.metric("Active Users", active_users)
#     c3.metric("Expired Users", expired_users)
#     c4.metric("Total Revenue", f"₹ {total_revenue}")

#     st.subheader("📈 Monthly Earnings")
#     earnings = (
#         df.groupby(df["join_date"].dt.to_period("M"))["amount_paid"]
#         .sum()
#         .reset_index()
#     )
#     earnings["join_date"] = earnings["join_date"].astype(str)

#     fig = px.bar(
#         earnings,
#         x="join_date",
#         y="amount_paid",
#         labels={"join_date": "Month", "amount_paid": "Earnings"},
#     )
#     st.plotly_chart(fig, use_container_width=True)

# ---------------- SEARCH USER ----------------
elif menu == "Search User":
    st.subheader("🔍 Search User")

    search_by = st.selectbox(
        "Search By",
        ["user_id", "name", "mobile"]
    )

    search_value = st.text_input("Enter value")

    if search_value:
        result = df[
            df[search_by]
            .astype(str)
            .str.contains(search_value, case=False)
        ]

        st.write(f"### Results ({len(result)})")
        st.dataframe(result, use_container_width=True)

# ---------------- EARNINGS RANGE ----------------
elif menu == "Earnings (Date Range)":
    st.subheader("💰 Earnings by Time Range")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")

    filtered = df[
        (df["join_date"] >= pd.to_datetime(start_date)) &
        (df["join_date"] <= pd.to_datetime(end_date))
    ]

    st.metric("Total Earnings", f"₹ {filtered['amount_paid'].sum()}")
    st.dataframe(filtered, use_container_width=True)

# ---------------- PENDING / EXPIRED USERS ----------------
elif menu == "Pending / Expired Users":
    st.subheader("⏰ Pending / Expired Memberships")

    expired = df[df["expiry_date"] < today]

    st.write(f"### Expired Users ({len(expired)})")
    st.dataframe(expired, use_container_width=True)

    st.download_button(
        "⬇️ Download Expired Users",
        expired.to_csv(index=False),
        file_name="expired_users.csv",
        mime="text/csv"
    )
