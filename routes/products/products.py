from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db

products_bp = Blueprint("products", __name__, url_prefix="/products")

# --- Product Model ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)


# --- Seller: Add Product ---
@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role != "seller":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])

        product = Product(name=name, price=price, stock=stock, seller_id=current_user.id)
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("products.seller_dashboard_products"))

    return render_template("products/add_product.html")


# --- Seller: Edit Product ---
@products_bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if current_user.role != "seller":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    product = Product.query.get(product_id)
    if not product or product.seller_id != current_user.id:
        flash("Product not found or access denied!", "danger")
        return redirect(url_for("products.seller_dashboard_products"))

    if request.method == "POST":
        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.stock = int(request.form["stock"])
        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for("products.seller_dashboard_products"))

    return render_template("products/edit_product.html", product=product)


# --- Seller: View Own Products ---
@products_bp.route("/seller")
@login_required
def seller_dashboard_products():
    if current_user.role != "seller":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template("products/seller_products.html", products=products)


# --- Customer & Admin: View All Products ---
@products_bp.route("/all")
@login_required
def all_products():
    if current_user.role not in ["customer", "admin"]:
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    products = Product.query.all()
    return render_template("products/all_products.html", products=products)


# --- Delete Product (Admin/Seller) ---
@products_bp.route("/delete/<int:product_id>")
@login_required
def delete_product(product_id):
    if current_user.role not in ["seller", "admin"]:
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!", "danger")
        return redirect(request.referrer or url_for("products.all_products"))

    # Seller can delete only their own products
    if current_user.role == "seller" and product.seller_id != current_user.id:
        flash("Access denied!", "danger")
        return redirect(url_for("products.seller_dashboard_products"))

    # Admin can delete any product
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")

    # Redirect based on role
    if current_user.role == "admin":
        return redirect(url_for("products.all_products"))
    else:
        return redirect(url_for("products.seller_dashboard_products"))








