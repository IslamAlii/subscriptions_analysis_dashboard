from utils.data_utils import st, load_data, format_currency, get_subscriptions_by_currency, compute_egp_financial_metrics, compute_total_students_count, compute_free_students_count, compute_non_churned_students_count, compute_churned_students_count, compute_churn_rate, compute_arpu_for_egp, plot_yearly_revenue_trends, plot_yearly_user_trends

st.set_page_config(page_title="Subscriptions Analysis Dashboard", layout="wide", page_icon="📊")

st.title("📊 Dashboard Overview")

students_df, subscriptions_df = load_data()
egp_subs = get_subscriptions_by_currency(subscriptions_df, 'egp')

# Revenue Metrics
st.markdown("<style>div.row-widget.stColumn {margin-top: 20px;}</style>", unsafe_allow_html=True)
st.subheader("Revenue Metrics - EGP Only")
egp_financial_metrics  = compute_egp_financial_metrics (subscriptions_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue 💰", format_currency(egp_financial_metrics['total_revenue']))
col2.metric("Net Revenue 📈", format_currency(egp_financial_metrics['net_revenue']))
col3.metric("Remaining Amount ⏳", format_currency(egp_financial_metrics['remaining_amount']))
col4.metric("Refund Amount ↩️", format_currency(egp_financial_metrics['refunded_amount']))

# Student Metrics
st.markdown("<style>div.row-widget.stColumn {margin-top: 20px;}</style>", unsafe_allow_html=True)
st.subheader("Student Subscription Status")
total_students_count = compute_total_students_count(students_df)
free_students_count = compute_free_students_count(students_df)
non_churned_students_counts = compute_non_churned_students_count(students_df)
churned_students_counts = compute_churned_students_count(students_df)

col5, col6, col7 = st.columns(3)
col5.metric("✅ Active Students", non_churned_students_counts['active'])
col6.metric("⚠️ Inactive Students", non_churned_students_counts['inactive'])
col7.metric("⏳ Pending Students", non_churned_students_counts['pending'])

col8, col9, col10 = st.columns(3)
col8.metric("❌ Expired Students", churned_students_counts['expired'])
col9.metric("🚫 Canceled Students", churned_students_counts['canceled'])
col10.metric("🆓 Free Students", free_students_count)

# Business Snapshot
st.markdown("<style>div.row-widget.stColumn {margin-top: 20px;}</style>", unsafe_allow_html=True)
st.subheader('🚀 Business Snapshot')
col11, col12, col13 =  st.columns(3)
col11.metric("👥 Total Students", total_students_count)
col12.metric("💵 ARPU",  format_currency(compute_arpu_for_egp(subscriptions_df)))
col13.metric("📉 Churn Rate",  f"{compute_churn_rate(students_df):.2f}%")


# Show time lines
st.markdown("<style>div.row-widget.stColumn {margin-top: 20px;}</style>", unsafe_allow_html=True)
plot_yearly_revenue_trends(egp_subs, 'EGP')

st.markdown("<style>div.row-widget.stColumn {margin-top: 20px;}</style>", unsafe_allow_html=True)
plot_yearly_user_trends(students_df, subscriptions_df)


