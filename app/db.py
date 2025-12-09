import streamlit as st
import mysql.connector
from mysql.connector import Error

# Determine demo mode from secrets
DEMO_MODE = False
try:
    DEMO_MODE = bool(st.secrets["app"].get("demo_mode", False))
except Exception:
    DEMO_MODE = False


def get_connection():
    """
    Real DB connection unless demo mode is enabled.
    """
    if DEMO_MODE:
        # Returning None signals "no real DB available"
        return None

    try:
        conn = mysql.connector.connect(
            host=st.secrets["db"]["host"],
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            database=st.secrets["db"]["database"],
            port=st.secrets["db"]["port"],
        )
        return conn

    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None