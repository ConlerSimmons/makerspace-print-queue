#!/bin/bash
# Quick setup script to create the sign_ins table and add fiscal_year to print_jobs

echo "==================================================="
echo "Makerspace Database Setup"
echo "==================================================="
echo ""
echo "This script will run the SQL migration to add:"
echo "  1. fiscal_year column to print_jobs table"
echo "  2. sign_ins table for visitor tracking"
echo ""
echo "Make sure MySQL is running before continuing."
echo ""

# Prompt for MySQL credentials
read -p "MySQL Host (default: 127.0.0.1): " DB_HOST
DB_HOST=${DB_HOST:-127.0.0.1}

read -p "MySQL Port (default: 3307): " DB_PORT
DB_PORT=${DB_PORT:-3307}

read -p "MySQL User (default: root): " DB_USER
DB_USER=${DB_USER:-root}

read -sp "MySQL Password: " DB_PASSWORD
echo ""

read -p "Database Name (default: makerspace_db_final): " DB_NAME
DB_NAME=${DB_NAME:-makerspace_db_final}

echo ""
echo "Running migration script..."
echo ""

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$(dirname "$0")/Add_Sign_In_And_Fiscal_Year.sql"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "The following tables/columns are now ready:"
    echo "  - print_jobs.fiscal_year"
    echo "  - sign_ins (full table)"
    echo ""
    echo "You can now run the Streamlit app!"
else
    echo ""
    echo "❌ Migration failed. Please check your credentials and try again."
    echo ""
fi
