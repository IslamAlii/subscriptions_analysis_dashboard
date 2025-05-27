# 📊 Subscriptions Analysis Dashboard

[🔗 Live App](https://subscriptionsanalysisdashboard-gspuffpbafa4npighs3rd5.streamlit.app/cohort_analysis)

A powerful, interactive dashboard built using **Streamlit** to analyze subscription trends, revenue metrics, user churn, and retention performance for a learning platform.

---

## 🔍 Features

### 🚀 Dashboard Overview
- **Revenue Metrics (EGP)**: Total, Net, Remaining, and Refunded revenue.
- **Student Metrics**: Breakdown of student subscription status (Active, Inactive, Pending, Free, Expired, Canceled).
- **Business KPIs**: Total students, ARPU, and Churn Rate.
- **Trends Visualization**: Year-over-year revenue and user activity trends using Altair charts.

### 🧮 Cohort Analysis (Filter Viewer)
- Visual exploration of **Retention** and **Churn** across different cohorts.
- Filter by:
  - Subscription type (`Retention` or `Churn`)
  - Specific cohort month
  - Duration since initial subscription
- Display breakdowns by:
  - Country
  - Plan
  - Grade, Instructor, and Lost Reasons (for churned users)
- Pivot tables for:
  - Renewed revenue
  - Churned subscriptions
  - Churned ARPU projections

---

## 🛠️ Tech Stack

- **Python**
- **Pandas** & **Altair** – Data processing and visualization
- **Streamlit** – Interactive dashboard framework
- **Parquet** – Efficient data storage format

