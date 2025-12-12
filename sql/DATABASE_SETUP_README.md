# Database Setup Instructions

## Problem
You're seeing the error: `Table 'makerspace_db_final.sign_ins' doesn't exist`

This is because the database needs to be updated with the new sign-in functionality.

## Solution

You have **two options** to fix this:

---

### Option 1: Run the Migration Script (Recommended)

The migration script adds the missing table to your existing database.

**From the terminal, run:**

```bash
cd sql
./setup_database.sh
```

Or manually run:

```bash
mysql -h 127.0.0.1 -P 3307 -u root -p makerspace_db_final < sql/Add_Sign_In_And_Fiscal_Year.sql
```

This will:
- ✅ Add `fiscal_year` column to `print_jobs` table
- ✅ Create the `sign_ins` table
- ✅ Update existing jobs with calculated fiscal year

---

### Option 2: Rebuild the Entire Database (Fresh Start)

If you want to start fresh or don't have existing data to preserve:

```bash
mysql -h 127.0.0.1 -P 3307 -u root -p < sql/Final_SQL_Script.sql
```

This creates everything from scratch including the new `sign_ins` table.

---

## What Was Added

### New Table: `sign_ins`
Tracks visitor sign-ins to the Makerspace.

**Columns:**
- `sign_in_id` - Auto-incrementing ID
- `name` - Visitor's full name
- `email` - Creighton email
- `sign_in_time` - Timestamp of sign-in
- `fiscal_year` - Calculated fiscal year (July-June)
- `fiscal_quarter` - Q1-Q4 (July-Sep, Oct-Dec, Jan-Mar, Apr-Jun)

### Updated Table: `print_jobs`
Added `fiscal_year` column for fiscal year tracking on all print jobs.

---

## Fiscal Year & Quarter Calculation

**Fiscal Year:**
- July 1, 2024 - June 30, 2025 = **FY 2025**
- Automatically calculated and stored

**Fiscal Quarters:**
- Q1: July - September
- Q2: October - December
- Q3: January - March
- Q4: April - June

---

## After Running the Migration

1. Restart your Streamlit app (if running)
2. Try the Sign-In page - it should work now!
3. Check the Exports page - you'll see TWO export buttons:
   - 📦 **3D Print Records** (jobs, materials, charges)
   - 🖊️ **Sign-In Records** (visitor tracking by fiscal year/quarter)

---

## Troubleshooting

**If you still see errors:**

1. Make sure MySQL is running
2. Check your `.streamlit/secrets.toml` has correct database credentials
3. Verify the database name is `makerspace_db_final`
4. Try running the migration script again

**Check if tables exist:**

```sql
USE makerspace_db_final;
SHOW TABLES;
DESCRIBE sign_ins;
DESCRIBE print_jobs;
```

You should see `sign_ins` in the table list and `fiscal_year` in `print_jobs`.
