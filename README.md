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

### **4. Set Up MySQL Database Using Docker**

This project requires a MySQL database. The easiest way is to use Docker.

#### **Step 4.1: Install Docker**

If you don't have Docker installed:

- **macOS**: Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- **Windows**: Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

After installation, verify Docker is running:
```bash
docker --version
```

#### **Step 4.2: Create MySQL Container**

Run this command to create and start a MySQL container:

```bash
docker run --name mysql542 \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=pass123 \
  -e MYSQL_DATABASE=makerspace_db_final \
  -d mysql:8.0
```

**What this does:**
- Creates a container named `mysql542`
- Maps port `3307` on your computer to MySQL's port `3306`
- Sets root password to `pass123`
- Creates database `makerspace_db_final` automatically
- Runs MySQL 8.0 in the background

#### **Step 4.3: Verify Container is Running**

Check that your MySQL container is running:
```bash
docker ps
```

You should see a container named `mysql542` in the list.

**Common Docker Commands:**
```bash
# Start the container (if stopped)
docker start mysql542

# Stop the container
docker stop mysql542

# View logs
docker logs mysql542

# Remove container (careful - deletes all data!)
docker rm -f mysql542
```

#### **Step 4.4: Create Database Tables**

Now run the SQL script to create all tables:

```bash
# Navigate to project directory
cd makerspace-print-queue

# Run the main SQL script to create all tables
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Final_SQL_Script.sql
```

**Expected output:** No errors (warnings about password on command line are OK)

#### **Step 4.5: Verify Tables Were Created**

```bash
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; SHOW TABLES;"
```

You should see these tables:
- `patrons`
- `print_jobs`
- `sign_ins`
- `staff`
- `machines`
- `materials`
- `job_machines`
- `job_materials`
- `job_charges`

---

### **5. Configure** `.streamlit/secrets.toml`

Create a file at `.streamlit/secrets.toml` (create the `.streamlit` folder if it doesn't exist):

```bash
mkdir -p .streamlit
```

Then create/edit `.streamlit/secrets.toml` with this content:

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

Make sure:
1. ✅ Docker container `mysql542` is running (`docker ps`)
2. ✅ Database tables are created
3. ✅ `.streamlit/secrets.toml` is configured

Then from the project root:
```bash
python3 -m streamlit run app/Home.py
```

This opens the multipage interface in your browser at `http://localhost:8501`

---

### **You should now see:**
- **Sign In** - Visitor sign-in page  
- **3D Printing Submissions** - Submit print jobs with file uploads
- **Staff Dashboard** - Manage jobs, download files, assign machines/materials
- **Exports** - Two Excel export options (Print Jobs & Sign-Ins by fiscal year/quarter)

And everything should work **with your real Docker database** when `demo_mode = false`.

---

## Troubleshooting

### "Can't connect to MySQL server"
- Make sure Docker container is running: `docker ps`
- Start it if stopped: `docker start mysql542`

### "Table doesn't exist"
- Run the SQL script again: 
  ```bash
  docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Final_SQL_Script.sql
  ```

### "Unknown column 'fiscal_quarter'"
- Run this to add missing column:
  ```bash
  docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; ALTER TABLE sign_ins ADD COLUMN fiscal_quarter INT NULL DEFAULT NULL AFTER fiscal_year;"
  ```

### Reset Everything (Fresh Start)
```bash
# Stop and remove container
docker stop mysql542
docker rm mysql542

# Create new container
docker run --name mysql542 -p 3307:3306 -e MYSQL_ROOT_PASSWORD=pass123 -e MYSQL_DATABASE=makerspace_db_final -d mysql:8.0

# Wait 10 seconds for MySQL to start
sleep 10

# Create all tables
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Final_SQL_Script.sql
```

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
