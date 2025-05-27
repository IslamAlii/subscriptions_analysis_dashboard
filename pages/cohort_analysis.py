from utils.data_utils import st, pd, aov, current_day, load_data, get_percentage_pivot_for_same_cohort

st.set_page_config(page_title="iSchool Dashboard", layout="wide", page_icon="📊")

st.title("📊 Subscription Analysis")

students_df, subscriptions_df = load_data()

# Sort by student_id and created_at
subscriptions_df = subscriptions_df.sort_values(by=['student_id', 'created_at'])

# Assign subscription number using cumcount (starts from 0, so add 1)
subscriptions_df['subscription_count'] = subscriptions_df.groupby('student_id').cumcount()
subscriptions_df['subscribed_at'] = subscriptions_df.groupby('student_id')['created_at'].transform('min')
subscriptions_df = subscriptions_df.sort_values(by=['student_id', 'expired_at'])

# Prepare total subscriptions
total_subs_df = subscriptions_df.copy()
total_subs_df['cohort_month'] = total_subs_df['expired_at']
total_subs_df['months_count_from_subscription'] = (((total_subs_df['expired_at'] - total_subs_df['subscribed_at']).dt.days) / 30).round()
total_subs_df = total_subs_df[total_subs_df['cohort_month'] < current_day]
total_subs_df['cohort_month'] = total_subs_df['expired_at'].dt.to_period('M')

# Prepare renewed subscriptions
renewed_df = subscriptions_df.copy()
renewed_df['cohort_month'] = renewed_df.groupby('student_id')['expired_at'].shift(1)
renewed_df['months_count_from_subscription'] = (((renewed_df['cohort_month'] - renewed_df['subscribed_at']).dt.days) / 30).round()
renewed_df = renewed_df[renewed_df['cohort_month'] < current_day]
renewed_df['cohort_month'] = renewed_df['cohort_month'].dt.to_period('M')

# Prepare churned subscriptions
churned_df = subscriptions_df.copy()
churned_df = churned_df.groupby('student_id').last().reset_index()
churned_df = churned_df[churned_df['expired_at'] < current_day]
churned_df['cohort_month'] = churned_df['expired_at'].dt.to_period('M')
churned_df['months_count_from_subscription'] = (((churned_df['expired_at'] - churned_df['subscribed_at']).dt.days) / 30).round()

# Pivot table for total subscriptions
total_subs_pivot = total_subs_df.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='months_count_from_subscription',
    aggfunc='count'
)

# Pivot table for renewed subscriptions
renewed_pivot = renewed_df.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='months_count_from_subscription',
    aggfunc='count'
)
# Align with total_subs_pivot and fill only meaningful NaNs with 0, keeping structural NaNs intact
# renewed_pivot = renewed_pivot.reindex(index=total_subs_pivot.index, columns=total_subs_pivot.columns)
# renewed_pivot = renewed_pivot.where(total_subs_pivot.isna(), renewed_pivot.fillna(0))

# Pivot table for renewed revenue
renewed_revenue_pivot = renewed_df.pivot_table(
    values='paid_amount',
    index='cohort_month',
    columns='months_count_from_subscription',
    aggfunc='sum'
)

# Pivot table for churned subscriptions
churned_pivot = churned_df.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='months_count_from_subscription',
    aggfunc='count'
)

# Pivot table for churned AOV projection
churned_aov_projection_pivot = (churned_pivot * aov).applymap(lambda x: int(x) if pd.notna(x) else None)

# Merge student metadata and currency (if in subscriptions_df)
subs_with_info = total_subs_df.merge(
    students_df[['id', 'country', 'last_or_current_grade_and_module']],
    left_on='student_id',
    right_on='id',
    how='left'
)

# --- Country Pivot ---
country_pivot = subs_with_info.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='country',
    aggfunc='count',
    fill_value=0
)
country_pivot = country_pivot[country_pivot.sum().sort_values(ascending=False).index]

# --- Grade and Module Pivot ---
grade_module_pivot = subs_with_info.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='last_or_current_grade_and_module',
    aggfunc='count',
    fill_value=0
)
grade_module_pivot = grade_module_pivot[grade_module_pivot.sum().sort_values(ascending=False).index]

# --- Currency Pivot ---
currency_pivot = subs_with_info.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='currency',
    aggfunc='count',
    fill_value=0
)
currency_pivot = currency_pivot[currency_pivot.sum().sort_values(ascending=False).index]

# ✅ Percentage toggle
show_percentage = st.sidebar.checkbox("Show Percentage Tables", value=False)

# Layout columns
col1, col2 = st.columns([1, 1])
with col1:
    cohort_counts = total_subs_df.groupby('cohort_month')['student_id'].nunique()
    st.subheader("👥 Cohort Breakdown by Student Count")
    st.write(cohort_counts)

# --- Country ---
st.subheader("🌍 Country Distribution by Cohort Month (Sorted)")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(country_pivot))
else:
    st.write(country_pivot)

# --- Grade & Module ---
st.subheader("🎓 Grade and Module Distribution by Cohort Month (Sorted)")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(grade_module_pivot))
else:
    st.write(grade_module_pivot)

# --- Currency ---
st.subheader("💱 Currency Distribution by Cohort Month (Sorted)")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(currency_pivot))
else:
    st.write(currency_pivot)

# --- Retention Achieved ---
st.subheader("🔁 Retention Achieved")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(renewed_pivot))
else:
    st.write(renewed_pivot)

# --- Churned Subscriptions ---
st.subheader("📉 Churned Subscriptions")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(churned_pivot))
else:
    st.write(churned_pivot)

# --- Renewed Revenue ---
st.subheader("💰 Renewed Revenue by Cohort Month")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(renewed_revenue_pivot))
else:
    st.write(renewed_revenue_pivot)

# --- Churned Revenue ---
st.subheader("💸 Churned AOV projection")
if show_percentage:
    st.write(get_percentage_pivot_for_same_cohort(churned_aov_projection_pivot))
else:
    st.write(churned_aov_projection_pivot)

# Testing Purpose
subscription_number_pivot = renewed_df.pivot_table(
    values='student_id',
    index='cohort_month',
    columns='subscription_count',
    aggfunc='count'
)
st.subheader("🛠️ Testing Purpose")
st.write(subscription_number_pivot)