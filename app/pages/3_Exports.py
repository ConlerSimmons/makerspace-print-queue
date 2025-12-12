import sys
import os
# Add project root to Python path (so "app.*" imports work when Streamlit loads pages)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from io import BytesIO
import mysql.connector
from app.db import get_connection, DEMO_MODE
from datetime import datetime

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
            • job info (with fiscal year)
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
                "fiscal_year": 2025,
                "num_items": 2,
                "upload_path": "uploads/demo_file.stl",
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
                pj.fiscal_year,
                pj.num_items,
                pj.upload_path,
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


def fetch_sign_in_data():
    """
    Retrieve all sign-in records for export.
    
    Returns:
        Pandas DataFrame with sign-in records including fiscal quarter
        or None if database unavailable
    """
    if DEMO_MODE:
        return pd.DataFrame([
            {
                "sign_in_id": 1,
                "name": "Demo User",
                "email": "demo@creighton.edu",
                "sign_in_time": "2025-01-01 10:00:00",
                "fiscal_year": 2025,
                "fiscal_quarter": 3
            },
            {
                "sign_in_id": 2,
                "name": "Jane Smith",
                "email": "janesmith@creighton.edu",
                "sign_in_time": "2025-01-02 14:30:00",
                "fiscal_year": 2025,
                "fiscal_quarter": 3
            }
        ])
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                sign_in_id,
                name,
                email,
                sign_in_time,
                fiscal_year,
                fiscal_quarter
            FROM sign_ins
            ORDER BY sign_in_time DESC
            """
        )
        
        rows = cursor.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    
    except mysql.connector.Error as e:
        st.error(f"Error fetching sign-in data: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()


def render_exports_page():
    """
    UI for exporting makerspace records.

    Provides TWO separate export options:
        1. 3D Print Job Records - full job/patron/machine/material/charge data
        2. Sign-In Records - visitor tracking for involvement metrics (by fiscal year and quarter)

    Each export:
        • Shows a preview table
        • Provides one-click CSV download
        • Includes fiscal year tracking
        • Works in both demo and production modes
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
        Export Makerspace records to CSV for reporting, analysis, or archival.
        Choose between 3D print job records or sign-in records below.
        """
    )

    # =====================================================
    # EXPORT 1: 3D PRINT JOB RECORDS
    # =====================================================
    st.header("📦 3D Print Job Records")
    st.write("Export complete print job data including patrons, machines, materials, and charges.")

    # Load print job dataset (real or simulated)
    jobs_df = fetch_export_data()

    if jobs_df is None:
        st.error("Unable to fetch print job data.")
    elif jobs_df.empty:
        st.info("No print job data available yet to export.")
    else:
        # Preview section
        st.subheader("Preview")
        st.dataframe(jobs_df, use_container_width=True)

        # Convert DataFrame → CSV
        csv_data = jobs_df.to_csv(index=False)

        # Download button
        st.download_button(
            label="📥 Download 3D Print Records (CSV)",
            data=csv_data,
            file_name=f"makerspace_print_jobs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_print_jobs"
        )

    st.divider()

    # =====================================================
    # EXPORT 2: SIGN-IN RECORDS
    # =====================================================
    st.header("🖊️ Sign-In Records")
    st.write("Export visitor sign-in data for involvement tracking and reporting by fiscal year and quarter.")

    # Load sign-in dataset
    signin_df = fetch_sign_in_data()

    if signin_df is None:
        st.error("Unable to fetch sign-in data.")
    elif signin_df.empty:
        st.info("No sign-in data available yet to export.")
    else:
        # Show summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sign-Ins", len(signin_df))
        with col2:
            st.metric("Unique Visitors", signin_df["email"].nunique())
        with col3:
            if "fiscal_year" in signin_df.columns:
                current_fy = signin_df["fiscal_year"].mode()[0] if not signin_df.empty else "N/A"
                st.metric("Current FY", current_fy)

        # Preview section
        st.subheader("Preview")
        st.dataframe(signin_df, use_container_width=True)

        # Convert DataFrame → CSV
        csv_data2 = signin_df.to_csv(index=False)

        # Download button
        st.download_button(
            label="📥 Download Sign-In Records (CSV)",
            data=csv_data2,
            file_name=f"makerspace_sign_ins_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_sign_ins"
        )


if __name__ == "__main__":
    render_exports_page()
