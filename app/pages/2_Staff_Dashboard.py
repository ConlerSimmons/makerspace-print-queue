import sys
import os
# Add project root to Python path so "app.*" imports work when Streamlit loads pages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import mysql.connector
from app.db import get_connection, DEMO_MODE

#############################################
# STAFF AUTHENTICATION HOOK (SAFE & OPTIONAL)
#############################################
def user_is_staff():
    """
    Placeholder for future authentication.

    IT will eventually replace this with *real* logic such as:
        • campus SSO integration  
        • checking authenticated NetIDs  
        • checking group memberships (e.g., "makerspace_staff")

    For now:
        - Always returns True so the dashboard is ALWAYS visible.
        - This ensures the app remains fully usable during development.

    IMPORTANT:
        This function is *never* used to block any DB write operations.
        It ONLY determines whether the staff UI is visible.
    """
    return True
#############################################


def fetch_jobs():
    """
    Retrieve all print jobs for staff review.

    Behavior:
    ---------
    • If DEMO_MODE is ON → return a small hardcoded job list.
    • Otherwise → query real MySQL data.

    Returns:
        Pandas DataFrame (may be empty)
        or None if DB connection fails.
    """
    if DEMO_MODE:
        return pd.DataFrame([
            {
                "job_id": 1,
                "job_name": "Demo Job",
                "created_at": "2025-01-01",
                "num_items": 2,
                "netid": "demo123",
                "patron_name": "Demo Student",
                "patron_email": "demo@creighton.edu"
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
                pj.job_name,
                pj.created_at,
                pj.num_items,
                p.netid,
                p.name AS patron_name,
                p.email AS patron_email
            FROM print_jobs pj
            JOIN patrons p ON pj.patron_id = p.patron_id
            ORDER BY pj.created_at DESC
            """
        )
        rows = cursor.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    except mysql.connector.Error as e:
        st.error(f"Error fetching jobs: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def fetch_machines():
    """
    Fetch list of available 3D printers.

    Demo mode returns a single fake machine.
    """
    if DEMO_MODE:
        return [{"machine_id": 1, "display_name": "Demo Printer"}]

    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT machine_id, display_name FROM machines ORDER BY display_name")
        return cursor.fetchall()

    except mysql.connector.Error as e:
        st.error(f"Error fetching machines: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def fetch_materials():
    """
    Retrieve all printing materials (PLA, ABS, colors, units, etc.).

    Demo mode returns a single simulated material.
    """
    if DEMO_MODE:
        return [{"material_id": 1, "name": "PLA", "color": "Red", "unit": "g"}]

    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT material_id, name, color, unit FROM materials ORDER BY name, color"
        )
        return cursor.fetchall()

    except mysql.connector.Error as e:
        st.error(f"Error fetching materials: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def upsert_job_machine(job_id, machine_id, role, notes):
    """
    Assign or update the printer (machine) used for a job.

    • In DEMO_MODE → always return True.
    • Otherwise:
        - Attempt an UPDATE first.
        - If no row updated → INSERT a new one.
    """
    if DEMO_MODE:
        return True

    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # First try updating an existing assignment
        cursor.execute(
            """
            UPDATE job_machines
            SET role = %s, notes = %s
            WHERE job_id = %s AND machine_id = %s
            """,
            (role or None, notes or None, job_id, machine_id),
        )

        # If nothing updated, insert new assignment
        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO job_machines (job_id, machine_id, role, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (job_id, machine_id, role or None, notes or None),
            )

        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        st.error(f"Error updating job_machines: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def upsert_job_material(job_id, material_id, qty, unit, notes):
    """
    Add or update material usage for a job.

    Same pattern as machine assignment:
        • Try UPDATE first
        • INSERT if needed
    """
    if DEMO_MODE:
        return True

    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE job_materials
            SET qty = %s, unit = %s, notes = %s
            WHERE job_id = %s AND material_id = %s
            """,
            (qty, unit or None, notes or None, job_id, material_id),
        )

        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO job_materials (job_id, material_id, qty, unit, notes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (job_id, material_id, qty, unit or None, notes or None),
            )

        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        st.error(f"Error updating job_materials: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def insert_job_charge(job_id, amount, charged_to, notes):
    """
    Record a billing/charge entry for a print job.
    """
    if DEMO_MODE:
        return True

    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO job_charges (job_id, amount, charged_to, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (job_id, amount, charged_to or None, notes or None),
        )

        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        st.error(f"Error inserting charge: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def render_staff_dashboard():
    """
    Main UI for staff operations.

    This page allows staff to:
      • View all submitted jobs  
      • Assign printers  
      • Assign materials  
      • Record charges  

    Demo mode alters only the *data sources*, not the UI structure.
    """

    st.title("Staff Dashboard")

    #############################################
    # Apply the staff access hook
    # (non-breaking and safe for production)
    #############################################
    if not user_is_staff():
        st.error("You do not have permission to view this page.")
        st.stop()
    #############################################

    if DEMO_MODE:
        st.info("Demo mode: database functions use simulated data.")

    st.write(
        """
        View all submitted print jobs below.
        Use the forms to assign machines, materials, and record charges.
        """
    )

    # ---------------------------
    # LOAD ALL JOBS
    # ---------------------------
    jobs_df = fetch_jobs()

    if jobs_df is None:
        st.stop()

    if jobs_df.empty:
        st.info("No print jobs found yet.")
    else:
        st.subheader("Current Print Jobs")
        st.dataframe(jobs_df, use_container_width=True)

    job_ids = jobs_df["job_id"].tolist() if not jobs_df.empty else []

    # ---------------------------
    # MACHINE ASSIGNMENT
    # ---------------------------
    st.subheader("Assign / Update Machine for a Job")
    machines = fetch_machines()

    if job_ids and machines:
        with st.form("assign_machine_form"):
            selected_job = st.selectbox("Job ID", job_ids)

            machine_labels = [f"{m['display_name']} (ID {m['machine_id']})" for m in machines]
            machine_ids = [m["machine_id"] for m in machines]

            machine_idx = st.selectbox(
                "Machine",
                range(len(machine_ids)),
                format_func=lambda i: machine_labels[i],
            )

            role_val = st.text_input("Machine Role (optional)")
            notes = st.text_area("Machine Notes (optional)")

            submit_machine = st.form_submit_button("Save Machine Assignment")

        if submit_machine:
            ok = upsert_job_machine(
                selected_job,
                machine_ids[machine_idx],
                role_val,
                notes,
            )
            if ok:
                st.success("Machine assignment saved.")
    else:
        st.info("No jobs or machines available.")

    # ---------------------------
    # MATERIAL ASSIGNMENT
    # ---------------------------
    st.subheader("Assign / Update Material for a Job")
    materials = fetch_materials()

    if job_ids and materials:
        with st.form("assign_material_form"):
            selected_job_mat = st.selectbox("Job ID (materials)", job_ids, key="job_for_material")

            material_labels = [
                f"{m['name']} ({m['color'] or 'no color'}) [ID {m['material_id']}]"
                for m in materials
            ]
            material_ids = [m["material_id"] for m in materials]

            mat_idx = st.selectbox(
                "Material",
                range(len(material_ids)),
                format_func=lambda i: material_labels[i],
            )

            qty = st.number_input("Quantity", min_value=0.0, step=0.1)
            unit = st.text_input("Unit (optional)")
            mat_notes = st.text_area("Material Notes (optional)")

            submit_material = st.form_submit_button("Save Material Assignment")

        if submit_material:
            if qty <= 0:
                st.error("Quantity must be greater than zero.")
            else:
                ok = upsert_job_material(
                    selected_job_mat,
                    material_ids[mat_idx],
                    qty,
                    unit if unit.strip() else None,
                    mat_notes,
                )
                if ok:
                    st.success("Material assignment saved.")
    else:
        st.info("No jobs or materials available.")

    # ---------------------------
    # CHARGES
    # ---------------------------
    st.subheader("Record a Charge for a Job")

    if job_ids:
        with st.form("charge_form"):
            selected_job_charge = st.selectbox("Job ID (charges)", job_ids, key="job_for_charge")

            amount = st.number_input("Amount (required)", min_value=0.0, step=0.5)
            charged_to = st.text_input("Charged To (optional)")
            charge_notes = st.text_area("Charge Notes (optional)")

            submit_charge = st.form_submit_button("Record Charge")

        if submit_charge:
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                ok = insert_job_charge(
                    selected_job_charge,
                    amount,
                    charged_to,
                    charge_notes,
                )
                if ok:
                    st.success("Charge recorded.")
    else:
        st.info("No jobs available to charge.")


if __name__ == "__main__":
    render_staff_dashboard()