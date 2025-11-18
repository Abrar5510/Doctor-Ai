# Render Database Setup Guide for Doctor-AI

This guide explains how to set up and configure a PostgreSQL database on Render for the Doctor-AI application.

## Table of Contents
1. [Creating the Database on Render](#creating-the-database-on-render)
2. [Configuring Your Application](#configuring-your-application)
3. [Initializing the Database](#initializing-the-database)
4. [Uploading Data](#uploading-data)
5. [Environment Variables Configuration](#environment-variables-configuration)

---

## Creating the Database on Render

### Step 1: Sign In to Render
1. Go to https://dashboard.render.com/
2. Sign in or create a new account

### Step 2: Create PostgreSQL Database

1. Click the **"New +"** button in the top right
2. Select **"PostgreSQL"**

3. Configure your database:
   ```
   Name:                doctor-ai-db
   Database:            doctor_ai
   User:                doctor_ai_user
   Region:              Choose the same region as your web service
   PostgreSQL Version:  16 (or latest)
   Datadog API Key:     (leave empty unless you use Datadog)
   ```

4. Select a plan:
   - **Free** (Development/Testing):
     - 256 MB RAM
     - 1 GB Storage
     - Expires after 90 days
     - Perfect for development

   - **Starter** ($7/month - Recommended for Production):
     - 1 GB RAM
     - 10 GB Storage
     - Daily backups
     - No expiration
     - High availability

5. Click **"Create Database"**

### Step 3: Wait for Provisioning
- The database takes 2-3 minutes to provision
- You'll see a "Provisioning" status that will change to "Available"

### Step 4: Get Connection Details

Once the database is created, go to the database dashboard and find:

#### Internal Connection (for Render services in the same region):
```
Internal Database URL:
postgresql://doctor_ai_user:LONG_RANDOM_PASSWORD@dpg-xxxxx/doctor_ai
```

#### External Connection (for local development or external services):
```
External Database URL:
postgresql://doctor_ai_user:LONG_RANDOM_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai
```

You'll also see individual connection parameters:
- **Hostname**: `dpg-xxxxx.region-postgres.render.com`
- **Port**: `5432`
- **Database**: `doctor_ai`
- **Username**: `doctor_ai_user`
- **Password**: (long random string)

---

## Configuring Your Application

### Option 1: Local Development

Update your `.env` file:

```bash
# Use External Database URL for local development
DATABASE_URL=postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai
```

### Option 2: Render Web Service

1. Go to your Render Web Service dashboard
2. Click on **"Environment"** in the left sidebar
3. Add environment variable:
   ```
   Key:   DATABASE_URL
   Value: postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx/doctor_ai
   ```
   ⚠️ **Important**: Use the **Internal Database URL** for better performance and security

4. Click **"Save Changes"**
5. Your service will automatically redeploy

---

## Initializing the Database

### Method 1: From Local Machine

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set the database URL** in your `.env` file (use External URL):
   ```bash
   DATABASE_URL=postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai
   ```

3. **Run database migrations**:
   ```bash
   # Create all tables
   alembic upgrade head
   ```

4. **Initialize with default data**:
   ```bash
   python scripts/init_db.py
   ```

5. **Seed medical conditions data** (optional):
   ```bash
   python scripts/seed_data.py
   ```

### Method 2: Using Render Shell (Recommended for Production)

1. Go to your Render Web Service dashboard
2. Click **"Shell"** in the top menu
3. Run the following commands:
   ```bash
   # Upgrade database schema
   alembic upgrade head

   # Initialize database
   python scripts/init_db.py

   # Seed medical conditions (optional)
   python scripts/seed_data.py
   ```

### Method 3: Using psql (Direct Database Connection)

1. **Install PostgreSQL client** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql-client

   # macOS
   brew install postgresql
   ```

2. **Connect to Render database**:
   ```bash
   psql "postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai"
   ```

3. You can now run SQL commands directly

---

## Uploading Data

### Option 1: Using Python Scripts (Recommended)

Our application includes scripts to populate the database:

```bash
# 1. Initialize database schema and create admin user
python scripts/init_db.py

# 2. Seed medical conditions data
python scripts/seed_data.py
```

**What gets created:**
- Database tables (users, sessions, audit logs, etc.)
- Default admin user:
  - Username: `admin`
  - Password: `ChangeMe123!@#` (⚠️ CHANGE THIS IMMEDIATELY!)
  - Email: `admin@doctor-ai.local`
- Sample medical conditions for testing

### Option 2: Import SQL Dump

If you have an existing SQL dump:

```bash
# From local machine
psql "postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai" < backup.sql

# Or using pg_restore for custom format dumps
pg_restore -h dpg-xxxxx.region-postgres.render.com \
  -U doctor_ai_user \
  -d doctor_ai \
  -v backup.dump
```

### Option 3: Using Render Dashboard

1. Go to your database dashboard on Render
2. Click **"Backups"** tab
3. You can restore from a backup file

---

## Environment Variables Configuration

### Complete `.env` Example for Render

```bash
# Application Settings
APP_NAME="Medical Symptom Constellation Mapper"
APP_VERSION="0.2.0"
DEBUG=False
LOG_LEVEL=INFO

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Security
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_AT_LEAST_32_CHARS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=https://your-frontend.onrender.com,https://your-domain.com
CORS_ALLOW_CREDENTIALS=True

# Database (Use Internal URL for Render services)
DATABASE_URL=postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx/doctor_ai
DATABASE_ECHO=False

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=medical_conditions

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ML Models
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
EMBEDDING_DIMENSION=768
MAX_SEQUENCE_LENGTH=512

# AI Assistant (Optional - can be provided by users)
OPENAI_API_KEY=
USE_OPENROUTER=False
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
USE_LOCAL_LLM=False
LOCAL_LLM_MODEL=llama2

# Feature Flags
ENABLE_RARE_DISEASE_DETECTION=True
ENABLE_RED_FLAG_ALERTS=True
ENABLE_TEMPORAL_ANALYSIS=True
ENABLE_AI_ASSISTANT=True
```

### Setting Environment Variables on Render

1. Go to your Web Service dashboard
2. Navigate to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add each variable one by one
5. Click **"Save Changes"**

**Critical Variables for Render:**
- `DATABASE_URL` - Your Render PostgreSQL connection string
- `SECRET_KEY` - Generate using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `CORS_ORIGINS` - Your frontend URL(s)
- `DEBUG` - Set to `False` for production

---

## Database Migrations

### Creating New Migrations

When you modify database models:

```bash
# Generate a new migration
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file in alembic/versions/

# Apply the migration
alembic upgrade head
```

### Applying Migrations on Render

After pushing migration files to your repository:

1. Render will automatically redeploy your service
2. Add a build command in Render dashboard:
   ```bash
   alembic upgrade head && python scripts/init_db.py
   ```

Or run manually via Render Shell:
```bash
alembic upgrade head
```

---

## Backup and Restore

### Manual Backup

```bash
# Create a backup
pg_dump "postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai" > backup_$(date +%Y%m%d).sql
```

### Automatic Backups (Starter Plan and Above)

Render provides automatic daily backups:
1. Go to your database dashboard
2. Click **"Backups"** tab
3. View and restore from available backups

### Restore from Backup

```bash
psql "postgresql://doctor_ai_user:YOUR_PASSWORD@dpg-xxxxx.region-postgres.render.com/doctor_ai" < backup_20241118.sql
```

---

## Troubleshooting

### Connection Issues

1. **Timeout errors**: Use the External URL for connections outside Render
2. **Authentication failed**: Double-check your password (copy directly from Render dashboard)
3. **SSL errors**: Render requires SSL. Add `?sslmode=require` to connection string if needed:
   ```
   postgresql://user:pass@host/db?sslmode=require
   ```

### Database Initialization Fails

1. Check logs: `alembic upgrade head --sql` to see what SQL will run
2. Verify DATABASE_URL is correct
3. Ensure database is empty or run: `alembic downgrade base` first

### Performance Issues

1. Monitor database metrics in Render dashboard
2. Consider upgrading to a larger plan
3. Add database indexes for frequently queried fields
4. Enable connection pooling in your application

---

## Security Best Practices

1. **Never commit `.env` files** - They're gitignored by default
2. **Use Internal URLs** when connecting from Render services
3. **Rotate passwords regularly** - Can be done from Render dashboard
4. **Use strong SECRET_KEY** - Generate cryptographically secure keys
5. **Enable SSL** - Always use `sslmode=require` for external connections
6. **Limit database access** - Only allow connections from trusted IPs if possible
7. **Change default admin password** - Run after first initialization:
   ```python
   python -c "from src.utils.password import hash_password; print(hash_password('your_new_secure_password'))"
   ```

---

## Next Steps

1. ✅ Create Render PostgreSQL database
2. ✅ Configure DATABASE_URL in environment variables
3. ✅ Run migrations: `alembic upgrade head`
4. ✅ Initialize database: `python scripts/init_db.py`
5. ✅ Seed data: `python scripts/seed_data.py`
6. ✅ Change default admin password
7. ✅ Deploy your application to Render
8. ✅ Test database connectivity
9. ✅ Set up automatic backups (Starter plan)
10. ✅ Monitor database performance

---

## Support

- Render Documentation: https://render.com/docs/databases
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Alembic Documentation: https://alembic.sqlalchemy.org/

For project-specific issues, check the main README.md or open an issue on GitHub.
