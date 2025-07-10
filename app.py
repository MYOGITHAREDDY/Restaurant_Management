from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from datetime import datetime, date
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key in production

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yogitha@2002'
app.config['MYSQL_DB'] = 'restaurant_db'


mysql = MySQL(app)

#----------------REGISTER-------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role == 'admin':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE role = 'admin'")
            existing_admin = cur.fetchone()
            if existing_admin:
                cur.close()
                return "Admin account already exists. Please log in."
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                    (username, password, role))
        mysql.connection.commit()
        cur.close()
        msg = 'Account created! Please login.'
        return redirect(url_for('login'))
    
    return render_template('register.html', msg=msg)


# -------------------- LOGIN --------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role=%s", (username, password, role))
        user = cur.fetchone()
        cur.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('admin_panel' if role == 'admin' else 'menu'))
        else:
            msg = 'Invalid username, password, or role!'
    return render_template('login.html', msg=msg)

# -------------------- MENU --------------------
@app.route('/menu')
def menu():
    if 'role' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM menu")
    items = cur.fetchall()
    cur.close()
    return render_template('menu.html', items=items)

# -------------------- ADD TO CART --------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    quantity = int(request.form['quantity'])
    cart = session.get('cart', [])
    for item in cart:
        if item['item_id'] == item_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'item_id': item_id, 'quantity': quantity})
    session['cart'] = cart
    session.modified = True
    return redirect('/menu')

# -------------------- VIEW CART --------------------
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cur = mysql.connection.cursor()
    items = []
    total = 0
    for entry in cart:
        cur.execute("SELECT * FROM menu WHERE id=%s", (entry['item_id'],))
        item = cur.fetchone()
        subtotal = item[3] * entry['quantity']
        items.append((item, entry['quantity'], subtotal))
        total += subtotal
    cur.close()
    return render_template('cart.html', items=items, total=total)

# -------------------- CHECKOUT --------------------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        payment_method = request.form['payment']
        name = request.form['name']
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        table_id = request.form['table_id']

        if not name.replace(" ", "").isalpha():
            return "Invalid name. Only letters allowed."

        if not (card_number.isdigit() and len(card_number) == 16):
            return "Invalid card number. Must be 16 digits."

        if not (cvv.isdigit() and 3 <= len(cvv) <= 6):
            return "Invalid CVV. Must be 3 to 6 digits."

        cart = session.get('cart', [])
        cur = mysql.connection.cursor()
        total = 0
        for entry in cart:
            cur.execute("SELECT price FROM menu WHERE id = %s", [entry['item_id']])
            price = cur.fetchone()[0]
            total += price * entry['quantity']
        cur.close()

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['checkout_data'] = {
            'payment_method': payment_method,
            'total': total,
            'card_number': card_number,
            'cvv': cvv,
            'table_id': table_id
        }

        print(f"DEBUG OTP (simulate sent to user): {otp}")  # Simulated SMS/Email
        return render_template('otp.html')

    # GET request
    cart = session.get('cart', [])
    cur = mysql.connection.cursor()
    total = 0
    for entry in cart:
        cur.execute("SELECT price FROM menu WHERE id = %s", [entry['item_id']])
        price = cur.fetchone()[0]
        total += price * entry['quantity']
    cur.close()
    return render_template('checkout.html', total=total)

# -------------------- VERIFY OTP --------------------
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']
    if entered_otp != session.get('otp'):
        return "Invalid OTP. Please go back and try again."

    cart = session.get('cart', [])
    if not cart:
        return redirect('/cart')

    data = session.get('checkout_data')
    total = data['total']
    payment_method = data['payment_method']
    table_id = data['table_id']
    user_id = session.get('user_id')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders (user_id, table_id, total_amount, payment_method, status) VALUES (%s, %s, %s, %s, %s)",
                (user_id, table_id, total, payment_method, 'Pending'))
    order_id = cur.lastrowid

    for entry in cart:
        cur.execute("SELECT price FROM menu WHERE id = %s", [entry['item_id']])
        price = cur.fetchone()[0]
        subtotal = price * entry['quantity']
        cur.execute("INSERT INTO order_items (order_id, menu_id, quantity, subtotal) VALUES (%s, %s, %s, %s)",
                    (order_id, entry['item_id'], entry['quantity'], subtotal))

    mysql.connection.commit()
    cur.close()

    session.pop('cart', None)
    session.pop('otp', None)
    session.pop('checkout_data', None)
    return redirect('/success')

# -------------------- SUCCESS PAGE --------------------
@app.route('/success')
def success():
    return render_template('success.html')

# -------------------- ADMIN PANEL --------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    filter_type = request.form.get('filter_type')
    total_filtered = 0  # ✅ Add this
    filter_heading = "Today's Sales ({})".format(date.today())  # ✅ Add this

    if request.method == 'POST' and filter_type:
        if filter_type == 'date':
            specific_date = request.form.get('specific_date')
            if specific_date:
                cur.execute("SELECT SUM(total_amount) FROM orders WHERE DATE(created_at) = %s", [specific_date])
                result = cur.fetchone()
                total_filtered = result[0] if result[0] else 0
                filter_heading = f"Sales on {specific_date}"

        elif filter_type == 'month':
            month = request.form.get('month')
            year = request.form.get('year')
            if month and year:
                cur.execute("SELECT SUM(total_amount) FROM orders WHERE MONTH(created_at) = %s AND YEAR(created_at) = %s", [month, year])
                result = cur.fetchone()
                total_filtered = result[0] if result[0] else 0
                filter_heading = f"Sales in {year}-{int(month):02d}"

        elif filter_type == 'year':
            year = request.form.get('year_only')
            print(f"DEBUG: year received in filter = {year}")
            if year:
                try:
                    year_int = int(year)
                    cur.execute("SELECT SUM(total_amount) FROM orders WHERE YEAR(created_at) = %s", [year_int])
                    result = cur.fetchone()
                    total_filtered = result[0] if result[0] else 0
                    filter_heading = f"Sales in {year_int}"
                except ValueError:
                    total_filtered = 0
                    filter_heading = "Invalid year selected"


        elif filter_type == 'range':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            if start_date and end_date:
                cur.execute("SELECT SUM(total_amount) FROM orders WHERE DATE(created_at) BETWEEN %s AND %s", [start_date, end_date])
                result = cur.fetchone()
                total_filtered = result[0] if result[0] else 0
                filter_heading = f"Sales from {start_date} to {end_date}"

    else:
        # Default: today’s sales
        cur.execute("SELECT SUM(total_amount) FROM orders WHERE DATE(created_at) = CURDATE()")
        result = cur.fetchone()
        total_filtered = result[0] if result[0] else 0

    # Fetch all orders
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()

    # Fetch menu items per order
    order_details = {}
    for order in orders:
        cur.execute("""
            SELECT m.name, oi.quantity, oi.subtotal 
            FROM order_items oi 
            JOIN menu m ON oi.menu_id = m.id 
            WHERE oi.order_id = %s
        """, [order[0]])
        order_details[order[0]] = cur.fetchall()

    # Fetch menu items
    cur.execute("SELECT * FROM menu")
    menu_items = cur.fetchall()

    cur.close()

    return render_template(
    'admin_panel.html',
    orders=orders,
    menu_items=menu_items,
    order_details=order_details,
    total_filtered=total_filtered,
    filter_heading=filter_heading,
    current_year=datetime.now().year,
    filter_type=filter_type,
    request_form=request.form
)


# -------------------- ADD MENU ITEM --------------------
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_path = request.form['image_path']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO menu (name, description, price, image_path) VALUES (%s, %s, %s, %s)",
                    (name, description, price, image_path))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_panel'))
    return render_template('add_menu_item.html')

# -------------------- DELETE MENU ITEM --------------------
@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM menu WHERE id = %s", (item_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin_panel'))

# -------------------- MARK ORDER AS FINISHED --------------------
@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status = 'Finished' WHERE id = %s", (order_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin_panel'))

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# -------------------- RUN SERVER --------------------
if __name__ == '__main__':
    app.run(debug=True)
