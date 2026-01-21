"""
Database initialization script for TKR Chatbot
Run this to create the database and import the schema
"""
import pymysql
import os

# Database credentials
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Rajesh@2310'
DB_NAME = 'tkr_chatbot'

def init_database():
    """Initialize database and import schema"""
    try:
        # Connect to MySQL (without database)
        print("Connecting to MySQL...")
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Create database
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Database '{DB_NAME}' created successfully!")
        
        # Use the database
        cursor.execute(f"USE {DB_NAME}")
        
        # Read schema file
        schema_path = os.path.join('..', 'database', 'schema.sql')
        print(f"\nReading schema from {schema_path}...")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Remove comments and split by semicolon
        lines = []
        for line in schema_sql.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('--'):
                lines.append(line)
        
        # Join lines and split by semicolon
        clean_sql = ' '.join(lines)
        statements = [s.strip() for s in clean_sql.split(';') if s.strip()]
        
        print(f"Executing {len(statements)} SQL statements...")
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    # Skip USE database statements
                    if statement.upper().startswith('USE '):
                        continue
                    cursor.execute(statement)
                    # Get statement type for better logging
                    stmt_type = statement.split()[0].upper()
                    if stmt_type == 'CREATE':
                        if 'DATABASE' in statement.upper():
                            print(f"  [{i}/{len(statements)}] Database created")
                        else:
                            # Extract table name
                            parts = statement.upper().split()
                            if 'TABLE' in parts:
                                idx = parts.index('TABLE')
                                if idx + 1 < len(parts):
                                    table_name = parts[idx + 1].replace('IF', '').replace('NOT', '').replace('EXISTS', '').strip()
                                    print(f"  [{i}/{len(statements)}] Created table: {table_name}")
                    elif stmt_type == 'INSERT':
                        print(f"  [{i}/{len(statements)}] Inserted sample data")
                    else:
                        print(f"  [{i}/{len(statements)}] Executed {stmt_type}")
                except Exception as e:
                    # Skip if already exists
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        print(f"  [{i}/{len(statements)}] Already exists, skipping")
                    else:
                        print(f"  [{i}/{len(statements)}] Warning: {e}")
        
        connection.commit()
        print("\n✓ Schema imported successfully!")
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        print(f"\n✓ Sample data: {subject_count} subjects loaded")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*50)
        print("DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nYou can now:")
        print("1. Run 'python app.py' to start the backend")
        print("2. Open frontend/index.html in a browser")
        print("3. Start uploading materials and asking questions!")
        
        return True
        
    except pymysql.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except FileNotFoundError:
        print(f"\n✗ Schema file not found at {schema_path}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("="*50)
    print("TKR CHATBOT - DATABASE INITIALIZATION")
    print("="*50)
    print()
    
    success = init_database()
    
    if not success:
        print("\n⚠ Setup failed. Please check the error messages above.")
        exit(1)
