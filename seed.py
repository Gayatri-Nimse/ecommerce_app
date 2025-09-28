from extensions import db
from app import app
from routes.users.users import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create Admin
    admin = User(
        username="admin",
        email="admin@example.com",
        password=generate_password_hash("admin123", method="pbkdf2:sha256"),
        role="admin"
    )
    # Create Seller
    seller = User(
        username="seller1",
        email="seller1@example.com",
        password=generate_password_hash("seller123", method="pbkdf2:sha256"),
        role="seller"
    )

    db.session.add(admin)
    db.session.add(seller)
    db.session.commit()

    print("✅ Admin and Seller added successfully!")

