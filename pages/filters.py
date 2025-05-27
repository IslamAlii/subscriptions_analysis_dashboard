from utils.data_utils import st, pd, aov, current_day, load_data

st.set_page_config(page_title="Filter Viewer", layout="wide", page_icon="🧮")
st.title("🧮 Filter Viewer")

students_df, subscriptions_df = load_data()

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

# Sidebar filters
st.sidebar.subheader("Filters")
subscription_type = st.sidebar.selectbox('Select Subscription Type', ['Retention', 'Churn'], index=0)
cohort_months_sorted = sorted(total_subs_df['cohort_month'].unique())
cohort_month = st.sidebar.selectbox('Select Cohort Month', ['All Cohort Months'] + cohort_months_sorted, index=0)
months_count_sorted = sorted(total_subs_df['months_count_from_subscription'].unique())
months_count = st.sidebar.selectbox('Select Months Count from Subscription', ['All Months in Cohort'] + months_count_sorted, index=0)

# Filter data
if subscription_type == 'Retention':
    # If "All Cohort Months" is selected, remove the cohort_month filter
    if cohort_month == 'All Cohort Months':
        filtered_data = renewed_df
    else:
        filtered_data = renewed_df[renewed_df['cohort_month'] == cohort_month]
    
    # If "All Months in Cohort" is selected, remove the months_count filter
    if months_count == 'All Months in Cohort':
        filtered_data = filtered_data
    else:
        filtered_data = filtered_data[filtered_data['months_count_from_subscription'] == months_count]
    
    # filtered_data = filtered_data[['student_id', 'subscribed_at', 'expired_at', 'currency', 'paid_amount', 'plan']]

    st.subheader(f"📊 Retention for Cohort {cohort_month} - Months Count {months_count}")
    if filtered_data.empty:
        st.info("No data available for this filter combination.")
    else:
        st.write(filtered_data[['student_id', 'subscribed_at', 'expired_at', 'currency', 'paid_amount', 'plan']])

        # Country distribution for retention
        country_table = students_df[students_df['id'].isin(filtered_data['student_id'])] \
            .groupby('country')['id'].count().reset_index(name='count')
        country_table = country_table.sort_values(by='count', ascending=False)
        st.write("🎓 Country Distribution")
        st.write(country_table.set_index('country').T)

        # Currency distribution for retention
        currency_table = filtered_data.groupby('currency')['student_id'].count().reset_index(name='count')
        currency_table = currency_table.sort_values(by='count', ascending=False)
        st.write("💰 Currency Distribution")
        st.write(currency_table.set_index('currency').T)

        # Plan distribution for retention
        currency_table = filtered_data.groupby('plan')['student_id'].count().reset_index(name='count')
        currency_table = currency_table.sort_values(by='count', ascending=False)
        st.write("🗂️ Plan Distribution")
        st.write(currency_table.set_index('plan').T)

        renewed_pivot = filtered_data.pivot_table(
            values='student_id',
            index='cohort_month',
            columns='months_count_from_subscription',
            aggfunc='count'
        )
        st.subheader("🔁 Retention Achieved")
        st.write(renewed_pivot)
    
        renewed_revenue_pivot = filtered_data.pivot_table(
            values='paid_amount',
            index='cohort_month',
            columns='months_count_from_subscription',
            aggfunc='sum'
        )
        st.subheader("💰 Renewed Revenue")
        st.write(renewed_revenue_pivot)

else:
    # For churned data, same logic applies
    if cohort_month == 'All Cohort Months':
        filtered_data = churned_df
    else:
        filtered_data = churned_df[churned_df['cohort_month'] == cohort_month]

    if months_count == 'All Months in Cohort':
        filtered_data = filtered_data
    else:
        filtered_data = filtered_data[filtered_data['months_count_from_subscription'] == months_count]

    # filtered_data = filtered_data[['student_id', 'subscribed_at', 'expired_at', 'currency']]

    st.subheader(f"📊 Churned for Cohort {cohort_month} - Months Count {months_count}")
    if filtered_data.empty:
        st.info("No data available for this filter combination.")
    else:
        st.write(filtered_data[['student_id', 'subscribed_at', 'expired_at', 'currency']])

        # Country distribution for churn
        country_table = students_df[students_df['id'].isin(filtered_data['student_id'])] \
            .groupby('country')['id'].count().reset_index(name='count')
        country_table = country_table.sort_values(by='count', ascending=False)
        st.write("🎓 Country Distribution")
        st.write(country_table.set_index('country').T)

        # Currency distribution for churn
        currency_table = filtered_data.groupby('currency')['student_id'].count().reset_index(name='count')
        currency_table = currency_table.sort_values(by='count', ascending=False)
        st.write("💰 Currency Distribution")
        st.write(currency_table.set_index('currency').T)

        # Grades distribution for churn
        country_table = students_df[students_df['id'].isin(filtered_data['student_id'])] \
            .groupby('last_or_current_grade_and_module')['id'].count().reset_index(name='count')
        country_table = country_table.sort_values(by='count', ascending=False)
        st.write("🎓 Grade Distribution")
        st.write(country_table.set_index('last_or_current_grade_and_module').T)

        # Instructor distribution for churn
        country_table = students_df[students_df['id'].isin(filtered_data['student_id'])] \
            .groupby('last_or_current_tutor')['id'].count().reset_index(name='count')
        country_table = country_table.sort_values(by='count', ascending=False)
        st.write("👨‍🏫 Instructor Breakdown")
        st.write(country_table.set_index('last_or_current_tutor').T)

        # Lost reason distribution for churn
        country_table = students_df[students_df['id'].isin(filtered_data['student_id'])] \
            .groupby('lost_reason')['id'].count().reset_index(name='count')
        country_table = country_table.sort_values(by='count', ascending=False)
        st.write("🔍 Lost Reason Breakdown")
        st.write(country_table.set_index('lost_reason').T)

        # Pivot table for churned subscriptions
        churned_pivot = filtered_data.pivot_table(
            values='student_id',
            index='cohort_month',
            columns='months_count_from_subscription',
            aggfunc='count'
        )
        st.subheader("📉 Churned Subscriptions")
        st.write(churned_pivot)

        # Pivot table for churned AOV projection
        churned_aov_projection_pivot = (churned_pivot * aov).applymap(lambda x: int(x) if pd.notna(x) else None)
        st.subheader("💸 Churned AOV projection")
        st.write(churned_aov_projection_pivot)
