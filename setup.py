from extensions import db
from app import app
from routes.users.users import User
from routes.products.products import Product
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1️⃣ Create all tables (safe to run multiple times)
    db.create_all()

    # 2️⃣ Add Admin only if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin"
        )
        db.session.add(admin)

    # 3️⃣ Add Seller only if not exists
    if not User.query.filter_by(username="seller1").first():
        seller = User(
            username="seller1",
            email="seller1@example.com",
            password=generate_password_hash("seller123", method="pbkdf2:sha256"),
            role="seller"
        )
        db.session.add(seller)

    db.session.commit()
    print("✅ Setup completed! Tables created and Admin/Seller added safely.")
