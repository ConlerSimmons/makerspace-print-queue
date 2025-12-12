import sys
import os

# Add the project root directory to Python's module search path.
# This allows imports like `from app.db import DEMO_MODE` to work
# regardless of where Streamlit executes the script.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db import DEMO_MODE  # Imported so the UI can reflect whether demo mode is active


def main():
    """
    The main entry point for the Home page.

    This file does not interact with the database directly.
    Instead, it explains the purpose of the application and
    displays navigation guidance for students and staff.

    All functional pages (submission, dashboard, exports)
    are implemented as Streamlit "pages" in the /app/pages directory.
    """

    # Configure the Streamlit page (title, icon, layout).
    st.set_page_config(
        page_title="Makerspace Print Queue",
        page_icon="🖨️",
        layout="wide",
    )

    # If demo mode is turned on in secrets.toml, show a banner so users
    # understand that no real database changes will occur.
    if DEMO_MODE:
        st.warning(
            "**Demo Mode is ON — database actions are simulated and no real data is stored.**"
        )

    # Main page header
    st.title("Makerspace Print Queue")

    # Overview text shown on the landing page.
    # Explains where users should navigate depending on their role.
    st.write(
        """
        Welcome to the Creighton Library Makerspace print queue.

        Use the navigation on the left to move between:
        - **Sign In** – quick sign-in for anyone visiting the Makerspace (tracks involvement)
        - **3D Printing Submissions** – submit new 3D print jobs with file uploads
        - **Staff Dashboard** – staff interface to review jobs, assign machines/materials, and download files
        - **Exports** – export print job records or sign-in records to Excel (with fiscal year tracking)
        """
    )

    st.markdown("---")

    # High-level workflow explanation so new users understand how
    # information flows through the system.
    st.subheader("How this app works")
    st.markdown(
        """
        **For Visitors:**
        1. **Sign in** when you arrive at the Makerspace to track involvement.
        
        **For Print Jobs:**
        1. **Students/Staff** submit 3D print jobs on the *3D Printing Submissions* page with file uploads.  
        2. Jobs are stored in the **makerspace_db_final** MySQL database *(or simulated during demo mode).*  
        3. **Staff** review jobs, download print files, assign machines/materials, and record charges on the *Staff Dashboard*.  
        4. Staff can export two types of data on the *Exports* page:
           - **3D Print Records** (jobs, materials, charges, fiscal year)
           - **Sign-In Records** (visitor tracking for involvement metrics)
        """
    )


# Standard Python pattern to execute the app when the file is run directly.
# Streamlit calls this automatically when loading the home page.
if __name__ == "__main__":
    main()