# Docker Quick Reference for Makerspace Print Queue

This is a quick reference guide for managing the MySQL Docker container used by this project.

---

## Initial Setup

### 1. Create and Start MySQL Container
```bash
docker run --name mysql542 \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=pass123 \
  -e MYSQL_DATABASE=makerspace_db_final \
  -d mysql:8.0
```

### 2. Wait for MySQL to Start (about 10 seconds)
```bash
sleep 10
```

### 3. Create All Database Tables
```bash
cd makerspace-print-queue
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Final_SQL_Script.sql
```

---

## Daily Use

### Start Container (if stopped)
```bash
docker start mysql542
```

### Stop Container
```bash
docker stop mysql542
```

### Check if Container is Running
```bash
docker ps | grep mysql542
```

### View All Containers (running and stopped)
```bash
docker ps -a
```

---

## Database Management

### Connect to MySQL Shell
```bash
docker exec -it mysql542 mysql -uroot -ppass123 makerspace_db_final
```

Once inside, you can run SQL commands:
```sql
SHOW TABLES;
SELECT * FROM sign_ins;
SELECT * FROM print_jobs;
EXIT;
```

### Run SQL File
```bash
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < path/to/script.sql
```

### Run Single SQL Command
```bash
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; SHOW TABLES;"
```

### View Database Tables
```bash
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; SHOW TABLES;"
```

### Check Table Structure
```bash
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; DESCRIBE sign_ins;"
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; DESCRIBE print_jobs;"
```

---

## Backup & Restore

### Backup Database
```bash
docker exec mysql542 mysqldump -uroot -ppass123 makerspace_db_final > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < backup_20251212.sql
```

---

## Troubleshooting

### View Container Logs
```bash
docker logs mysql542
```

### Restart Container
```bash
docker restart mysql542
```

### Container Won't Start
```bash
# Check logs for errors
docker logs mysql542

# Remove and recreate
docker rm -f mysql542
docker run --name mysql542 -p 3307:3306 -e MYSQL_ROOT_PASSWORD=pass123 -e MYSQL_DATABASE=makerspace_db_final -d mysql:8.0
```

### Port Already in Use
```bash
# Find what's using port 3307
lsof -i :3307

# Or use a different port
docker run --name mysql542 -p 3308:3306 -e MYSQL_ROOT_PASSWORD=pass123 -e MYSQL_DATABASE=makerspace_db_final -d mysql:8.0
```

### Reset Everything (CAUTION: Deletes all data!)
```bash
# Stop and remove container
docker stop mysql542
docker rm mysql542

# Recreate from scratch
docker run --name mysql542 -p 3307:3306 -e MYSQL_ROOT_PASSWORD=pass123 -e MYSQL_DATABASE=makerspace_db_final -d mysql:8.0

# Wait for startup
sleep 10

# Recreate tables
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Final_SQL_Script.sql
```

---

## Understanding the Connection

**Container Details:**
- **Container Name**: `mysql542`
- **External Port**: `3307` (what your app connects to)
- **Internal Port**: `3306` (MySQL default)
- **Root Password**: `pass123`
- **Database Name**: `makerspace_db_final`

**Connection String** (in `.streamlit/secrets.toml`):
```toml
[db]
host = "127.0.0.1"
port = 3307
user = "root"
password = "pass123"
database = "makerspace_db_final"
```

---

## Common Error Fixes

### Error: "Table 'sign_ins' doesn't exist"
```bash
docker exec -i mysql542 mysql -uroot -ppass123 makerspace_db_final < sql/Add_Sign_In_And_Fiscal_Year.sql
```

### Error: "Unknown column 'fiscal_quarter'"
```bash
docker exec -i mysql542 mysql -uroot -ppass123 -e "USE makerspace_db_final; ALTER TABLE sign_ins ADD COLUMN fiscal_quarter INT NULL DEFAULT NULL AFTER fiscal_year;"
```

### Error: "Can't connect to MySQL server"
```bash
# Check if container is running
docker ps

# If not running, start it
docker start mysql542

# Wait a few seconds
sleep 5
```

---

## Production Notes

For production deployment, you should:
1. Use stronger passwords
2. Store credentials in environment variables or secrets manager
3. Set up regular backups
4. Use Docker volumes for data persistence
5. Consider using Docker Compose for easier management

Example with persistent volume:
```bash
docker run --name mysql542 \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=<strong-password> \
  -e MYSQL_DATABASE=makerspace_db_final \
  -v mysql_data:/var/lib/mysql \
  -d mysql:8.0
```
