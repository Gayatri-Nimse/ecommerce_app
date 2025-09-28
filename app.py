from flask import Flask, render_template
from extensions import db, login_manager  
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
login_manager.init_app(app)


from routes.users.users import users_bp
from routes.products.products import products_bp
from routes.orders.orders import orders_bp

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(orders_bp, url_prefix="/orders")

# -----------------------------
# User loader for Flask-Login
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    from routes.users.users import User
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == "__main__":
    with app.app_context():

        from routes.users.users import User
        from routes.products.products import Product
        from routes.orders.orders import Order

        # Create tables if not exist
        db.create_all()


    app.run(debug=True)



