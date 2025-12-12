import sys
import os
# Add the project root directory to the Python path so imports
# like "from app.db import ..." work when Streamlit loads pages.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import mysql.connector
from app.db import get_connection, DEMO_MODE
from pathlib import Path
from datetime import datetime


def get_fiscal_year():
    """
    Calculate the fiscal year based on current date.
    Fiscal year starts July 1st.
    Example: July 1, 2024 - June 30, 2025 = FY 2025
    """
    now = datetime.now()
    if now.month >= 7:  # July or later
        return now.year + 1
    else:
        return now.year


def insert_patron_and_job(
    netid,
    name,
    email,
    phone,
    affiliation,
    status,
    job_name,
    num_items,
    is_class_assign,
    special_instructions,
    support_needed,
    notes,
    upload_path=None,
):
    """
    Insert (or reuse) a patron in the database, then create a new print job.

    How this function works:
    ------------------------
    • If DEMO_MODE is ON:
        We do *not* write to a real database. Instead, we simulate success
        by returning a placeholder job ID.

    • If DEMO_MODE is OFF:
        1. Establish a MySQL connection.
        2. Check whether a patron already exists based on NetID.
        3. Insert patron if needed.
        4. Insert a new print job tied to that patron.
        5. Commit the transaction and return the new job_id.

    Returns:
        - job_id (int) on success  
        - None if the insert fails or no DB connection is available
    """

    # Demo mode short-circuit
    if DEMO_MODE:
        # Return a fake job ID to mimic success
        return 9999

    conn = get_connection()
    if not conn:
        # If DB connection is unavailable, signal failure
        return None

    try:
        cursor = conn.cursor(dictionary=True)

        # ------------------------------------------------------------
        # 1) Check if this patron already exists based on their NetID
        # ------------------------------------------------------------
        cursor.execute("SELECT patron_id FROM patrons WHERE netid = %s", (netid,))
        row = cursor.fetchone()

        if row:
            patron_id = row["patron_id"]
        else:
            # ------------------------------------------------------------
            # 2) Insert a new patron record
            # ------------------------------------------------------------
            cursor.execute(
                """
                INSERT INTO patrons (netid, name, email, phone, affiliation, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (netid, name, email, phone or None, affiliation or None, status or "student"),
            )
            patron_id = cursor.lastrowid

        # ------------------------------------------------------------
        # 3) Insert the new print job tied to the patron
        # ------------------------------------------------------------
        fiscal_year = get_fiscal_year()
        
        cursor.execute(
            """
            INSERT INTO print_jobs (
                patron_id,
                job_name,
                num_items,
                is_class_assign,
                special_instructions,
                support_needed,
                notes,
                upload_path,
                fiscal_year
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                patron_id,
                job_name,
                num_items if num_items is not None else None,
                1 if is_class_assign else 0,
                special_instructions or None,
                1 if support_needed else 0,
                notes or None,
                upload_path,
                fiscal_year,
            ),
        )

        # Capture the new job ID
        job_id = cursor.lastrowid

        conn.commit()
        return job_id

    except mysql.connector.Error as e:
        # Roll back any partial changes
        conn.rollback()
        st.error(f"Error inserting into database: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def render_student_submission():
    """
    Renders the full Streamlit UI for students/staff to submit print requests.

    This page:
    • Displays the submission form  
    • Validates required fields  
    • Handles file uploads for 3D print files
    • Calls insert_patron_and_job()  
    • Shows success or error messages accordingly  
    • Adjusts behavior if DEMO_MODE is active  
    """
    st.title("3D Print Submission Form")

    # Banner to inform users that submission is simulated
    if DEMO_MODE:
        st.info("Demo mode: form submissions are simulated and no real data is stored.")

    st.write(
        """
        Please fill out the form below to submit a print job to the Makerspace.
        Your information will be stored securely in the Makerspace database.
        """
    )

    # ------------------------------------------------------------
    # Streamlit Form — groups input and submit button
    # ------------------------------------------------------------
    with st.form("student_submission_form"):
        st.subheader("Your Information")

        netid = st.text_input("NetID (required)")
        name = st.text_input("Full Name (required)")
        email = st.text_input("Email (required)")
        phone = st.text_input("Phone (optional)")
        affiliation = st.text_input("Affiliation (optional)")
        status = st.selectbox(
            "Status",
            ["student", "faculty", "staff", "alumni", "visitor", "other"],
            index=0,
        )

        st.subheader("Print Job Details")

        job_name = st.text_input("Job Name / Description (required)")
        num_items = st.number_input("Number of Items (optional)", min_value=0, step=1, format="%d")

        is_class_assign = st.checkbox("Is this for a class assignment?")
        support_needed = st.checkbox("Do you think support material will be needed?")

        special_instructions = st.text_area("Special Instructions (optional)")
        notes = st.text_area("Additional Notes (optional)")

        st.subheader("3D Print File Upload")
        st.write("Upload your 3D print file(s) (STL, OBJ, 3MF, GCODE, etc.)")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=["stl", "obj", "3mf", "gcode", "step", "stp", "iges", "igs", "amf", "ply"],
            help="Upload your 3D model file. Supported formats: STL, OBJ, 3MF, GCODE, STEP, IGES, AMF, PLY"
        )

        # Actual submit button
        submitted = st.form_submit_button("Submit Print Job")

    # ------------------------------------------------------------
    # Handle form submission
    # ------------------------------------------------------------
    if submitted:
        # Basic validation of required fields
        if not netid or not name or not email or not job_name:
            st.error("Please fill in all required fields.")
            return

        # Handle file upload
        file_path = None
        if uploaded_file is not None:
            # Create uploads directory if it doesn't exist
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            # Save file with a unique name (netid_jobname_filename)
            safe_job_name = "".join(c for c in job_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_job_name = safe_job_name.replace(' ', '_')[:50]  # Limit length
            file_name = f"{netid.strip()}_{safe_job_name}_{uploaded_file.name}"
            file_path = upload_dir / file_name
            
            # Write the uploaded file to disk
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_path = str(file_path)  # Convert to string for database
            except Exception as e:
                st.error(f"Error saving file: {e}")
                file_path = None

        # Attempt to create job
        job_id = insert_patron_and_job(
            netid.strip(),
            name.strip(),
            email.strip(),
            phone.strip() if phone else None,
            affiliation.strip() if affiliation else None,
            status,
            job_name.strip(),
            int(num_items) if num_items is not None else None,
            is_class_assign,
            special_instructions,
            support_needed,
            notes,
            file_path,
        )

        # Display success or failure result
        if job_id is not None:
            st.success(f"Your print job has been submitted! Reference Job ID: {job_id}")
            if file_path:
                st.success(f"File uploaded: {uploaded_file.name}")
        else:
            st.error("There was a problem submitting your job.")


if __name__ == "__main__":
    render_student_submission()