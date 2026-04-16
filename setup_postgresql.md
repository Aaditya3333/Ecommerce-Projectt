# PostgreSQL Setup Instructions

## 1. Install PostgreSQL (if not already installed)

### Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and note the password you set for the postgres user
3. Make sure PostgreSQL is running as a service

### Alternative (using Docker):
```bash
docker run --name postgres-db -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:latest
```

## 2. Create the Database

### Method 1: Using pgAdmin (GUI)
1. Open pgAdmin that comes with PostgreSQL installation
2. Connect to the PostgreSQL server using:
   - Host: localhost
   - Port: 5432
   - Username: postgres
   - Password: (the password you set during installation)
3. Right-click on "Databases" and select "Create" > "Database"
4. Enter database name: `aaditya_store_db`
5. Click "Save"

### Method 2: Using psql (Command Line)
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create the database
CREATE DATABASE aaditya_store_db;

# Exit psql
\q
```

## 3. Update Django Settings

The settings.py file has already been updated with:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aaditya_store_db',
        'USER': 'postgres',
        'PASSWORD': 'password',  # Update this with your actual password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Important**: Update the 'PASSWORD' field in settings.py with your actual PostgreSQL password.

## 4. Test the Connection

After setting up the database, run these commands to test:

```bash
# Activate virtual environment
venv\Scripts\activate

# Test database connection
python manage.py check

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

## 5. Troubleshooting

### Common Issues:

1. **Connection Refused**:
   - Make sure PostgreSQL service is running
   - Check if port 5432 is available
   - Verify firewall settings

2. **Authentication Failed**:
   - Double-check the password in settings.py
   - Make sure the postgres user exists

3. **Database Doesn't Exist**:
   - Verify the database name is exactly 'aaditya_store_db'
   - Check if you have permissions to create databases

4. **psycopg2 errors**:
   - Make sure psycopg2-binary is installed: `pip install psycopg2-binary`

## 6. Benefits of PostgreSQL over SQLite

- Better performance for larger datasets
- Concurrent access support
- Advanced features (triggers, stored procedures, etc.)
- Better security and user management
- More reliable for production use
- Better backup and restore options

## 7. Next Steps

Once PostgreSQL is set up and working:
1. Run `python manage.py makemigrations` (if you have new migrations)
2. Run `python manage.py migrate` to create tables
3. Create a superuser with `python manage.py createsuperuser`
4. Test the application to ensure everything works
