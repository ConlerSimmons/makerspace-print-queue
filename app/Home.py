import sys
import os

# Ensure project root is on the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db import DEMO_MODE  # <-- import demo mode flag


def main():
    st.set_page_config(
        page_title="Makerspace Print Queue",
        page_icon="🖨️",
        layout="wide",
    )

    # Small banner if demo mode is ON
    if DEMO_MODE:
        st.warning("**Demo Mode is ON — database actions are simulated and no real data is stored.**")

    st.title("Makerspace Print Queue")

    st.write(
        """
        Welcome to the Creighton Library Makerspace print queue.

        Use the navigation on the left to move between:
        - **Student Submission** – where students submit new print jobs.
        - **Staff Dashboard** – where staff review jobs and assign machines/materials.
        - **Exports** – where staff export job data to Excel for reporting or archival.
        """
    )

    st.markdown("---")
    st.subheader("How this app works")
    st.markdown(
        """
        1. **Students** submit jobs on the *Student Submission* page.  
        2. Jobs are stored in the **makerspace_db_final** MySQL database *(or simulated during demo mode).*  
        3. **Staff** review jobs, assign machines/materials, and record charges on the *Staff Dashboard*.  
        4. Staff can export data to Excel on the *Exports* page.
        """
    )


if __name__ == "__main__":
    main()