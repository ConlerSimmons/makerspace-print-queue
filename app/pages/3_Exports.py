import sys
import os
# Add project root to Python path (so "app.*" imports work when Streamlit loads pages)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from io import BytesIO
import mysql.connector
from app.db import get_connection, DEMO_MODE

#############################################
# STAFF AUTHENTICATION HOOK (SAFE & OPTIONAL)
#############################################
def user_is_staff():
    """
    Placeholder for future authentication.

    IT will eventually replace this with real checks:
        - Campus SSO
        - LDAP / Active Directory
        - NetID role/group memberships

    For now:
        Always returns True.
        This ensures nothing breaks and all staff pages stay visible.
    """
    return True
#############################################


def fetch_export_data():
    """
    Retrieve full joined job data for reporting/export.

    In DEMO_MODE:
        Returns a single fabricated row that mimics the real schema.
        This allows the Export UI to work even without a real database.

    In Production:
        Executes a multi-table JOIN to assemble:
            • job info
            • patron info
            • machine assignments
            • material usage
            • charge history

    Returns:
        Pandas DataFrame
        or None if database unavailable.
    """
    if DEMO_MODE:
        return pd.DataFrame([
            {
                "job_id": 1,
                "job_number": "D-001",
                "job_name": "Demo Job",
                "created_at": "2025-01-01",
                "num_items": 2,
                "netid": "demo123",
                "patron_name": "Demo Student",
                "patron_email": "demo@creighton.edu",
                "machine_name": "Demo Printer",
                "material_name": "PLA",
                "material_color": "Red",
                "machine_role": "primary",
                "material_qty": 10,
                "material_unit": "g",
                "charge_amount": 5.00,
                "charged_to": "Demo Account",
                "charged_at": "2025-01-02"
            }
        ])

    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)

        # Combined export query:
        # This pulls together jobs, patrons, printers, materials, and charges.
        cursor.execute(
            """
            SELECT
                pj.job_id,
                pj.job_number,
                pj.job_name,
                pj.created_at,
                pj.num_items,
                p.netid,
                p.name AS patron_name,
                p.email AS patron_email,
                m.display_name AS machine_name,
                mat.name AS material_name,
                mat.color AS material_color,
                jm.role AS machine_role,
                jmat.qty AS material_qty,
                jmat.unit AS material_unit,
                jc.amount AS charge_amount,
                jc.charged_to,
                jc.charged_at
            FROM print_jobs pj
            JOIN patrons p ON pj.patron_id = p.patron_id
            LEFT JOIN job_machines jm ON jm.job_id = pj.job_id
            LEFT JOIN machines m ON m.machine_id = jm.machine_id
            LEFT JOIN job_materials jmat ON jmat.job_id = pj.job_id
            LEFT JOIN materials mat ON mat.material_id = jmat.material_id
            LEFT JOIN job_charges jc ON jc.job_id = pj.job_id
            ORDER BY pj.created_at DESC, pj.job_id DESC
            """
        )

        rows = cursor.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    except mysql.connector.Error as e:
        st.error(f"Error fetching export data: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def render_exports_page():
    """
    UI for exporting full makerspace job records.

    Provides:
        • A preview table of all combined job data
        • A one-click Excel export (OpenXML .xlsx)
        • Demo mode visibility that mirrors real usage

    This page is primarily used by staff for:
        • Reporting
        • Semester summaries
        • Internal documentation
        • Financial or usage audits
    """

    st.title("Data Exports")

    #############################################
    # APPLY STAFF HOOK (non-breaking placeholder)
    #############################################
    if not user_is_staff():
        st.error("You do not have permission to view this page.")
        st.stop()
    #############################################

    if DEMO_MODE:
        st.info(
            "Demo mode: exporting simulated data only. "
            "No real database records are used."
        )

    st.write(
        """
        Export Makerspace job data to Excel for reporting or archival.
        This includes patrons, jobs, machines, materials, and charges.
        """
    )

    # Load export dataset (real or simulated)
    df = fetch_export_data()

    if df is None:
        # DB unavailable or failed connection
        st.stop()

    if df.empty:
        st.info("No data available yet to export.")
        return

    # Preview section
    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)

    # Convert DataFrame → Excel bytes
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="PrintJobs")
    buffer.seek(0)

    # Download button
    st.download_button(
        label="Download Excel Export",
        data=buffer,
        file_name="makerspace_print_jobs_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    render_exports_page()