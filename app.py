import streamlit as st
import plotly.express as px
import pandas as pd
from services.auth import authenticate_user, get_user_accessible_category
from services.analytics import (
    calculate_nps, 
    get_satisfaction_distribution, 
    get_top_products, 
    get_worst_products,
    get_all_categories
)
from services.ai_summary import summarize_negative_reviews
from services.ai_router import parse_query_intent
from services.reports import save_report, get_user_reports
from database.db import setup_database

st.set_page_config(page_title="AI Product Review Analytics", layout="wide")

# ... (omitting unchanged init block because we're just injecting the import at the top)


# setup session state
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

setup_database()
init_session()

# login screen
def login_page():
    st.title("Review Analytics System - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                # print(f"login ok for {username}")
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    st.info("Demo Accounts:\n- admin_user (adminpass)\n- analyst_electronics (analystpass)")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# dashboard view
def show_dashboard():
    user = st.session_state.user
    role = user['role']
    
    st.title(f"Dashboard - Welcome, {user['username']} ({role.capitalize()})")
    st.button("Logout", on_click=logout)
    
    st.markdown("---")
    
    # handle role constraints
    assigned_category = get_user_accessible_category(user)
    selected_category = None
    
    st.header("Analytics Filters")
    if role == "analyst":
        st.info(f"You are restricted to the **{assigned_category}** category.")
        selected_category = assigned_category
    else:
        # Admin can choose any category, or 'All'
        all_cats = ["All Categories"] + get_all_categories()
        choice = st.selectbox("Select Category", all_cats)
        if choice != "All Categories":
            selected_category = choice
            
    st.markdown("---")
    st.header("Executive Summary")
    
    # nps scoreboard
    nps_data = calculate_nps(selected_category)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Net Promoter Score (NPS)", value=f"{nps_data['nps']}", delta=None)
        st.caption(f"Based on {nps_data['total']} reviews")
        st.write(f"- Promoters: {nps_data['promoters']}")
        st.write(f"- Passives: {nps_data['passives']}")
        st.write(f"- Detractors: {nps_data['detractors']}")
        
    # satisfaction bar chart
    with col2:
        sat_data = get_satisfaction_distribution(selected_category)
        df_sat = pd.DataFrame(list(sat_data.items()), columns=['Sentiment', 'Count'])
        fig_sat = px.bar(
            df_sat, 
            x='Sentiment', 
            y='Count', 
            color='Sentiment',
            title="Satisfaction Distribution",
            color_discrete_map={"Happy": "green", "Neutral": "gray", "Unhappy": "red"}
        )
        st.plotly_chart(fig_sat, use_container_width=True)
        
    st.markdown("---")
    
    # show top and worst products
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Top Products (Min 10 reviews)")
        # rankings only work if we aren't filtering by category yet
        if selected_category:
            st.warning("Product rankings are only available when viewing All Categories.")
        else:
            top_df = pd.DataFrame(get_top_products(limit=5, min_reviews=10))
            st.dataframe(top_df, hide_index=True, use_container_width=True)
            
    with col4:
        st.subheader("Worst Products (Min 10 reviews)")
        if not selected_category:
            worst_df = pd.DataFrame(get_worst_products(limit=5, min_reviews=10))
            st.dataframe(worst_df, hide_index=True, use_container_width=True)

# report generation page
def show_reports():
    user = st.session_state.user
    st.title("Traceability & Reports")
    
    st.header("Run a Query")
    st.write("Ask any question naturally. E.g., 'What is the NPS for Books?', 'Show top 5 products', or 'Why are people unhappy?'")
    query = st.text_input("Enter your query:", placeholder="e.g. Why are customers unhappy?")
    
    # security check: analyst assigned role overrides the query intent
    role_cat_limit = get_user_accessible_category(user)
    
    if st.button("Run Query & Save"):
        if not query.strip():
            st.warning("Please enter a query.")
            return
            
        with st.spinner("AI Router is interpreting your intent..."):
            intent = parse_query_intent(query)
            
        if "error" in intent:
            st.error(f"System Error: {intent['error']}")
            return
            
        action = intent.get("action", "unknown")
        
        # override llm if user is an analyst
        effective_category = role_cat_limit if role_cat_limit else intent.get("category")
        
        # Safely parse limit
        try:
            limit = int(intent.get("limit")) if intent.get("limit") else 5
        except (ValueError, TypeError):
            limit = 5
            
        res = None
        
        if action == "calculate_nps":
            res = {"type": "nps", "data": calculate_nps(effective_category)}
            st.success(f"NPS Calculated for {effective_category or 'All Categories'}!")
            st.json(res["data"])
            
        elif action == "satisfaction_distribution":
            res = {"type": "satisfaction", "data": get_satisfaction_distribution(effective_category)}
            st.success(f"Satisfaction Distribution for {effective_category or 'All Categories'}!")
            st.json(res["data"])
            
        elif action == "top_products":
            if role_cat_limit:
                 st.error(f"Cannot run global ranking queries. You are restricted to {role_cat_limit}.")
            else:
                 res = {"type": "top_products", "data": get_top_products(limit=limit)}
                 st.success(f"Top {limit} Products Found!")
                 st.dataframe(res["data"])
                 
        elif action == "worst_products":
             if role_cat_limit:
                 st.error(f"Cannot run global ranking queries. You are restricted to {role_cat_limit}.")
             else:
                 res = {"type": "worst_products", "data": get_worst_products(limit=limit)}
                 st.success(f"Worst {limit} Products Found!")
                 st.dataframe(res["data"])
                 
        elif action == "complaint_summary":
            with st.spinner("Generating AI Summary by analyzing negative reviews..."):
                summary_text = summarize_negative_reviews(effective_category)
                res = {"type": "ai_summary", "data": summary_text}
                st.success(f"AI Summary Generated for {effective_category or 'All Categories'}!")
                val = res["data"]
                if "Unable" in val or "No negative" in val:
                    st.warning(val)
                else:
                    st.info(val)
                    
        else:
            st.warning("Query intent not recognized. I only know about NPS, satisfaction, top/worst products, and complaint summaries.")
            
        # save report to db
        if res:
            save_report(user['id'], query, res)
            st.info("Report saved to history.")
            
    st.markdown("---")
    st.header("Report History")
    
    # admins see all history, analysts see their own
    is_admin = (user['role'] == 'admin')
    reports = get_user_reports(user['id'], is_admin=is_admin)
    
    if not reports:
        st.write("No reports found.")
    else:
        for r in reports:
            with st.expander(f"{r['timestamp']} | Query: {r['query_text']}"):
                st.write(f"**Report ID:** {r['id']} | **User ID:** {r['user_id']}")
                st.json(r['result_summary'])

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # Navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to:", ["Dashboard", "Reports View"])
        
        if page == "Dashboard":
            show_dashboard()
        else:
            show_reports()

if __name__ == "__main__":
    main()
