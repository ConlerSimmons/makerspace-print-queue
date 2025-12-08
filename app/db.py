import streamlit as st

# -------------------------------------------------------
# DEMO MODE TOGGLE
# -------------------------------------------------------
# Default is False so production is safe.
DEMO_MODE = False

# If running inside Streamlit Cloud or if the local secrets file
# contains demo_mode=true, override it.
try:
    if "demo_mode" in st.secrets:
        DEMO_MODE = bool(st.secrets["demo_mode"])
except Exception:
    # If secrets can't load (e.g., running locally without secrets.toml),
    # keep demo mode OFF by default.
    DEMO_MODE = False


# -------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------
def get_connection():
    """
    Returns:
      - None if DEMO_MODE=True (the app uses mock data)
      - A real MySQL connection if DEMO_MODE=False
    """

    if DEMO_MODE:
        # No real DB in demo mode
        return None

    # Production mode → attempt a real DB connection
    try:
        host = st.secrets["db"]["host"]
        user = st.secrets["db"]["user"]
        password = st.secrets["db"]["password"]
        database = st.secrets["db"]["database"]
        port = st.secrets["db"]["port"]

        import mysql.connector
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        return conn

    except Exception as e:
        # Streamlit Cloud will show this to you, not end users
        st.error(f"Database connection failed: {e}")
        return None