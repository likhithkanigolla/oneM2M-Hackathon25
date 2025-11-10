#!/usr/bin/env python3
"""Create admin user script"""

import sys
import os
sys.path.append('/Users/likhithkanigolla/IIITH/code-files/Digital-Twin/Hackathon25/backend')

from app.database import get_db
from app.models.user import User
from app.auth import get_password_hash

def create_admin_user():
    """Create admin user if it doesn't exist"""
    db = next(get_db())
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == 'admin').first()
    if existing_admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin_user = User(
        username='admin',
        full_name='Administrator',
        password=get_password_hash('admin123'),
        role='admin'
    )
    
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    create_admin_user()