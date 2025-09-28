from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint("users", __name__, url_prefix="/users")

# --- User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# --- Register ---
@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"], method="pbkdf2:sha256")

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("users.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("users.register"))

        user = User(username=username, email=email, password=password, role="customer")
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! You can login now.", "success")
        return redirect(url_for("users.login"))

    return render_template("users/register.html")

# --- Login ---
@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password!", "danger")
            return redirect(url_for("users.login"))

        login_user(user)
        flash("Logged in successfully!", "success")

        # Redirect based on role
        if user.role == "admin":
            return redirect(url_for("users.admin_dashboard"))
        elif user.role == "seller":
            return redirect(url_for("users.seller_dashboard"))
        else:
            return redirect(url_for("users.customer_dashboard"))

    return render_template("users/login.html")

# --- Logout ---
@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))  # Redirect to home after logout

# --- Seller Dashboard ---
@users_bp.route("/seller/dashboard")
@login_required
def seller_dashboard():
    if current_user.role != "seller":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))
    from routes.products.products import Product
    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template("users/seller_dashboard.html", products=products)

# --- Customer Dashboard ---
@users_bp.route("/dashboard")
@login_required
def customer_dashboard():
    if current_user.role != "customer":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))
    return render_template("users/dashboard.html")

# --- Admin Dashboard ---
@users_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))
    return render_template("users/admin_dashboard.html")

# --- Admin: Manage Users ---
@users_bp.route("/manage_users")
@login_required
def admin_manage_users():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))
    users = User.query.all()
    return render_template("users/admin_users.html", users=users)

# --- Admin: Delete User ---
@users_bp.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    user = User.query.get(user_id)
    if user:
        if user.role == "admin":
            flash("You cannot delete another admin!", "danger")
            return redirect(url_for("users.admin_manage_users"))

        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")

    return redirect(url_for("users.admin_manage_users"))

# --- Flask-Login user loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
