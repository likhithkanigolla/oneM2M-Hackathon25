"""
Migration script to update the database schema.

This script adds new columns to existing tables to support the enhanced features.
Run this before using the updated application if you have an existing database.

Usage:
    python migrate_db.py
"""

from app.database import engine
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_scenarios_table():
    """Add priority, trigger, and impact columns to scenarios table if they don't exist"""
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('scenarios')]
    
    with engine.begin() as conn:
        if 'priority' not in existing_columns:
            logger.info("Adding priority column to scenarios table")
            conn.execute(text("ALTER TABLE scenarios ADD COLUMN priority VARCHAR DEFAULT 'Medium'"))
        
        if 'trigger' not in existing_columns:
            logger.info("Adding trigger column to scenarios table")
            conn.execute(text("ALTER TABLE scenarios ADD COLUMN trigger VARCHAR"))
            
        if 'impact' not in existing_columns:
            logger.info("Adding impact column to scenarios table")
            conn.execute(text("ALTER TABLE scenarios ADD COLUMN impact VARCHAR"))

def migrate_users_table():
    """Update users table to match new schema"""
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    
    with engine.begin() as conn:
        if 'full_name' not in existing_columns:
            logger.info("Adding full_name column to users table")
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
            
        if 'role' not in existing_columns:
            logger.info("Adding role column to users table")
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'operator'"))
            
        if 'is_active' not in existing_columns:
            logger.info("Adding is_active column to users table")
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            
        if 'assigned_rooms' not in existing_columns:
            logger.info("Adding assigned_rooms column to users table")
            conn.execute(text("ALTER TABLE users ADD COLUMN assigned_rooms JSON"))
            
        if 'created_at' not in existing_columns:
            logger.info("Adding created_at column to users table")
            conn.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW()"))

def update_scenario_data():
    """Update existing scenarios with priority, trigger, and impact data"""
    logger.info("Updating scenario data with new fields")
    
    with engine.begin() as conn:
        # Update Meeting Priority scenario
        conn.execute(text("""
            UPDATE scenarios SET 
                priority = 'High',
                trigger = 'Meeting detected + time block',
                impact = 'Comfort +15%'
            WHERE name = 'Meeting Priority'
        """))
        
        # Update Energy Shortage scenario  
        conn.execute(text("""
            UPDATE scenarios SET 
                priority = 'Critical',
                trigger = 'Power consumption > 80%',
                impact = 'Energy -25%'
            WHERE name = 'Energy Shortage'
        """))
        
        # Update System Active scenario
        conn.execute(text("""
            UPDATE scenarios SET 
                priority = 'Low',
                trigger = 'Default operation state',
                impact = 'Balanced operation'
            WHERE name = 'System Active'
        """))

def update_user_data():
    """Update existing users with new schema data"""
    logger.info("Updating user data with new fields")
    
    with engine.begin() as conn:
        # Update admin user
        conn.execute(text("""
            UPDATE users SET 
                full_name = 'System Administrator',
                role = 'admin',
                is_active = TRUE,
                assigned_rooms = '[1,2,3,4]'
            WHERE username = 'admin'
        """))
        
        # Update operator user
        conn.execute(text("""
            UPDATE users SET 
                full_name = 'System Operator',
                role = 'operator',
                is_active = TRUE,
                assigned_rooms = '[1,2]'
            WHERE username = 'operator'
        """))

def migrate_slos_table():
    """Update SLOs table to include weight and active columns"""
    logger.info("Migrating SLOs table")
    
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('slos')]
    
    with engine.begin() as conn:
        if 'weight' not in existing_columns:
            logger.info("Adding weight column to slos table")
            conn.execute(text("ALTER TABLE slos ADD COLUMN weight FLOAT DEFAULT 0.1"))
            
        if 'active' not in existing_columns:
            logger.info("Adding active column to slos table")
            conn.execute(text("ALTER TABLE slos ADD COLUMN active BOOLEAN DEFAULT TRUE"))

def update_slo_data():
    """Update existing SLO data with default weights"""
    logger.info("Updating SLO data with weights")
    
    with engine.begin() as conn:
        # Set reasonable default weights for existing SLOs
        conn.execute(text("""
            UPDATE slos SET 
                weight = 0.33,
                active = TRUE
            WHERE name = 'Comfort' AND weight IS NULL
        """))
        
        conn.execute(text("""
            UPDATE slos SET 
                weight = 0.33,
                active = TRUE
            WHERE name = 'Energy Efficiency' AND weight IS NULL
        """))
        
        conn.execute(text("""
            UPDATE slos SET 
                weight = 0.34,
                active = TRUE
            WHERE name = 'Reliability' AND weight IS NULL
        """))

def main():
    """Run all migrations"""
    logger.info("Starting database migration...")
    
    try:
        migrate_scenarios_table()
        migrate_users_table()
        migrate_slos_table()
        update_scenario_data()
        update_user_data()
        update_slo_data()
        
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()