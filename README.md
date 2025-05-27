# 📊 Subscriptions Analysis Dashboard

[🔗 Live App](https://subscriptionsanalysisdashboard-gspuffpbafa4npighs3rd5.streamlit.app/cohort_analysis)

An end-to-end analytics dashboard suite built with **Streamlit** to visualize, track, and forecast student subscription performance in an education platform. It includes multiple apps: an **overview dashboard**, **renewals/churn forecasting**, and a **filter-driven exploration tool**.
---

## 🚀 Overview

This suite allows you to:

- Analyze revenue, churn, and ARPU
- Forecast subscription renewals by cohort
- Filter and drill into subscription behaviors by type, cohort month, and duration
- Understand distributions across country, plan, grade/module, and instructor

---


## 🔍 Features
- Retention and churn metrics per cohort month  
- Pivot tables of student counts by country, grade/module, and currency  
- Revenue-based CLV forecasts  
- Monthly student cohort sizes and renewal patterns
- 📅 Monthly cohort-based analysis  
- 🔁 Retention achieved breakdown  
- 📉 Churned user insights  
- 💰 Renewed revenue visualization  
- 🌍 Country-based distribution  
- 🎓 Grade and module segmentation  
- ✅ Toggle to show percentages  
- 📊 Pivot tables for deep-dives 

---

## 🧰 Included Dashboards

### 1. **Dashboard Overview** (`app.py`)

> 📊 High-level performance metrics for business leaders

- Total Revenue, Net Revenue, Remaining & Refunded Amounts
- Active vs. Expired Student breakdown
- Churn rate, ARPU, and business snapshot
- Annual revenue and user growth trends

### 2. **Renewals Forecast Dashboard** (`00_subscriptions_analysis.py`)

> 🔁 Deep dive into cohort-based retention/churn

- Monthly cohort pivots for total, renewed, and churned subscriptions
- Country, Grade/Module, and Currency segmentation
- CLV projections using ARPU
- Renewed revenue and churned revenue estimates

### 3. **Filter Viewer** (`filters.py`)

> 🧮 Exploratory tool to slice subscription behavior

- Filters: subscription type (retention or churn), cohort month, months from subscription
- Plan, country, instructor, and lost reason breakdowns
- Pivot tables for renewals and churn with AOV projections

---

## 🛠️ Tech Stack

- **Python**
- **Pandas** & **Altair** – Data processing and visualization
- **Streamlit** – Interactive dashboard framework
- **Parquet** – Efficient data storage format

