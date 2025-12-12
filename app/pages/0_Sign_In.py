import sys
import os
# Add project root to Python path so "app.*" imports work when Streamlit loads pages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import mysql.connector
from app.db import get_connection, DEMO_MODE
from datetime import datetime


def get_fiscal_year():
    """
    Calculate the fiscal year based on current date.
    Fiscal year starts July 1st.
    Example: July 1, 2024 - June 30, 2025 = FY 2025
    """
    now = datetime.now()
    if now.month >= 7:  # July or later
        return now.year + 1
    else:
        return now.year


def get_fiscal_quarter():
    """
    Calculate the fiscal quarter based on current date.
    Fiscal year starts July 1st.
    Q1 = Jul-Sep, Q2 = Oct-Dec, Q3 = Jan-Mar, Q4 = Apr-Jun
    """
    now = datetime.now()
    month = now.month
    
    if 7 <= month <= 9:  # July-September
        return 1
    elif 10 <= month <= 12:  # October-December
        return 2
    elif 1 <= month <= 3:  # January-March
        return 3
    else:  # April-June (4-6)
        return 4


def insert_sign_in(name, email):
    """
    Insert a sign-in record into the database.
    
    In DEMO_MODE:
        Returns a fake sign-in ID.
    
    Otherwise:
        Inserts into sign_ins table with name, email, timestamp, fiscal year, and quarter.
    
    Returns:
        sign_in_id (int) on success
        None on failure
    """
    if DEMO_MODE:
        return 9999
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        fiscal_year = get_fiscal_year()
        fiscal_quarter = get_fiscal_quarter()
        
        cursor.execute(
            """
            INSERT INTO sign_ins (name, email, fiscal_year, fiscal_quarter)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, fiscal_year, fiscal_quarter)
        )
        
        sign_in_id = cursor.lastrowid
        conn.commit()
        return sign_in_id
    
    except mysql.connector.Error as e:
        conn.rollback()
        st.error(f"Error recording sign-in: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()


def render_sign_in_page():
    """
    Renders the Makerspace sign-in page.
    
    This simple page allows anyone entering the Makerspace to:
    • Sign in with their name and email
    • Get tracked for involvement metrics
    • Support fiscal year reporting
    """
    st.title("🖊️ Makerspace Sign-In")
    
    if DEMO_MODE:
        st.info("Demo mode: sign-ins are simulated and no real data is stored.")
    
    st.write(
        """
        Welcome to the Creighton Library Makerspace!
        
        Please sign in below to help us track involvement and usage.
        This information is used for reporting to administration.
        """
    )
    
    # Simple sign-in form
    with st.form("sign_in_form"):
        st.subheader("Sign In")
        
        name = st.text_input("Full Name (required)", placeholder="John Doe")
        email = st.text_input("Creighton Email (required)", placeholder="johndoe@creighton.edu")
        
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
    
    if submitted:
        # Validate required fields
        if not name or not email:
            st.error("Please fill in both name and email.")
            return
        
        # Basic email validation
        if "@" not in email or "." not in email:
            st.warning("Please enter a valid email address.")
            return
        
        # Record sign-in
        sign_in_id = insert_sign_in(name.strip(), email.strip())
        
        if sign_in_id is not None:
            st.success(f"✅ Thank you for signing in, {name}!")
            st.balloons()
        else:
            st.error("There was a problem recording your sign-in. Please try again.")
    
    # Display current fiscal year info
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Current Fiscal Year: FY {get_fiscal_year()}")
    with col2:
        st.caption(f"Current Fiscal Quarter: Q{get_fiscal_quarter()}")


if __name__ == "__main__":
    render_sign_in_page()
