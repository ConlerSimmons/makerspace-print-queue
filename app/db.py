import streamlit as st
import mysql.connector
from mysql.connector import Error

# ------------------------------------------------------------
# Determine whether the application should run in "demo mode".
#
# Demo mode is controlled entirely through secrets.toml:
#
#   [app]
#   demo_mode = true
#
# When demo mode is ON:
#   - The application does NOT connect to a real database.
#   - Pages that normally read/write MySQL instead use
#     placeholder or simulated data.
#
# If the key is missing or unreadable, demo_mode defaults to False.
# ------------------------------------------------------------
DEMO_MODE = False
try:
    DEMO_MODE = bool(st.secrets["app"].get("demo_mode", False))
except Exception:
    # If secrets are missing (e.g., when running in Streamlit Cloud
    # before secrets have been configured), fall back to normal mode.
    DEMO_MODE = False


def get_connection():
    """
    Create and return a MySQL database connection *unless* demo mode is active.

    This helper function is the single point through which all pages
    interact with the database. This makes the system predictable and
    allows demo mode to intercept DB operations cleanly.

    Behavior:
    ---------
    • If demo mode is ON:
        Returns None to indicate that no real database should be used.
        The calling functions check DEMO_MODE and adapt accordingly.
    
    • If demo mode is OFF:
        Attempts to connect to the database using credentials defined
        in secrets.toml under the [db] section.

    Returns:
    --------
    - A live MySQL connection object if successful.
    - None if demo mode is enabled or a connection error occurs.
    """

    # When demo mode is enabled, force all DB callers to skip real DB access.
    if DEMO_MODE:
        return None

    try:
        # Pull DB connection details from Streamlit secrets.
        conn = mysql.connector.connect(
            host=st.secrets["db"]["host"],
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            database=st.secrets["db"]["database"],
            port=st.secrets["db"]["port"],
        )
        return conn

    except Error as e:
        # Display a visible error in the UI and return None for callers
        # to gracefully handle failures.
        st.error(f"Database connection failed: {e}")
        return None