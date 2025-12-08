import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import mysql.connector
from app.db import get_connection


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
):
    """
    Insert (or reuse) a patron and create a new print job.
    Returns the new job_id on success, or None on failure.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)

        # 1) Check if patron already exists by netid
        cursor.execute(
            "SELECT patron_id FROM patrons WHERE netid = %s",
            (netid,),
        )
        row = cursor.fetchone()

        if row:
            patron_id = row["patron_id"]
        else:
            # 2) Insert new patron
            cursor.execute(
                """
                INSERT INTO patrons (netid, name, email, phone, affiliation, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (netid, name, email, phone or None, affiliation or None, status or "student"),
            )
            patron_id = cursor.lastrowid

        # 3) Insert print job
        cursor.execute(
            """
            INSERT INTO print_jobs (
                patron_id,
                job_name,
                num_items,
                is_class_assign,
                special_instructions,
                support_needed,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                patron_id,
                job_name,
                num_items if num_items is not None else None,
                1 if is_class_assign else 0,
                special_instructions or None,
                1 if support_needed else 0,
                notes or None,
            ),
        )
        job_id = cursor.lastrowid

        conn.commit()
        return job_id

    except mysql.connector.Error as e:
        conn.rollback()
        st.error(f"Error inserting into database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def render_student_submission():
    st.title("Student Print Job Submission")

    st.write(
        """
        Please fill out the form below to submit a print job to the Makerspace.
        Your information will be stored securely in the Makerspace database.
        """
    )

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
        num_items = st.number_input(
            "Number of Items (optional)", min_value=0, step=1, format="%d",
        )

        is_class_assign = st.checkbox("Is this for a class assignment?")
        support_needed = st.checkbox("Do you think support material will be needed?")

        special_instructions = st.text_area(
            "Special Instructions (optional)",
            help="Anything specific the staff should know about your print.",
        )

        notes = st.text_area(
            "Additional Notes (optional)",
            help="Any extra context or information.",
        )

        submitted = st.form_submit_button("Submit Print Job")

    if submitted:
        # Validate required fields
        if not netid or not name or not email or not job_name:
            st.error("Please fill in all required fields (NetID, Name, Email, Job Name).")
            return

        job_id = insert_patron_and_job(
            netid=netid.strip(),
            name=name.strip(),
            email=email.strip(),
            phone=phone.strip() if phone else None,
            affiliation=affiliation.strip() if affiliation else None,
            status=status,
            job_name=job_name.strip(),
            num_items=int(num_items) if num_items is not None else None,
            is_class_assign=is_class_assign,
            special_instructions=special_instructions,
            support_needed=support_needed,
            notes=notes,
        )

        if job_id is not None:
            st.success(f"Your print job has been submitted! Reference Job ID: {job_id}")
        else:
            st.error("There was a problem submitting your job. Please try again or contact staff.")


if __name__ == "__main__":
    render_student_submission()