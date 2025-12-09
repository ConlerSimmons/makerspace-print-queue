# Makerspace Print Queue — Project Documentation

This repository contains the full codebase for the Creighton Library **Makerspace Print Queue Application**, built with **Streamlit** and backed by a **MySQL database**.  
It includes:

- A **student-facing print job submission form**
- A **staff dashboard** for reviewing jobs, assigning machines/materials, and recording charges
- A **data export** interface
- A **demo mode** (for cloud deployments without a database)
- A **security scaffolding hook** (for IT to later implement real authentication)
- A clean, modular project structure ready for deployment

---

## High-Level Architecture Overview

Below is a **text-based architecture diagram** describing how the system works.  
IT may later replace the authentication layer or add backend integrations, but the core flow remains the same.

```
                          ┌──────────────────────────┐
                          │     Student Frontend     │
                          │  (Streamlit: Submission) │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │     Application Logic    │
                          │ (Streamlit pages + db.py)│
                          └─────────────┬────────────┘
                                        │
     Demo Mode ON ──────── Yes ────────┘
         │
         ▼
 ┌───────────────────────┐
 │  Simulated In-Memory  │
 │     Demo Responses    │
 └───────────────────────┘
                                        │
                                        ▼
                     Demo Mode OFF ─────┬───────► Real DB Mode
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │        MySQL DB          │
                          │  patrons, print_jobs,    │
                          │  job_machines, etc.      │
                          └──────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │     Staff Dashboard      │
                          │ (Machine/material work)  │
                          └──────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │     Export Interface     │
                          │ (Excel export via UI)    │
                          └──────────────────────────┘
```

---

## Project Structure & File Purpose

```
makerspace-print-queue/
│
├── app/
│   ├── Home.py                 → Main landing page; explains app structure
│   ├── db.py                   → Handles DB connections & demo mode behavior
│   │
│   ├── pages/                  → Streamlit multipage system
│   │   ├── 1_Student_Submission.py → Student form UI + DB inserts
│   │   ├── 2_Staff_Dashboard.py    → Staff job management UI
│   │   ├── 3_Exports.py            → Staff export-to-Excel interface
│   │
│   └── __init__.py
│
├── .streamlit/
│   ├── secrets.toml            → Stores DB credentials + demo_mode flag
│
├── requirements.txt            → Python dependencies
├── README.md                   → (THIS DOCUMENT)
└── venv/                       → Your local virtual environment
```

---

## Developer Setup Guide (Local Machine)

This section explains exactly how a developer or student should run the project locally.

---

### **1. Clone the Repository**
```bash
git clone <your-private-repo-url>
cd makerspace-print-queue
```

---

### **2. Create & Activate a Virtual Environment**
macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

---

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

---

### **4. Ensure MySQL or Docker DB is Running**

You must have **either**:

- A local MySQL server  
**OR**
- A Docker container running MySQL on port `3307`

Example Docker command:
```bash
docker run --name makerspace-mysql -p 3307:3306 -e MYSQL_ROOT_PASSWORD=pass123 -d mysql:8
```

---

### **5. Configure** `.streamlit/secrets.toml`

Example:
```toml
[db]
host = "127.0.0.1"
user = "root"
password = "pass123"
database = "makerspace_db_final"
port = 3307

[app]
demo_mode = false  # Set to true to disable DB access and enable demo data
force_staff_lock = false
```

Make sure this file exists locally — it is **not** committed to GitHub.

---

### **6. Run the Application**

From the project root:
```bash
python3 -m streamlit run app/Home.py
```

This opens the multipage interface in your browser.

---

### You should now see:
- Home page  
- Student Submission  
- Staff Dashboard  
- Exports  

And everything should work **with your real local database** when `demo_mode = false`.

---

## Demo Mode (Used for Streamlit Cloud)

Streamlit Cloud **cannot connect to a local DB**, so this repository includes a **demo mode flag**:

```toml
[app]
demo_mode = true
```

When `demo_mode = true`:
- No database connections occur  
- Fake data is used for Staff Dashboard and Exports  
- Student submission returns a simulated Job ID  
- No writes are attempted  
- The UI displays a banner indicating demo mode is active  

This allows:
- Library staff to preview the interface  
- Secure deployment without exposing student data  
- Demonstration without infrastructure

---

## IT Implementation Guide (Production Deployment)

This section is written specifically for Creighton IT, showing what they must do to deploy the production version.

---

### **1. Prepare a Production MySQL Database**

IT will run the SQL schema (provided separately as the final SQL build script).

Required tables:
- patrons
- print_jobs
- machines
- materials
- job_machines
- job_materials
- job_charges

---

### **2. Configure Streamlit Secrets on Production Server**

Example production secrets file:

```toml
[db]
host = "INTERNAL_DB_HOST"
user = "makerspace_user"
password = "PRODUCTION_SECURE_PASSWORD"
database = "makerspace_prod"
port = 3306

[app]
demo_mode = false          # Production = OFF
force_staff_lock = true    # Optional: IT may enforce staff-only mode
```

---

### **3. Replace the Authentication Hook**

Inside:

```
app/pages/2_Staff_Dashboard.py  
app/pages/3_Exports.py
```

IT will update:

```python
def user_is_staff():
    return True
```

to something like:

```python
def user_is_staff():
    return st.experimental_user.email.endswith("@creighton.edu")  
```

Or any approved SSO / SAML / LDAP logic.

This is the **only part they must modify** in the code.

---

### **4. Deployment Options**

IT can deploy:

#### **Option A — Streamlit Cloud (simplest)**
- Works fully when DB is publicly reachable
- Requires DB IP allowlisting

#### **Option B — Internal Creighton Server (recommended)**
- Docker container  
- Or local Python environment with systemd service  
- Reverse proxy (Nginx) to expose HTTPS  

---

### **5. Post-Deployment Expectations**
Once deployed, staff will be able to:

- Receive real student submissions  
- Manage print job workflow  
- Export reports on demand  

No further code changes required.

---

## Final Notes

- This project is built to be **simple**, **secure**, and **easy to maintain**  
- Developers can run everything locally with MySQL or Docker  
- IT can deploy it with minimal changes  
- Demo mode guarantees safe public demonstration  
- Authentication hook ensures forward-compatibility with Creighton systems  

---

If you need a **PDF version**, **diagram image**, or **additional internal documentation**, I can generate that as well.