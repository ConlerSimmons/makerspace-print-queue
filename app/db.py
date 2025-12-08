import streamlit as st
import mysql.connector
from mysql.connector import Error

# I use this flag to switch between real DB mode and demo/sample mode.
DEMO_MODE = bool(st.secrets.get("demo_mode", False))


def get_connection():
    """
    Create and return a MySQL connection using Streamlit secrets.

    I expect .streamlit/secrets.toml (or Streamlit Cloud secrets) to have:

    [db]
    host = "127.0.0.1"
    user = "root"
    password = "pass123"
    database = "makerspace_db_final"
    port = 3307

    When DEMO_MODE is True, I skip making a real database connection and
    return None instead. The calling code is responsible for handling
    the demo behavior.
    """
    if DEMO_MODE:
        # In demo mode I do not talk to a live database.
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