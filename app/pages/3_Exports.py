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
        # Sample joined data to demonstrate the export layout.
        data = [
            {
                "job_id": 101,
                "job_number": "MS-2025-001",
                "job_name": "Phone Stand",
                "created_at": "2025-01-10 10:00:00",
                "num_items": 1,
                "netid": "abc123",
                "patron_name": "Alex Student",
                "patron_email": "alex.student@example.edu",
                "machine_name": "Prusa MK3S+ #1",
                "material_name": "PLA",
                "material_color": "Black",
                "machine_role": "primary",
                "material_qty": 35.0,
                "material_unit": "g",
                "charge_amount": 2.50,
                "charged_to": "student account",
                "charged_at": "2025-01-11 09:00:00",
            },
            {
                "job_id": 102,
                "job_number": "MS-2025-002",
                "job_name": "Board Game Pieces",
                "created_at": "2025-01-11 14:30:00",
                "num_items": 6,
                "netid": "xyz789",
                "patron_name": "Blake Researcher",
                "patron_email": "blake.researcher@example.edu",
                "machine_name": "Prusa MK3S+ #2",
                "material_name": "PLA",
                "material_color": "White",
                "machine_role": "primary",
                "material_qty": 120.0,
                "material_unit": "g",
                "charge_amount": 5.00,
                "charged_to": "grant fund",
                "charged_at": "2025-01-12 13:15:00",
            },
        ]
        return pd.DataFrame(data)

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
        st.info(
            "Demo mode is enabled. The export below uses sample data only and does "
            "not reflect a live database."
        )

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
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


if __name__ == "__main__":
    render_exports_page()