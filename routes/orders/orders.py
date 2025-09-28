from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from routes.products.products import Product

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

# --- Order Model ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# --- Place Order (Customer) ---
@orders_bp.route("/place/<int:product_id>", methods=["POST"])
@login_required
def place_order(product_id):
    if current_user.role != "customer":
        flash("Only customers can place orders!", "danger")
        return redirect(url_for("users.login"))

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("products.all_products"))

    order = Order(customer_id=current_user.id, product_id=product.id, quantity=1)
    db.session.add(order)
    db.session.commit()
    flash("Order placed successfully!", "success")
    return redirect(url_for("orders.my_orders"))


# --- Customer: My Orders ---
@orders_bp.route("/my_orders")
@login_required
def my_orders():
    if current_user.role != "customer":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    orders = Order.query.filter_by(customer_id=current_user.id).all()
    order_list = []
    for o in orders:
        product = Product.query.get(o.product_id)
        order_list.append({
            "id": o.id,
            "product_name": product.name if product else "Unknown",
            "quantity": o.quantity
        })

    return render_template("orders/customer_orders.html", orders=order_list)


# --- Admin: View All Orders ---
@orders_bp.route("/all")
@login_required
def all_orders():
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    from routes.users.users import User

    orders = Order.query.all()
    order_list = []
    for o in orders:
        customer = User.query.get(o.customer_id)
        product = Product.query.get(o.product_id)
        order_list.append({
            "id": o.id,
            "customer_name": customer.username if customer else "Unknown",
            "product_name": product.name if product else "Unknown",
            "quantity": o.quantity
        })

    return render_template("orders/admin_orders.html", orders=order_list)


# --- Admin: Delete Order ---
@orders_bp.route("/delete/<int:order_id>")
@login_required
def delete_order(order_id):
    if current_user.role != "admin":
        flash("Access denied!", "danger")
        return redirect(url_for("users.login"))

    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash("Order deleted successfully!", "success")

    return redirect(url_for("orders.all_orders"))




