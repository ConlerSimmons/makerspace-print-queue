import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from io import BytesIO
import mysql.connector
from app.db import get_connection, DEMO_MODE


def fetch_export_data():
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
    st.title("Data Exports")

    if DEMO_MODE:
        st.info("Demo mode: export data is simulated and does not come from a real database.")

    st.write(
        """
        Export Makerspace job data to Excel for reporting or archival.
        This includes patrons, jobs, machines, materials, and charges.
        """
    )

    df = fetch_export_data()

    if df is None:
        st.stop()

    if df.empty:
        st.info("No data available yet to export.")
        return

    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="PrintJobs")
    buffer.seek(0)

    st.download_button(
        label="Download Excel Export",
        data=buffer,
        file_name="makerspace_print_jobs_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    render_exports_page()