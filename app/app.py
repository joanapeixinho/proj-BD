#!/usr/bin/python3
from logging.config import dictConfig

import psycopg
import json
from flask import flash
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from urllib.request import urlopen
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool


# postgres://{user}:{password}@{hostname}:{port}/{database-name}
DATABASE_URL = "postgres://db:db@postgres/db"

# Create a connection pool to the database.
pool = ConnectionPool(conninfo=DATABASE_URL)
# the pool starts connecting immediately.

cart_items = {'total_price': 0, 'total_items':0, 'items': []}


dictConfig(
    {
        "version": 1,

        # errors log formats
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },

        # handlers define where the log is written
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },

        # root defines the default logging level
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

# creates the flask app itself
app = Flask(__name__)

# object to log messages to
log = app.logger
app.secret_key = 'super secret key'

def get_flash_messages():
    messages = session.pop('_flashes', [])
    return messages


# testing templates
@app.route("/test", methods=("GET",))
def test():
    """Show the index page."""

    return render_template("test.html")


# HOME PAGE
@app.route("/", methods=("GET",))
def homepage():
    """Show the index page."""

    return render_template("homepage.html", current_page="homepage" , page_title="Homepage")

# CUSTOMERS PAGE
@app.route("/customers", methods=("GET",))
def customers():
    """Show all the accounts, most recent first."""

    with pool.connection() as conn:
        cur = conn.cursor(row_factory=namedtuple_row)
        cur.execute(

                """
                SELECT * FROM customer;
                """,
                {},
            )
        log.debug(f"Found {cur.rowcount} rows.")

    # API-like response is returned to clients that request JSON explicitly (e.g., fetch)
    if (
        request.accept_mimetypes["application/json"]
        and not request.accept_mimetypes["text/html"]
    ):
        return jsonify(cur)

    return render_template("customer/customers.html", customers=cur, current_page="customers", page_title="Customers")

# CREATE CUSTOMER
@app.route('/create-customer', methods=['POST'])
def create_customer():
    # Obtenha os dados do formulário enviado
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("SELECT MAX(cust_no) FROM CUSTOMER")
            max_cust_no = cur.fetchone()[0]
            
            # (Miguel speaking) In case the table is empty and you try to add a customer
            if max_cust_no == None:
                max_cust_no = 0
            
            cust_no = max_cust_no + 1
            cur.execute("INSERT INTO customer (cust_no, name, email, phone, address) VALUES (%(cust_no)s, %(name)s, %(email)s, %(phone)s, %(address)s)", {"cust_no": cust_no, "name": name, "email": email, "phone": phone, "address": address})
            log.debug(f"Inserted {cur.rowcount} rows.")

    return redirect('/customers')

# DELETE CUSTOMER
@app.route('/delete-customer', methods=['POST'])
def delete_customer():
    cust_no = request.form['cust_no']
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("DELETE FROM contains WHERE order_no IN (SELECT order_no FROM orders WHERE cust_no = %(cust_no)s)", {"cust_no": cust_no})
            cur.execute("DELETE FROM pay WHERE order_no IN (SELECT order_no FROM orders WHERE cust_no = %(cust_no)s)", {"cust_no": cust_no})
            cur.execute("DELETE FROM process WHERE order_no IN (SELECT order_no FROM orders WHERE cust_no = %(cust_no)s)", {"cust_no": cust_no})
            cur.execute("DELETE FROM orders WHERE cust_no = %(cust_no)s", {"cust_no": cust_no})
            cur.execute("DELETE FROM customer WHERE cust_no = %(cust_no)s", {"cust_no": cust_no})

            log.debug(f"Deleted {cur.rowcount} rows.")
    
    return redirect('/customers')

# SUPPLIERS PAGE
@app.route("/suppliers", methods=("GET",))
def suppliers():
    """Show the suppliers page."""

    messages = get_flash_messages()

    with pool.connection() as conn:
        cur = conn.cursor(row_factory=namedtuple_row)
        cur.execute(
                """
                SELECT * FROM supplier;
                """,
                {},
            )
        log.debug(f"Found {cur.rowcount} rows.")

    # API-like response is returned to clients that request JSON explicitly (e.g., fetch)
    if (
        request.accept_mimetypes["application/json"]
        and not request.accept_mimetypes["text/html"]
    ):
        return jsonify(cur)

    return render_template("supplier/supplier.html", current_page="suppliers", page_title="Suppliers", suppliers=cur, messages=messages)

# CREATE SUPPLIER
@app.route('/create-supplier', methods=['POST'])
def create_supplier():

    # Obtenha os dados do formulário enviado
    TIN = request.form.get('TIN')
    name = request.form.get('name')
    address = request.form.get('address')
    SKU = request.form.get('SKU')
    date = request.form.get('date')

    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            while True:
                
                cur.execute("SELECT TIN FROM supplier WHERE TIN = %(TIN)s", {"TIN": TIN})
                if cur.fetchone() != None:
                    flash("TIN already registed. Supplier not created.")
                    break

                cur.execute("SELECT SKU FROM product WHERE SKU = %(SKU)s", {"SKU": SKU})
                if cur.fetchone() == None:
                    flash("SKU does not exist. Supplier not created.")
                    break

                cur.execute("INSERT INTO supplier (TIN, name, address, SKU, date) VALUES (%(TIN)s, %(name)s, %(address)s, %(SKU)s, %(date)s)", {"TIN": TIN, "name": name, "address": address, "SKU": SKU, "date": date})
                log.debug(f"Inserted {cur.rowcount} rows.")
                break

    return redirect('/suppliers')

# EDIT PRODUCT
@app.route('/edit-product', methods=['POST'])
def edit_product():
    # Obtenha os dados do formulário enviado
    sku = request.form['sku']
    description = request.form.get('description')
    price = request.form.get('price')
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("UPDATE product SET description = %(description)s, price = %(price)s WHERE sku = %(sku)s", {"sku": sku, "description": description, "price": price})
            
            log.debug(f"Deleted {cur.rowcount} rows.")
    
    
    return redirect('/products')

# DELETE SUPPLIER
@app.route('/delete-supplier', methods=['POST'])
def delete_supplier():
    TIN = request.form['TIN']
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("DELETE FROM delivery WHERE TIN = %(TIN)s", {"TIN": TIN})
            cur.execute("DELETE FROM supplier WHERE TIN = %(TIN)s", {"TIN": TIN})

            log.debug(f"Deleted {cur.rowcount} rows.")
    
    return redirect('/suppliers')

# PRODUCTS PAGE
@app.route("/products", methods=("GET",))
def products():
    """Show the products page."""

    with pool.connection() as conn:
        cur = conn.cursor(row_factory=namedtuple_row)
        cur.execute(
                """
                SELECT * FROM product ORDER BY sku;
                """,
                {},
            )
        log.debug(f"Found {cur.rowcount} rows.")

    # API-like response is returned to clients that request JSON explicitly (e.g., fetch)
    if (
        request.accept_mimetypes["application/json"]
        and not request.accept_mimetypes["text/html"]
    ):
        return jsonify(cur)

    return render_template("products/products.html", current_page="products", page_title="Products", products=cur )

# CREATE PRODUCT
@app.route('/create-product', methods=['POST'])
def create_product():
    # Obtenha os dados do formulário enviado
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    ean = request.form.get('ean')

    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("SELECT MAX(CAST(SUBSTRING(sku, 4) AS INT)) FROM product")
            max_sku = cur.fetchone()[0]
            
            # If the table is empty, set max_sku to 0
            if max_sku == None:
                max_sku = 0
            sku_n = max_sku + 1 
                
            sku = "SKU" + str(sku_n)
            cur.execute("INSERT INTO product (sku, name, description, price, ean) VALUES (%(sku)s, %(name)s, %(description)s, %(price)s, %(ean)s)", {"sku": sku, "name": name, "description": description, "price": price, "ean": ean})
            log.debug(f"Inserted {cur.rowcount} rows.")

    return redirect('/products')

# DELETE PRODUCT
@app.route('/delete-product', methods=['POST'])
def delete_product():
    sku = request.form['sku']
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("DELETE FROM contains WHERE sku IN (SELECT sku FROM product WHERE sku = %(sku)s)", {"sku": sku})
            
            # In case we are deleting the last product in an order, we need to delete the orders, pay and process tables
            cur.execute("DELETE FROM process WHERE order_no NOT IN (SELECT order_no FROM contains)")
            cur.execute("DELETE FROM pay WHERE order_no NOT IN (SELECT order_no FROM contains)")
            cur.execute("DELETE FROM orders WHERE order_no NOT IN (SELECT order_no FROM contains)")
            
            cur.execute("UPDATE supplier SET sku = NULL WHERE sku = %(sku)s", {"sku": sku})
            cur.execute("DELETE FROM product WHERE sku = %(sku)s", {"sku": sku})
            

            log.debug(f"Deleted {cur.rowcount} rows.")
    
    
    return redirect('/products')

# ORDERS PAGE
@app.route("/orders", methods=("GET",))
def orders():
    """Show the index page."""

    messages = get_flash_messages()  
    
    with pool.connection() as conn:
        cur = conn.cursor(row_factory=namedtuple_row)
        cur.execute(
                """
                SELECT * FROM product;
                """,
                {},
            )
        log.debug(f"Found {cur.rowcount} rows.")

    # API-like response is returned to clients that request JSON explicitly (e.g., fetch)
    if (
        request.accept_mimetypes["application/json"]
        and not request.accept_mimetypes["text/html"]
    ):
        return jsonify(cur)
    
    return render_template("orders/orders.html", current_page="orders", page_title="Available for Order", products=cur, cart_items=cart_items, messages=messages )

@app.route("/cart", methods=("GET",))
def cart():
    

    return render_template("orders/cart.html", current_page="cart", page_title="Your Cart", cart_items=cart_items)

@app.route("/remove_from_cart",methods=['POST'])
def remove_from_cart():
    sku = request.form['sku_to_remove']
    #remove item from cart
    for item in cart_items['items']:
        if item['sku'] == sku:
            price = item['price_for_qty']
            quantity = item['quantity']
            cart_items['items'].remove(item)
            break
    else:
        flash("Item not found in cart")
        return redirect('/cart')
    
    #update cart total price and total items
    cart_items['total_price'] -= price
    cart_items['total_items'] -= quantity

    return redirect('/cart')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    sku = request.form.get('sku')
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price')) * quantity

    
    for item in cart_items['items']:
        # Update existing product quantity and price for it
        if item['sku'] == sku:
            item['quantity'] += quantity
            item ['price_for_qty'] += price 
            break
    else:
        # Add new product to cart
        cart_items['items'].append({'sku': sku, 'quantity': quantity, 'price_for_qty': price, 'name': request.form.get('name')})
        
    cart_items['total_price'] += price
    cart_items['total_items'] += quantity

    flash("added" + str(quantity) +  "items to cart sucessfully")

    return redirect('/orders') 


# @app.route("/accounts/<account_number>/update", methods=("GET", "POST"))
# def account_update(account_number):
#     """Update the account balance."""

#     with pool.connection() as conn:
#         with conn.cursor(row_factory=namedtuple_row) as cur:
#             account = cur.execute(
#                 """
#                 SELECT account_number, branch_name, balance
#                 FROM account
#                 WHERE account_number = %(account_number)s;
#                 """,
#                 {"account_number": account_number},
#             ).fetchone()
#             log.debug(f"Found {cur.rowcount} rows.")
#here its professor's code

#     if request.method == "POST":
#         balance = request.form["balance"]

#         error = None

#         if not balance:
#             error = "Balance is required."
#             if not balance.isnumeric():
#                 error = "Balance is required to be numeric."

#         if error is not None:
#             flash(error)
#         else:
#             with pool.connection() as conn:
#                 with conn.cursor(row_factory=namedtuple_row) as cur:
#                     cur.execute(
#                         """
#                         UPDATE account
#                         SET balance = %(balance)s
#                         WHERE account_number = %(account_number)s;
#                         """,
#                         {"account_number": account_number, "balance": balance},
#                     )
#                 conn.commit()
#             return redirect(url_for("account_index"))

#     return render_template("account/update.html", account=account)

# @app.route("/ping", methods=("GET",))
# def ping():
#     log.debug("ping!")
#     return jsonify({"message": "pong!", "status": "success"})


if __name__ == "__main__":
    app.run()
