#!/usr/bin/python3
from logging.config import dictConfig

import psycopg
import datetime
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

    return render_template("homepage.html", current_page="homepage" , page_title="Homepage", session=session , cart_items=cart_items)

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

    return render_template("customer/customers.html", customers=cur, current_page="customers", page_title="Customers", session=session , cart_items=cart_items)

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

    return render_template("products/products.html", current_page="products", page_title="Products", products=cur , session=session , cart_items=cart_items )

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
@app.route("/order", methods=("GET",))
def order():
    """Show the index page."""
    # Check if the user is logged in
    if 'customer' not in session:
        flash("You need to log in to checkout")
        return redirect('/login')

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
    
    return render_template("orders/order.html", current_page="order", page_title="Available for Order", products=cur, cart_items=cart_items, messages=messages, session = session)

@app.route("/orders", methods=("GET",))
def orders():
    """Show all orders for customer"""
    # Resto do código...

    # Get all orders for customer
    with pool.connection() as conn:
        cur = conn.cursor(row_factory=namedtuple_row)
        cur.execute(
            """
            SELECT * FROM orders WHERE cust_no = %(cust_no)s;
            """,
            {"cust_no": session['customer'][0]},
        )
        log.debug(f"Found {cur.rowcount} rows.")
        orders = cur.fetchall()  # Recupera todos os resultados da consulta

    # Get all payed orders for customer
    with pool.connection() as conn:
        cur1 = conn.cursor(row_factory=namedtuple_row)
        cur1.execute(
            """
            SELECT * FROM pay WHERE cust_no = %(cust_no)s;
            """,
            {"cust_no": session['customer'][0]},
        )
        log.debug(f"Found {cur1.rowcount} rows.")
        payed_orders = cur1.fetchall()  # Recupera todos os resultados da consulta

    return render_template("orders/orders.html", current_page="orders", page_title="Your Orders", orders=orders, payed_orders= [order.order_no for order in payed_orders], session = session, cart_items=cart_items)

@app.route("/cart", methods=("GET",))
def cart():
    flash(session)
    message = get_flash_messages()
    return render_template("orders/cart.html", current_page="cart", page_title="Your Cart", cart_items=cart_items, message=message , session=session)

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

    return redirect('/order') 

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    
    # Check if the user is logged in
    if 'customer' not in session:
        flash("You need to log in to checkout")
        return redirect('/login')
    

    current_date = datetime.date.today()  # Obtém a data atual

    # Create a new order
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("SELECT MAX(order_no) FROM orders")
            max_order_no = cur.fetchone()[0]
            order_no = max_order_no + 1 if max_order_no != None else 1
            cur.execute("INSERT INTO orders (order_no, cust_no, date) VALUES (%(order_no)s, %(cust_no)s, %(date)s)", {"order_no": order_no, "cust_no": session['customer'][0], "date": current_date})
            log.debug(f"Inserted {cur.rowcount} rows.")
    
    # Add the products to the order
    for item in cart_items['items']:
        with pool.connection() as conn:
            with conn.cursor(row_factory=namedtuple_row) as cur:
                cur.execute("INSERT INTO contains (order_no, SKU, QTY) VALUES (%(order_no)s, %(SKU)s, %(QTY)s)", {"order_no": order_no, "SKU": item['sku'], "QTY": item['quantity']})
                log.debug(f"Inserted {cur.rowcount} rows.")

    # Clear the cart
    cart_items['items'] = []
    cart_items['total_price'] = 0
    cart_items['total_items'] = 0

    return redirect('/orders')

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    order_no = request.form.get('order_no')
    cust_no = request.form.get('cust_no')

    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            cur.execute("INSERT INTO pay (order_no, cust_no) VALUES (%(order_no)s, %(cust_no)s)", {"order_no": order_no, "cust_no": cust_no}) 
            log.debug(f"Inserted {cur.rowcount} rows.")

    return redirect('/orders')

@app.route('/login', methods=['GET', 'POST'])
def login():
    messages= get_flash_messages()
    message = messages[0][1] if len(messages) > 0 else None
    if request.method == 'POST':
        email = request.form.get('email')

        with pool.connection() as conn:
            with conn.cursor(row_factory=namedtuple_row) as cur:
                cur.execute("SELECT * FROM customer WHERE email = %(email)s ", {"email": email})
                log.debug(f"Found {cur.rowcount} rows.")
                customer = cur.fetchone()
                if customer != None:
                    session['customer'] = customer
                    return redirect('/order')
                else:
                    flash("Invalid email: " + email)
                    return redirect('/login')
    else:
        return render_template('customer/login.html', current_page="login", page_title="login", message=message)


if __name__ == "__main__":
    app.run()
