import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Create and return a MySQL connection using Streamlit secrets.

    I expect .streamlit/secrets.toml to have:

    [db]
    host = "127.0.0.1"
    user = "root"
    password = "pass123"
    database = "makerspace_db_final"
    port = 3307
    """
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