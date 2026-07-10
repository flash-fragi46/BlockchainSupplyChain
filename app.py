from flask import Flask, render_template, request
import sqlite3
import hashlib
import qrcode
import os

from blockchain import Blockchain

app = Flask(__name__)

DATABASE = "database/supplychain.db"

blockchain = Blockchain()


def get_connection():
    return sqlite3.connect(DATABASE)


def save_transaction(product_id, sender, receiver, location):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT hash
    FROM transactions
    WHERE product_id=?
    ORDER BY tx_id DESC
    LIMIT 1
    """, (product_id,))

    last = cursor.fetchone()

    previous_hash = "0000"

    if last:
        previous_hash = last[0]

    block = blockchain.create_transaction(
        product_id,
        sender,
        receiver,
        location,
        previous_hash
    )

    cursor.execute("""
    INSERT INTO transactions
    (
        product_id,
        sender,
        receiver,
        location,
        timestamp,
        hash,
        previous_hash
    )
    VALUES (?,?,?,?,?,?,?)
    """,
    (
        block["product_id"],
        block["sender"],
        block["receiver"],
        block["location"],
        block["timestamp"],
        block["hash"],
        block["previous_hash"]
    ))

    conn.commit()
    conn.close()
# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- FARMER ----------------

@app.route("/farmer", methods=["GET", "POST"])
def farmer():

    if request.method == "POST":

        product_id = request.form["product_id"]
        product_name = request.form["product_name"]
        farmer_name = request.form["farmer_name"]
        harvest_date = request.form["harvest_date"]
        quantity = request.form["quantity"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO products
        VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            product_name,
            farmer_name,
            harvest_date,
            quantity
        ))

        conn.commit()
        conn.close()

        # Blockchain Transaction
        save_transaction(
            product_id,
            "Farmer",
            "Distributor",
            "Farm"
        )

        # QR Code Generation
        if not os.path.exists("static/qr"):
            os.makedirs("static/qr")

        qr = qrcode.make(
            f"http://127.0.0.1:5000/history/{product_id}"
        )

        qr.save(f"static/qr/{product_id}.png")

        return f"""
        <h2>✅ Product Added Successfully!</h2>

        <h3>QR Code Generated</h3>

        <img src="/static/qr/{product_id}.png" width="200">

        <br><br>

        <a href="/history/{product_id}">
        View Product History
        </a>

        <br><br>

        <a href="/products">
        View Products
        </a>
        """

    return render_template("farmer.html")
# ---------------- PRODUCTS ----------------

@app.route("/products")
def products():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return render_template("products.html", products=products)


## ---------------- DISTRIBUTOR ----------------

@app.route("/distributor", methods=["GET", "POST"])
def distributor():

    if request.method == "POST":

        product_id = request.form["product_id"]
        distributor_name = request.form["distributor_name"]
        dispatch_date = request.form["dispatch_date"]
        transport_method = request.form["transport_method"]
        destination = request.form["destination"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO distributor
        VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            distributor_name,
            dispatch_date,
            transport_method,
            destination
        ))

        conn.commit()
        conn.close()

        # Blockchain Transaction
        save_transaction(
            product_id,
            "Distributor",
            "Retailer",
            destination
        )

        return """
        <h2>✅ Distributor Details Saved!</h2>

        <br>

        <a href="/retailer">
        Continue to Retailer
        </a>

        <br><br>

        <a href="/products">
        View Products
        </a>
        """

    return render_template("distributor.html")
# ---------------- RETAILER ----------------

@app.route("/retailer", methods=["GET", "POST"])
def retailer():

    if request.method == "POST":

        product_id = request.form["product_id"]
        retailer_name = request.form["retailer_name"]
        store_name = request.form["store_name"]
        location = request.form["location"]
        arrival_date = request.form["arrival_date"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO retailer
        VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            retailer_name,
            store_name,
            location,
            arrival_date
        ))

        conn.commit()
        conn.close()

        # Blockchain Transaction
        save_transaction(
            product_id,
            "Retailer",
            "Customer",
            location
        )

        return f"""
        <h2>✅ Retailer Details Saved!</h2>

        <br>

        <a href="/history/{product_id}">
        View Product History
        </a>

        <br><br>

        <a href="/products">
        View Products
        </a>
        """

    return render_template("retailer.html")

# ---------------- CUSTOMER ----------------

@app.route("/customer")
def customer():
    return render_template("customer.html")
    # ---------------- HISTORY LIST ----------------

@app.route("/history")
def history_list():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT product_id,
               product_name,
               farmer_name,
               harvest_date
        FROM products
    """)

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "history_list.html",
        products=products
    )


# ---------------- PRODUCT HISTORY ----------------

@app.route("/history/<product_id>")
def history(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE product_id=?",
        (product_id,)
    )
    product = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM distributor WHERE product_id=?",
        (product_id,)
    )
    distributor = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM retailer WHERE product_id=?",
        (product_id,)
    )
    retailer = cursor.fetchone()

    cursor.execute("""
    SELECT sender,
           receiver,
           location,
           timestamp,
           hash,
           previous_hash
    FROM transactions
    WHERE product_id=?
    ORDER BY tx_id
    """, (product_id,))

    transactions = cursor.fetchall()

    conn.close()

    data = str(product) + str(distributor) + str(retailer)

    blockchain_hash = hashlib.sha256(
        data.encode()
    ).hexdigest()

    return render_template(
        "history.html",
        product=product,
        distributor=distributor,
        retailer=retailer,
        blockchain_hash=blockchain_hash,
        transactions=transactions
    )
# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)