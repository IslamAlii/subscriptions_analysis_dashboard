import pandas as pd
from pandas.tseries.offsets import DateOffset
import streamlit as st
import altair as alt
import ast
from datetime import datetime
import pytz


aov = 5900
cairo = pytz.timezone("Africa/Cairo")
current_day = datetime.now(cairo).replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data
def load_data():
    students_df = pd.read_parquet('students_sample.parquet')
    subscriptions_df = pd.read_parquet('subscriptions_sample.parquet')

    return students_df, subscriptions_df

def get_subscriptions_by_currency(subscriptions_df, currency):
    return subscriptions_df[subscriptions_df['currency'] == currency]


def format_currency(value, currency='egp'):
    symbol_map = {
        'egp': 'EGP', 'USD': '$', 'EUR': '€', 'AED': 'AED',
    }
    symbol = symbol_map.get(currency, currency)
    return f"{symbol} {int(value):,}"


def compute_egp_financial_metrics (subscriptions_df):
    egp_subs = get_subscriptions_by_currency(subscriptions_df, 'egp')

    return {
        'total_revenue': egp_subs['paid_amount'].sum() + egp_subs['remaining_amount'].sum(),
        'net_revenue': egp_subs['paid_amount'].sum() - egp_subs['refund_amount'].sum(),
        'remaining_amount': egp_subs['remaining_amount'].sum(),
        'refunded_amount': egp_subs['refund_amount'].sum()
    }

def compute_total_students_count(students_df):
    total_students_count = students_df['id'].shape[0]

    return total_students_count

def compute_free_students_count(students_df):
    free_students = students_df[students_df['status'] == 'free'].shape[0]

    return free_students

def compute_non_churned_students_count(students_df):
    return{
        'active': students_df[students_df['status'] == 'active'].shape[0],
        'inactive': students_df[students_df['status'] == 'pending_schedule'].shape[0],
        'pending': students_df[students_df['status'] == 'pending'].shape[0],
    }

def compute_churned_students_count(students_df):
    return{
        'expired': students_df[students_df['status'] == 'expired'].shape[0],
        'canceled': students_df[students_df['status'] == 'canceled'].shape[0],
    }

def compute_churn_rate(students_df):
    non_churned_students_status = compute_non_churned_students_count(students_df)
    churned_students_status = compute_churned_students_count(students_df)

    total_paid_students = non_churned_students_status['active'] + non_churned_students_status['inactive'] + non_churned_students_status['pending'] + churned_students_status['expired'] + churned_students_status['canceled']
    total_churned_students = churned_students_status['expired'] + churned_students_status['canceled']
    churn_rate = total_churned_students / total_paid_students * 100

    return churn_rate

def compute_arpu_for_egp(subscriptions_df):
    egp_subs = get_subscriptions_by_currency(subscriptions_df, 'egp')

    total_revenue = egp_subs['paid_amount'].sum() + egp_subs['remaining_amount'].sum()
    total_users = egp_subs['student_id'].nunique()
    arpu = total_revenue / total_users

    return arpu

def plot_yearly_revenue_trends(currency_subs: pd.DataFrame, currency):
    # Calculate yearly metrics
    yearly_total_revenue = currency_subs.groupby('created_at_year')[['paid_amount', 'remaining_amount']].sum().sum(axis=1)
    yearly_net_revenue = (currency_subs.groupby('created_at_year')[['paid_amount', 'refund_amount']].sum().eval('paid_amount - refund_amount')).reindex(yearly_total_revenue.index).fillna(0)
    yearly_refund_amount = (currency_subs.groupby('refund_at_year')['refund_amount'].sum()).reindex(yearly_total_revenue.index).fillna(0)

    # Create DataFrame for metrics
    yearly_metrics = pd.DataFrame({
        'Year': yearly_total_revenue.index,
        'Total Revenue': yearly_total_revenue.values,
        'Net Revenue': yearly_net_revenue.values,
        'Refund Amount': yearly_refund_amount.values
    })

    # Melt the data to long format for Altair charting
    melted_data = yearly_metrics.melt(
        id_vars=['Year'],
        value_vars=['Total Revenue', 'Net Revenue', 'Refund Amount'],
        var_name='Category',
        value_name='Amount'
    )

    # Format the Amount for tooltips
    melted_data['Formatted Amount'] = melted_data['Amount'].apply(lambda x: f"{currency} {x:,.0f}")

    # Display subheader and intro
    st.subheader(f"📈 {currency}: Yearly Revenue Trends")
    st.markdown(f"""
    This chart shows the yearly trends for **{currency} transactions only**:
    - 💰 Total Revenue
    - 📊 Net Revenue
    - ↪️ Refund Amount
    """)

    # Define custom order for categories
    category_order = ['Total Revenue', 'Net Revenue', 'Refund Amount']

    # Create interactive Altair chart
    selection = alt.selection_point(fields=['Category'], bind='legend', empty='all')

    line_chart = alt.Chart(melted_data).mark_line(point=True).encode(
        x=alt.X('Year:O', title="Year"),
        y=alt.Y('Amount:Q', title=f"Amount ({currency})"),
        color=alt.Color('Category:N', title="Category", sort=category_order,
                        legend=alt.Legend(labelFontSize=12, labelFont='Arial', labelLimit=200, titlePadding=15)),
        tooltip=['Year', 'Category', 'Formatted Amount'],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    ).add_params(selection)

    # Show the chart
    st.altair_chart(line_chart, use_container_width=True)

def plot_yearly_user_trends(students_df: pd.DataFrame, subscriptions_df: pd.DataFrame):
    activated_subs = subscriptions_df[
    subscriptions_df['expired_at'] < subscriptions_df['activated_at'] + DateOffset(months=18)
    ]
    
    # Explode to one row per active year per student
    activated_subs['active_years'] = activated_subs['active_years'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    exploded = activated_subs[['student_id', 'active_years']].explode('active_years').drop_duplicates()

    # Calculate yearly metrics
    yearly_registered_students = students_df.groupby('created_at_year')['id'].count()
    yearly_active_students = exploded.groupby('active_years')['student_id'].nunique()
    yearly_registered_free_students = students_df[students_df['signed_up_free'] == 1].groupby('created_at_year')['id'].count()

    # Build DataFrame
    yearly_metrics = pd.DataFrame({
        'Year': yearly_registered_students.index,
        'Total Registered Students': yearly_registered_students,
        'Active Students': yearly_active_students,
        'Free Registered Students': yearly_registered_free_students
    }).fillna(0)

    # Melt for visualization
    melted_data = yearly_metrics.reset_index().melt(
        id_vars=['Year'],
        value_vars=['Total Registered Students', 'Active Students', 'Free Registered Students'],
        var_name='Category',
        value_name='Count'
    )

    melted_data['Formatted Count'] = melted_data['Count'].apply(lambda x: f"{x:,.0f}")

    # Subheader and explanation
    st.subheader("📊 User Trends Over Time")
    st.markdown("""
    This chart shows the yearly trends for users:
    - 📈 Total Registered Users
    - 🔥 Active Users
    - 🚀 Free Registered Users
    """)

    # Custom order for legend
    category_order = ['Total Registered Students', 'Active Students', 'Free Registered Students']

    # Chart
    selection = alt.selection_point(fields=['Category'], bind='legend', empty='all')

    line_chart = alt.Chart(melted_data).mark_line(point=True).encode(
        x=alt.X('Year:O', title="Year"),
        y=alt.Y('Count:Q', title="Count"),
        color=alt.Color('Category:N', title="Category", sort=category_order,
                        legend=alt.Legend(labelFontSize=12, labelFont='Arial', labelLimit=200, titlePadding=15)),
        tooltip=['Year', 'Category', 'Formatted Count'],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    ).add_params(selection)

    st.altair_chart(line_chart, use_container_width=True)

def get_percentage_pivot_for_same_cohort(pivot_table):
   return (pivot_table.apply(lambda x: ((x / x.sum()) * 100).round(2), axis=1)).applymap(
    lambda x: f"{x}%"
    if pd.notna(x)
    else None
)