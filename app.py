from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.utils import secure_filename
import os
from functools import wraps
import random
from flask_mail import Message, Mail
import time
import string
from collections import defaultdict
import datetime 
from datetime import datetime
from decimal import Decimal

app = Flask(__name__, static_folder='static')

# Set the base upload folder path
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Specify your base uploads folder

# Ensure that the subfolders exist
subfolders = ['ids', 'profile', 'products']

# Create the subfolders within the main upload folder
for folder in subfolders:
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist

# Allowed file extensions for each folder
app.config['ALLOWED_EXTENSIONS'] = {
    'profile': {'png', 'jpg', 'jpeg', 'gif'},
    'id': {'pdf', 'png', 'jpg'},
    'products': {'png', 'jpg', 'jpeg'}
}
otp_dict = {}

app.secret_key = 'dqweqweqw'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not logged in

#-------------------------PANG GENERATE LANG NG PASS NG SUPERADMIN
# hashed_password = generate_password_hash('seller123')
# print(hashed_password)

app.config['MAIL_USERNAME'] = 'haulthriftshop@gmail.com'
app.config['MAIL_PASSWORD'] = 'oiow fzpn vvpn iitr'  # App Password here
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for SSL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'haulthriftshop@gmail.com'

mail = Mail(app)

def create_connection():
    connection = None
    try: 
        connection = mysql.connector.connect(
            host='localhost', port=3307,
            user='root',
            password='',
            database='ecom' )
        print("Connection to MySQL DB successful")
        return connection
    except Error as e:
        print(f"The error {e} has occurred")


# call product nigagawa ni ross
# def call_product(self, id):
#     self.item = id

#     connection = create_connection()
#     if connection == None:
#         print('failed to connect')
#         return redirect('index.html')
#     cursor = connection.cursor()
#     try:
#         cursor.execute(
#             'SELECT product_name, price FROM products WHERE productID = %s', 
#             (self.item)
#         )
#         product = cursor.fetchone()
#         cursor.execute(
#             'INSERT INTO '
#         )
#     except mysql.connector.Error as err:
#         pass


#User class now inherits from UserMixin (provides default behavior)
class User(UserMixin):
    def __init__(self, id, email, username, password, role, first_name, middle_name, last_name, suffix, address, mobile_no, id_type=None, gov_id_path=None, dob=None, profile_picture =None , verification_status=None, email_verified = 0):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.role = role
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.suffix = suffix
        self.address = address
        self.mobile_no = mobile_no
        self.id_type = id_type
        self.gov_id_path = gov_id_path
        self.dob = dob
        self.profile_picture = profile_picture
        self.verification_status = verification_status
        self.email_verified = email_verified

    @classmethod
    def get_by_id(cls, user_id):
        connection = create_connection()  # Make sure this method is defined
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return cls(
                    user_data['id'],
                    user_data['email'],
                    user_data['username'],
                    user_data['password'],
                    user_data['role'],
                    user_data['first_name'],
                    user_data['middle_name'],
                    user_data['last_name'],
                    user_data['suffix'],
                    user_data['address'],
                    user_data['mobile_no'],
                    user_data.get('id_type'),
                    user_data.get('gov_id_path'),
                    user_data.get('dob'),
                    user_data.get('verification_status', 'default_value'),
                    user_data.get('email_verified', 0)
                )
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_id(self):
        """Flask-Login uses this to store and retrieve the user ID"""
        return str(self.id)
    
    @classmethod
    def get_by_email(cls, email):
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                return cls(
                    user_data['id'],
                    user_data['email'],
                    user_data['username'],
                    user_data['password'],
                    user_data['role'],
                    user_data['first_name'],
                    user_data['middle_name'],
                    user_data['last_name'],
                    user_data['suffix'],
                    user_data['address'],
                    user_data['mobile_no'],
                    user_data.get('id_type'),
                    user_data.get('gov_id_path'),
                    user_data.get('dob'),
                    user_data.get('profile_picture'),
                    user_data.get('verification_status'),
                    user_data.get('email_verified')
                )
            return None
        finally:
            cursor.close()
            connection.close()

# Load user callback (needed for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# @app.route('/')
# def home():
#     return render_template('index.html' ,  user=current_user)

@app.route('/')
def home():
    if current_user.is_authenticated and current_user.role == 'superadmin':
        abort(404)

    return render_template('index.html', user=current_user)

# @app.route('/products')
# def products():
#     search = request.args.get('search', '')
#     category = request.args.get('category', '')
#     condition = request.args.get('condition', '')
#     min_price = request.args.get('min_price', None)
#     max_price = request.args.get('max_price', None)
#     sort_by = request.args.get('sort_by', '')

#     query = "SELECT * FROM products WHERE product_status = 'active'"
#     filters = []
#     values = []

#     # Apply search filter
#     if search:
#         search = f"%{search}%"  # Format the search term
#         filters.append("(product_name LIKE %s)")
#         values.extend([search])  # Add both search terms for name and description

#     # Apply category filter
#     if category:
#         filters.append("product_category = %s")
#         values.append(category)

#     # Apply condition filter
#     if condition:
#         filters.append("product_condition = %s")
#         values.append(condition)

#     # Apply price range filters
#     if min_price:
#         filters.append("product_price >= %s")
#         values.append(min_price)
#     if max_price:
#         filters.append("product_price <= %s")
#         values.append(max_price)

#     # Add filters to the query
#     if filters:
#         query += " AND " + " AND ".join(filters)

#     # Handle sorting logic
#     if sort_by:
#         if sort_by == "price_asc":
#             query += " ORDER BY product_price ASC"
#         elif sort_by == "price_desc":
#             query += " ORDER BY product_price DESC"
#         elif sort_by == "name_asc":
#             query += " ORDER BY product_name ASC"
#         elif sort_by == "name_desc":
#             query += " ORDER BY product_name DESC"

#     try:
#         # Establish database connection
#         with mysql.connector.connect(
#             host="localhost", user="root", password="", database="ecom"
#         ) as create_connection:
#             cursor = create_connection.cursor(dictionary=True)  # Enable dictionary mode

#             # Execute the query with the filters and values
#             cursor.execute(query, values)
#             products = cursor.fetchall()

#             # Fetch all unique categories (even if no products with that category)
#             cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
#             categories = cursor.fetchall()

#             # Fetch all unique conditions (even if no products with that condition)
#             cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
#             conditions = cursor.fetchall()

#     except Exception as e:
#         print(f"Error: {e}")
#         products = []
#         categories = []
#         conditions = []

#     return render_template(
#         'products.html', 
#         products=products, 
#         categories=categories, 
#         conditions=conditions
#     )

# @app.route('/products')
# def products():
#     search = request.args.get('search', '')
#     category = request.args.get('category', '')
#     condition = request.args.get('condition', '')
#     min_price = request.args.get('min_price', None)
#     max_price = request.args.get('max_price', None)
#     sort_by = request.args.get('sort_by', '')
#     page = int(request.args.get('page', 1))  # Default to page 1
#     items_per_page = 16  # Number of products per page

#     query = "SELECT * FROM products WHERE product_status = 'active'"
#     filters = []
#     values = []

#     # Apply search filter
#     if search:
#         search = f"%{search}%"  # Format the search term
#         filters.append("(product_name LIKE %s)")
#         values.append(search)

#     # Apply category filter
#     if category:
#         filters.append("product_category = %s")
#         values.append(category)

#     # Apply condition filter
#     if condition:
#         filters.append("product_condition = %s")
#         values.append(condition)

#     # Apply price range filters
#     if min_price:
#         filters.append("product_price >= %s")
#         values.append(min_price)
#     if max_price:
#         filters.append("product_price <= %s")
#         values.append(max_price)

#     # Add filters to the query
#     if filters:
#         query += " AND " + " AND ".join(filters)

#     # Handle sorting logic
#     if sort_by:
#         if sort_by == "price_asc":
#             query += " ORDER BY product_price ASC"
#         elif sort_by == "price_desc":
#             query += " ORDER BY product_price DESC"
#         elif sort_by == "name_asc":
#             query += " ORDER BY product_name ASC"
#         elif sort_by == "name_desc":
#             query += " ORDER BY product_name DESC"

#     # Add pagination (LIMIT and OFFSET)
#     offset = (page - 1) * items_per_page
#     query += " LIMIT %s OFFSET %s"
#     values.extend([items_per_page, offset])

#     try:
#         # Establish database connection
#         with mysql.connector.connect(
#             host="localhost", user="root", password="", database="ecom", port=3307,
#         ) as create_connection:
#             cursor = create_connection.cursor(dictionary=True)

#             # Execute the query with the filters and values
#             cursor.execute(query, values)
#             products = cursor.fetchall()

#             # Count total products for pagination
#             count_query = "SELECT COUNT(*) as total FROM products WHERE product_status = 'active'"
#             if filters:
#                 count_query += " AND " + " AND ".join(filters)
#             cursor.execute(count_query, values[:-2])  # Exclude LIMIT/OFFSET from count query
#             total_products = cursor.fetchone()['total']

#             # Calculate total pages
#             total_pages = (total_products + items_per_page - 1) // items_per_page

#             # Fetch all unique categories (even if no products with that category)
#             cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
#             categories = cursor.fetchall()

#             # Fetch all unique conditions (even if no products with that condition)
#             cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
#             conditions = cursor.fetchall()

#     except Exception as e:
#         print(f"Error: {e}")
#         products = []
#         categories = []
#         conditions = []
#         total_pages = 1

#     return render_template(
#         'products.html',
#         products=products,
#         categories=categories,
#         conditions=conditions,
#         total_pages=total_pages,
#         current_page=page
#     )

# @app.route('/products')
# def products():
#     search = request.args.get('search', '')
#     category = request.args.get('category', '')
#     condition = request.args.get('condition', '')
#     min_price = request.args.get('min_price', None)
#     max_price = request.args.get('max_price', None)
#     sort_by = request.args.get('sort_by', '')
#     page = int(request.args.get('page', 1))  # Default to page 1
#     items_per_page = 16  # Number of products per page

#     query = "SELECT * FROM products WHERE product_status = 'active'"
#     filters = []
#     values = []

#     # Apply search filter
#     if search:
#         search = f"%{search}%"  # Format the search term
#         filters.append("(product_name LIKE %s)")
#         values.append(search)

#     # Apply category filter
#     if category:
#         filters.append("product_category = %s")
#         values.append(category)

#     # Apply condition filter
#     if condition:
#         filters.append("product_condition = %s")
#         values.append(condition)

#     # Apply price range filters
#     if min_price:
#         filters.append("product_price >= %s")
#         values.append(min_price)
#     if max_price:
#         filters.append("product_price <= %s")
#         values.append(max_price)

#     # Add filters to the query
#     if filters:
#         query += " AND " + " AND ".join(filters)

#     # Handle sorting logic
#     if sort_by:
#         if sort_by == "price_asc":
#             query += " ORDER BY product_price ASC"
#         elif sort_by == "price_desc":
#             query += " ORDER BY product_price DESC"
#         elif sort_by == "name_asc":
#             query += " ORDER BY product_name ASC"
#         elif sort_by == "name_desc":
#             query += " ORDER BY product_name DESC"

#     # Add pagination (LIMIT and OFFSET)
#     offset = (page - 1) * items_per_page
#     query += " LIMIT %s OFFSET %s"
#     values.extend([items_per_page, offset])

#     try:
#         # Establish database connection
#         create_connection = mysql.connector.connect(
#             host="localhost", user="root", password="", database="ecom",
#             port=3307
#         )
#         cursor = create_connection.cursor(dictionary=True)

#         print("Query:", query)  # Debug print
#         print("Values:", values)  # Debug print

#         # Execute the query with the filters and values
#         cursor.execute(query, values)
#         products = cursor.fetchall()

#         # Count total products for pagination
#         count_query = "SELECT COUNT(*) as total FROM products WHERE product_status = 'active'"
#         if filters:
#             count_query += " AND " + " AND ".join(filters)
#         cursor.execute(count_query, values[:-2])  # Exclude LIMIT/OFFSET from count query
#         total_products = cursor.fetchone()['total']

#         # Calculate total pages
#         total_pages = (total_products + items_per_page - 1) // items_per_page

#         print("Total Products:", total_products)  # Debug print
#         print("Total Pages:", total_pages)  # Debug print

#         # Fetch all unique categories (even if no products with that category)
#         cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
#         categories = cursor.fetchall()

#         # Fetch all unique conditions (even if no products with that condition)
#         cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
#         conditions = cursor.fetchall()

#     except Exception as e:
#         print(f"Error: {e}")
#         products = []
#         categories = []
#         conditions = []
#         total_pages = 1

#     finally:
#         # Close the cursor and connection to avoid resource leaks
#         if 'cursor' in locals() and cursor is not None:
#             cursor.close()
#         if 'create_connection' in locals() and create_connection is not None:
#             create_connection.close()

#     return render_template(
#         'products.html',
#         products=products,
#         categories=categories,
#         conditions=conditions,
#         total_pages=total_pages,
#         current_page=page
#     )


@app.route('/products')
def products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    subcategory = request.args.get('subcategory', '')  # New subcategory filter
    condition = request.args.get('condition', '')
    min_price = request.args.get('min_price', None)
    max_price = request.args.get('max_price', None)
    sort_by = request.args.get('sort_by', '')
    page = int(request.args.get('page', 1))  # Default to page 1
    items_per_page = 16  # Number of products per page

    query = "SELECT * FROM products WHERE product_status = 'active'"
    filters = []
    values = []

    # Apply search filter
    if search:
        search = f"%{search}%"  # Format the search term
        filters.append("(product_name LIKE %s)")
        values.append(search)

    # Apply category filter
    if category:
        filters.append("product_category = %s")
        values.append(category)

    # Apply subcategory filter
    if subcategory:
        filters.append("product_subcategory = %s")
        values.append(subcategory)

    # Apply condition filter
    if condition:
        filters.append("product_condition = %s")
        values.append(condition)

    # Apply price range filters
    if min_price:
        filters.append("product_price >= %s")
        values.append(min_price)
    if max_price:
        filters.append("product_price <= %s")
        values.append(max_price)

    # Add filters to the query
    if filters:
        query += " AND " + " AND ".join(filters)

    # Handle sorting logic
    if sort_by:
        if sort_by == "price_asc":
            query += " ORDER BY product_price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY product_price DESC"
        elif sort_by == "name_asc":
            query += " ORDER BY product_name ASC"
        elif sort_by == "name_desc":
            query += " ORDER BY product_name DESC"

    # Add pagination (LIMIT and OFFSET)
    offset = (page - 1) * items_per_page
    query += " LIMIT %s OFFSET %s"
    values.extend([items_per_page, offset])

    try:
        # Establish database connection
        create_connection = mysql.connector.connect(
            host="localhost", user="root", password="", database="ecom" , port = 3307
        )
        cursor = create_connection.cursor(dictionary=True)

        print("Query:", query)  # Debug print
        print("Values:", values)  # Debug print

        # Execute the query with the filters and values
        cursor.execute(query, values)
        products = cursor.fetchall()

        # Count total products for pagination
        count_query = "SELECT COUNT(*) as total FROM products WHERE product_status = 'active'"
        if filters:
            count_query += " AND " + " AND ".join(filters)
        cursor.execute(count_query, values[:-2])  # Exclude LIMIT/OFFSET from count query
        total_products = cursor.fetchone()['total']

        # Calculate total pages
        total_pages = (total_products + items_per_page - 1) // items_per_page

        print("Total Products:", total_products)  # Debug print
        print("Total Pages:", total_pages)  # Debug print

        # Fetch all unique categories (even if no products with that category)
        cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
        categories = cursor.fetchall()

        # Fetch all unique subcategories (even if no products with that subcategory)
        cursor.execute("SELECT DISTINCT product_subcategory FROM products WHERE product_status = 'active'")
        subcategories = cursor.fetchall()

        # Fetch all unique conditions (even if no products with that condition)
        cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
        conditions = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
        products = []
        categories = []
        subcategories = []
        conditions = []
        total_pages = 1

    finally:
        # Close the cursor and connection to avoid resource leaks
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'create_connection' in locals() and create_connection is not None:
            create_connection.close()

    return render_template(
        'products.html',
        products=products,
        categories=categories,
        subcategories=subcategories,  # Pass subcategories to the template
        conditions=conditions,
        total_pages=total_pages,
        current_page=page
    )


@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'GET':
#         # Serve the registration form
#         return render_template('user_registration.html')
    
#     if request.method == 'POST':
#         first_name = request.form['first_name']
#         middle_name = request.form.get('middle_name', '')  # Optional field
#         last_name = request.form['last_name']
#         suffix = request.form.get('suffix', '')  # Optional field
#         address = request.form['address']
#         mobile_no = request.form['mobile_no']
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']

#         # Validate passwords
#         if password != confirm_password:
#             flash('Passwords do not match. Please try again.', category='danger')
#             return redirect(url_for('register'))

#         # Hash the password for storage
#         hashed_password = generate_password_hash(password)

#         conn = create_connection()
#         if conn is None:
#             flash('Database connection failed!', category='danger')
#             return redirect(url_for('register'))

#         cursor = conn.cursor()
        
#         try:
#             # Check if the username already exists
#             cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
#             if cursor.fetchone():
#                 flash('Username is already taken. Please choose another.', category='danger')
#                 return redirect(url_for('register'))
            
#             # Check if the email already exists
#             cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
#             if cursor.fetchone():
#                 flash('Email is already registered. Please use another email.', category='danger')
#                 return redirect(url_for('register'))
            
#             # Insert the new user into the database
#             cursor.execute("""
#                 INSERT INTO users (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, password) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, hashed_password))
#             conn.commit()
#             flash('Registration successful!', category='success')
#         except Error as e:
#             flash(f"An error occurred: {e}", category='danger')
#         finally:
#             cursor.close()
#             conn.close()

#         return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Serve the registration form
        return render_template('user_registration.html')
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')  # Optional field
        last_name = request.form['last_name']
        suffix = request.form.get('suffix', '')  # Optional field
        address = request.form['address']
        mobile_no = request.form['mobile_no']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', category='danger')
            return redirect(url_for('register'))

        # Hash the password for storage
        hashed_password = generate_password_hash(password)

        conn = create_connection()
        if conn is None:
            flash('Database connection failed!', category='danger')
            return redirect(url_for('register'))

        cursor = conn.cursor()

        try:
            # Check if the username already exists
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username is already taken. Please choose another.', category='danger')
                return redirect(url_for('register'))
            
            # Check if the email already exists
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email is already registered. Please use another email.', category='danger')
                return redirect(url_for('register'))
            
            # Insert the user with email_verified set to False
            cursor.execute("""
                INSERT INTO users (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, password, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, hashed_password, False))
            conn.commit()

            # Generate an OTP and save it temporarily (for email verification)
            otp = random.randint(100000, 999999)
            otp_dict[email] = {'otp': otp, 'time': time.time()}

            # Send OTP to the user's email
            msg = Message(
                subject="Email Verification for Your Account",
                recipients=[email]
            )
            msg.body = f"""
            Hello {username},

            Please use the following OTP to verify your email address:
            {otp}

            This OTP will expire in 15 minutes.

            Regards,
            Your Thrift Shop Team
            """
            mail.send(msg)
            flash('A verification OTP has been sent to your email. Please check your inbox to verify your account.', category='info')

            # Redirect to OTP verification page, passing user details
            return redirect(url_for('verify_otp', email=email, first_name=first_name, middle_name=middle_name, last_name=last_name, suffix=suffix, address=address, mobile_no=mobile_no, username=username, hashed_password=hashed_password))

        except Error as e:
            flash(f"An error occurred: {e}", category='danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))

# @app.route('/product/<int:product_id>')
# def product_details(product_id):
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)
    
#     # Fetch the selected product
#     cursor.execute("""
#         SELECT product_id, product_name, product_price, product_category, product_condition,
#                product_rating, product_size, product_description, product_image, product_status,
#                seller_id
#         FROM products WHERE product_id = %s
#     """, (product_id,))
#     product = cursor.fetchone()

#     # If the product doesn't exist or is archived, redirect to the products page
#     if not product or product['product_status'] == 'archived':
#         flash("Product not found or is no longer available.")
#         return redirect(url_for('products'))

#     # Fetch seller details including shop name, profile picture, and activity timestamp
#     cursor.execute("""
#         SELECT sellers.shop_name, sellers.bio, sellers.store_banner_path,
#                users.first_name, users.last_name, users.email, users.profile_picture, 
#                sellers.updated_at
#         FROM sellers
#         JOIN users ON sellers.user_id = users.id
#         WHERE sellers.seller_id = %s
#     """, (product['seller_id'],))
#     seller = cursor.fetchone()

#     # Calculate the time difference (active time)
#     if seller['updated_at']:
#         last_active = seller['updated_at']  # already a datetime object
#         time_diff = datetime.now() - last_active
#         minutes = time_diff.total_seconds() // 60

#         if minutes < 1:
#             active_status = "Active just now"
#         elif minutes < 60:
#             active_status = f"Active {int(minutes)} minutes ago"
#         elif minutes < 1440:
#             hours = minutes // 60
#             active_status = f"Active {int(hours)} hours ago"
#         else:
#             days = minutes // 1440
#             active_status = f"Active {int(days)} days ago"
#     else:
#         active_status = "Active unknown"

#     # Fetch the number of products the seller has (excluding archived products)
#     cursor.execute("""
#         SELECT COUNT(*) 
#         FROM products
#         WHERE seller_id = %s AND product_status != 'archived'
#     """, (product['seller_id'],))
#     product_count = cursor.fetchone()['COUNT(*)']

#     # Check if the product is already in the user's cart
#     product_in_cart = False
#     if current_user.is_authenticated:
#         cursor.execute("""
#             SELECT * FROM cart 
#             WHERE user_id = %s AND product_id = %s
#         """, (current_user.id, product_id))
#         product_in_cart = cursor.fetchone() is not None

#     # Check if the product is already in the user's wishlist
#     product_in_wishlist = False
#     if current_user.is_authenticated:
#         cursor.execute("""
#             SELECT * FROM wishlist 
#             WHERE user_id = %s AND product_id = %s
#         """, (current_user.id, product_id))
#         product_in_wishlist = cursor.fetchone() is not None

#     # Fetch related products (exclude archived products)
#     cursor.execute("""
#         SELECT product_id, product_name, product_price, product_image
#         FROM products 
#         WHERE product_category = %s 
#           AND product_id != %s 
#           AND product_status != 'archived'
#         LIMIT 4
#     """, (product['product_category'], product_id))
#     related_products = cursor.fetchall()

#     cursor.close()
#     connection.close()

#     return render_template(
#         'product_details.html',
#         product=product,
#         seller=seller,
#         active_status=active_status,  # Pass the active status to the template
#         product_count=product_count,  # Pass the product count to the template
#         related_products=related_products,
#         product_in_wishlist=product_in_wishlist,
#         product_in_cart=product_in_cart
#     )

# @app.route('/product/<int:product_id>')
# def product_details(product_id):
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)
    
#     # Fetch the selected product
#     cursor.execute("""
#         SELECT product_id, product_name, product_price, product_category, product_condition,
#                product_rating, product_size, product_description, product_image, product_status,
#                seller_id
#         FROM products WHERE product_id = %s
#     """, (product_id,))
#     product = cursor.fetchone()

#     # If the product doesn't exist or is archived, redirect to the products page
#     if not product or product['product_status'] == 'archived':
#         flash("Product not found or is no longer available.")
#         return redirect(url_for('products'))

#     # Fetch seller details including shop name, profile picture, and activity timestamp
#     cursor.execute("""
#         SELECT sellers.shop_name, sellers.bio, sellers.store_banner_path,
#                users.first_name, users.last_name, users.email, users.profile_picture, 
#                sellers.updated_at
#         FROM sellers
#         JOIN users ON sellers.user_id = users.id
#         WHERE sellers.seller_id = %s
#     """, (product['seller_id'],))
#     seller = cursor.fetchone()

#     # Calculate the time difference (active time)
#     if seller['updated_at']:
#         last_active = seller['updated_at']
#         time_diff = datetime.now() - last_active
#         minutes = time_diff.total_seconds() // 60

#         if minutes < 1:
#             active_status = "Active just now"
#         elif minutes < 60:
#             active_status = f"Active {int(minutes)} minutes ago"
#         elif minutes < 1440:
#             hours = minutes // 60
#             active_status = f"Active {int(hours)} hours ago"
#         else:
#             days = minutes // 1440
#             active_status = f"Active {int(days)} days ago"
#     else:
#         active_status = "Active unknown"

#     # Fetch the number of products the seller has (excluding archived products)
#     cursor.execute("""
#         SELECT COUNT(*) 
#         FROM products
#         WHERE seller_id = %s AND product_status != 'archived'
#     """, (product['seller_id'],))
#     product_count = cursor.fetchone()['COUNT(*)']

#     # Fetch the seller's average rating and rating count
#     cursor.execute("""
#         SELECT AVG(rating) AS average_rating, 
#                COUNT(CASE WHEN rating IS NOT NULL THEN 1 END) AS rating_count
#         FROM seller_ratings
#         WHERE seller_id = %s
#     """, (product['seller_id'],))
#     seller_rating_data = cursor.fetchone()

#     seller['average_rating'] = seller_rating_data['average_rating']
#     seller['rating_count'] = seller_rating_data['rating_count']
#     # Fetch related products (exclude archived products)
#     cursor.execute("""
#         SELECT product_id, product_name, product_price, product_image
#         FROM products 
#         WHERE product_category = %s 
#           AND product_id != %s 
#           AND product_status != 'archived'
#         LIMIT 4
#     """, (product['product_category'], product_id))
#     related_products = cursor.fetchall()

#     # Check if the product is already in the user's cart or wishlist
#     product_in_cart = False
#     product_in_wishlist = False
#     if current_user.is_authenticated:
#         cursor.execute("""
#             SELECT * FROM cart 
#             WHERE user_id = %s AND product_id = %s
#         """, (current_user.id, product_id))
#         product_in_cart = cursor.fetchone() is not None

#         cursor.execute("""
#             SELECT * FROM wishlist 
#             WHERE user_id = %s AND product_id = %s
#         """, (current_user.id, product_id))
#         product_in_wishlist = cursor.fetchone() is not None

#     cursor.close()
#     connection.close()

#     return render_template(
#         'product_details.html',
#         product=product,
#         seller=seller,
#         active_status=active_status,
#         product_count=product_count,
#         related_products=related_products,
#         product_in_wishlist=product_in_wishlist,
#         product_in_cart=product_in_cart
#     )

@app.route('/product/<int:product_id>')
def product_details(product_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch the selected product
    cursor.execute("""
        SELECT product_id, product_name, product_price, product_category, product_condition,
               product_rating, product_size, product_description, product_image, product_status,
               seller_id
        FROM products WHERE product_id = %s
    """, (product_id,))
    product = cursor.fetchone()

    # If the product doesn't exist or is archived, redirect to the products page
    if not product or product['product_status'] == 'archived':
        flash("Product not found or is no longer available.")
        return redirect(url_for('products'))

    # Fetch seller details including shop name, profile picture, and activity timestamp
    cursor.execute("""
        SELECT sellers.seller_id, sellers.shop_name, sellers.bio, sellers.store_banner_path,
               users.first_name, users.last_name, users.email, users.profile_picture, 
               sellers.updated_at
        FROM sellers
        JOIN users ON sellers.user_id = users.id
        WHERE sellers.seller_id = %s
    """, (product['seller_id'],))
    seller = cursor.fetchone()

    # Calculate the time difference (active time)
    if seller['updated_at']:
        last_active = seller['updated_at']
        time_diff = datetime.now() - last_active
        minutes = time_diff.total_seconds() // 60

        if minutes < 1:
            active_status = "Active just now"
        elif minutes < 60:
            active_status = f"Active {int(minutes)} minutes ago"
        elif minutes < 1440:
            hours = minutes // 60
            active_status = f"Active {int(hours)} hours ago"
        else:
            days = minutes // 1440
            active_status = f"Active {int(days)} days ago"
    else:
        active_status = "Active unknown"

    # Fetch the number of products the seller has (excluding archived products)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM products
        WHERE seller_id = %s AND product_status != 'archived'
    """, (product['seller_id'],))
    product_count = cursor.fetchone()['COUNT(*)']

    # Fetch the seller's average rating and rating count
    cursor.execute("""
        SELECT AVG(rating) AS average_rating, 
               COUNT(CASE WHEN rating IS NOT NULL THEN 1 END) AS rating_count
        FROM seller_ratings
        WHERE seller_id = %s
    """, (product['seller_id'],))
    seller_rating_data = cursor.fetchone()

    seller['average_rating'] = seller_rating_data['average_rating']
    seller['rating_count'] = seller_rating_data['rating_count']
    # Fetch related products (exclude archived products)
    cursor.execute("""
        SELECT product_id, product_name, product_price, product_image
        FROM products 
        WHERE product_category = %s 
          AND product_id != %s 
          AND product_status != 'archived'
        LIMIT 4
    """, (product['product_category'], product_id))
    related_products = cursor.fetchall()

    # Check if the product is already in the user's cart or wishlist
    product_in_cart = False
    product_in_wishlist = False
    if current_user.is_authenticated:
        cursor.execute("""
            SELECT * FROM cart 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        product_in_cart = cursor.fetchone() is not None

        cursor.execute("""
            SELECT * FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        product_in_wishlist = cursor.fetchone() is not None

    cursor.close()
    connection.close()

    return render_template(
        'product_details.html',
        product=product,
        seller=seller,
        active_status=active_status,
        product_count=product_count,
        related_products=related_products,
        product_in_wishlist=product_in_wishlist,
        product_in_cart=product_in_cart
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        abort(404)

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = create_connection()
        if connection is None:
            flash('Database connection failed!')
            return redirect(url_for('login'))

        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                user_obj = User(
                    user['id'], user['email'], user['username'], user['password'], 
                    user['role'], user['first_name'], user.get('middle_name', ''), 
                    user['last_name'], user.get('suffix', ''), user['address'], 
                    user['mobile_no'], user.get('id_type', ''), user.get('gov_id_path', ''), 
                    user.get('dob', '')
                )
                login_user(user_obj)
                
                if user_obj.role == 'superadmin':
                    flash('Logged in as Superadmin!', category='success')
                    return redirect(url_for('superadmin'))
                elif user_obj.role == 'seller':
                    # Check if seller profile is complete
                    cursor.execute("""
                        SELECT shop_name, bio 
                        FROM sellers 
                        WHERE user_id = %s
                    """, (user['id'],))

                    seller_info = cursor.fetchone()  # Fetch one record, no need for cursor.fetchall()

                    if not seller_info or not (seller_info['shop_name'] or "").strip() or not (seller_info['bio'] or "").strip():
                        flash('Your seller profile is incomplete. You can update it now or later.', category='info')
                        return redirect(url_for('seller_profile'))  # Redirect to update profile if incomplete
                    else:
                        return redirect(url_for('seller'))  # Redirect to seller dashboard if complete
                else:
                    flash('Login successful!', category='success')
                    return redirect(url_for('home'))
            else:
                flash('Invalid credentials!', category='danger')
        except Error as e:
            flash(f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for('login'))

def role_required(role, redirect_to_login=False):
    def decorator(func):
        @wraps(func)  # Preserves the original function's metadata (name, docstring)
        def wrapper(*args, **kwargs):
            # Check if the user is logged in
            if not current_user.is_authenticated:
                if redirect_to_login:
                    flash("You need to log in first!", category='danger')
                    return redirect(url_for('login'))
                else:
                    abort(404)  # Abort with 404 if accessed directly

            # Check if the user has the required role
            if current_user.role != role:
                abort(404)  # Forbidden if the user does not have the required role

            # If checks pass, call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404  


# @app.route('/inventory', methods=['GET'])
# @login_required
# def inventory():
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)
    
#     try:
#         # Fetch products from the database for the current seller (or all products)
#         cursor.execute("SELECT * FROM products WHERE seller_id = %s", (current_user.id,))
#         products = cursor.fetchall()  # Get all products for the seller

#         # Pass products to the template
#         return render_template('inventory.html', products=products)
    
#     except mysql.connector.Error as err:
#         flash(f"Error fetching products: {err}", 'danger')
#         return redirect(url_for('home'))
    
#     finally:
#         cursor.close()
#         connection.close()

@app.route('/inventory', methods=['GET'])
@login_required
def inventory():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Number of products per page
    per_page = 5

    # Get the current page for active and archived products (default is 1)
    active_page = int(request.args.get('active_page', 1))
    archived_page = int(request.args.get('archived_page', 1))

    try:
        # Active products pagination
        cursor.execute("SELECT COUNT(*) AS count FROM products WHERE seller_id = %s AND product_status = 'active'", (current_user.id,))
        total_active_products = cursor.fetchone()['count']

        active_offset = (active_page - 1) * per_page
        cursor.execute("""
            SELECT * FROM products
            WHERE seller_id = %s AND product_status = 'active'
            LIMIT %s OFFSET %s
        """, (current_user.id, per_page, active_offset))
        active_products = cursor.fetchall()

        # Archived products pagination
        cursor.execute("SELECT COUNT(*) AS count FROM products WHERE seller_id = %s AND product_status = 'archived'", (current_user.id,))
        total_archived_products = cursor.fetchone()['count']

        archived_offset = (archived_page - 1) * per_page
        cursor.execute("""
            SELECT * FROM products
            WHERE seller_id = %s AND product_status = 'archived'
            LIMIT %s OFFSET %s
        """, (current_user.id, per_page, archived_offset))
        archived_products = cursor.fetchall()

        # Pass variables to the template
        return render_template(
            'inventory.html',
            active_products=active_products,
            total_active_products=total_active_products,
            active_page=active_page,
            archived_products=archived_products,
            total_archived_products=total_archived_products,
            archived_page=archived_page,
            per_page=per_page
        )

    except mysql.connector.Error as err:
        flash(f"Error fetching products: {err}", 'danger')
        return redirect(url_for('home'))

    finally:
        cursor.close()
        connection.close()





@app.route('/logout')
@login_required
def logout():
    logout_user()  # This will log the user out
    flash('You have been logged out.')
    return redirect(url_for('home'))  # Redirect to the home page after logout



# @app.route('/add-product', methods=['POST'])
# @login_required
# def add_product():
#     if request.method == 'POST':
#         # Get form data
#         product_name = request.form['product-name']
#         price = request.form['product-price']
#         stock = request.form['product-stock']
#         category = request.form['product-category']
#         subcategory = request.form['product-subcategory']  # Get subcategory data
#         product_condition = request.form['product-condition']
#         product_size = request.form['product-size']
#         description = request.form['product-description']
        
#         # Get image data
#         product_image = request.files['product-image']
#         if product_image:
#             # Ensure secure filename
#             image_filename = secure_filename(product_image.filename)
            
#             # Set the folder for product images
#             folder_name = 'products'  # Set the subfolder for products
            
#             # Construct the target path to save the file
#             folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#             os.makedirs(folder_path, exist_ok=True)  # Create the subfolder if it doesn't exist
            
#             # Save the image file in the correct folder
#             image_path = os.path.join(folder_path, image_filename)
#             product_image.save(image_path)
#         else:
#             image_filename = None
        
#         # Insert product into the database, including the subcategory
#         connection = create_connection()
#         cursor = connection.cursor()
#         try:
#             cursor.execute(''' 
#                 INSERT INTO products (seller_id, product_name, product_price, product_stock, product_category, 
#                                       product_subcategory, product_condition, product_size, product_description, product_image)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ''', (current_user.id, product_name, price, stock, category, subcategory, product_condition, product_size, description, image_filename))
#             connection.commit()

#             # Return success response
#             return jsonify(success=True)
#         except Exception as e:
#             flash(f"Error adding product: {e}", 'danger')
#             return jsonify(success=False)
#         finally:
#             cursor.close()
#             connection.close()

@app.route('/add-product', methods=['POST'])
@login_required
def add_product():
    connection = None  # Initialize connection to None
    if request.method == 'POST':
        try:
            # Get form data
            product_name = request.form['product-name']
            price = request.form['product-price']
            stock = request.form['product-stock']
            category = request.form['product-category']
            subcategory = request.form['product-subcategory']
            product_condition = request.form['product-condition']
            product_size = request.form['product-size']
            description = request.form['product-description']
            
            # Handle image upload
            product_image = request.files['product-image']
            image_filename = None
            if product_image and product_image.filename:
                filename = secure_filename(product_image.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                image_filename = f"{timestamp}_{filename}"
                folder_name = 'products'
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                os.makedirs(folder_path, exist_ok=True)
                image_path = os.path.join(folder_path, image_filename)
                product_image.save(image_path)
            
            # Insert product into the database
            connection = create_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(''' 
                    INSERT INTO products (seller_id, product_name, product_price, product_stock, product_category, 
                                          product_subcategory, product_condition, product_size, product_description, product_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (current_user.id, product_name, price, stock, category, subcategory, product_condition, product_size, description, image_filename))
                connection.commit()
                product_id = cursor.lastrowid
            finally:
                cursor.close()

            # Return success response with product data
            return jsonify({
                'success': True,
                'product': {
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_price': price,
                    'product_stock': stock,
                    'product_category': category,
                    'product_subcategory': subcategory,
                    'product_condition': product_condition,
                    'product_size': product_size,
                    'product_description': description,
                    'product_image': image_filename
                }
            })

        except Exception as e:
            # Log the error and return failure response
            flash(f"Error adding product: {e}", 'danger')
            return jsonify({'success': False, 'error': str(e)}), 500

        finally:
            if connection:
                connection.close()


# @app.route('/add_to_cart/')
# product_id = request.form()
# call_product()

# @app.route('/superadmin') 
# @login_required
# @role_required('superadmin')  # Ensure that only superadmins can access this page
# def superadmin():
#     return render_template('superadmin.html')

@app.route('/superadmin')
@role_required('superadmin', redirect_to_login=False)
def superadmin():
    if not current_user.is_authenticated:
        abort(404)

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch total users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        # Fetch pending sellers
        cursor.execute("SELECT COUNT(*) AS pending_sellers FROM users WHERE role = 'pending_seller'")
        pending_sellers = cursor.fetchone()['pending_sellers']

        # Fetch total products
        cursor.execute("SELECT COUNT(*) AS total_products FROM products")
        total_products = cursor.fetchone()['total_products']

        # Fetch total sales revenue (completed orders)
        cursor.execute("""
            SELECT SUM(total_price) AS total_sales
            FROM orders
            WHERE status = 'Completed'
        """)
        total_sales = cursor.fetchone()['total_sales'] or 0.00

        # Fetch pending orders
        cursor.execute("SELECT COUNT(*) AS pending_orders FROM orders WHERE status = 'Pending'")
        pending_orders = cursor.fetchone()['pending_orders']

        # Format total sales as currency
        total_sales = f"{total_sales:,.2f}"

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'superadmin.html',
        total_users=total_users,
        pending_sellers=pending_sellers,
        total_products=total_products,
        total_sales=total_sales,
        pending_orders=pending_orders
    )

@app.route('/seller_dashboard')
@login_required
@role_required('seller', redirect_to_login=True)
def seller():
    user_id = current_user.id

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Query for total revenue (replace with your actual query logic)
        cursor.execute("""
            SELECT SUM(order_items.price * order_items.quantity) AS revenue
            FROM order_items
            JOIN orders ON order_items.order_id = orders.order_id
            WHERE orders.seller_id = %s AND orders.status = 'completed'
        """, (user_id,))
        revenue = cursor.fetchone()['revenue'] or 0.00

        # Query for number of orders (replace with your actual query logic)
        cursor.execute("""
            SELECT COUNT(*) AS orders_count
            FROM orders
            WHERE seller_id = %s AND orders.status = 'pending'
        """, (user_id,))
        orders_count = cursor.fetchone()['orders_count'] or 0

        # Query for total units sold (replace with your actual query logic)
        cursor.execute("""
            SELECT SUM(order_items.quantity) AS units_sold
            FROM order_items
            JOIN orders ON order_items.order_id = orders.order_id
            WHERE orders.seller_id = %s AND orders.status = 'completed'
        """, (user_id,))
        units_sold = cursor.fetchone()['units_sold'] or 0

        # Calculate the average order value (replace with your actual query logic)
        if orders_count > 0:
            average_order_value = revenue / orders_count
        else:
            average_order_value = 0.00

        # Format the values
        revenue = f"{revenue:,.2f}"  # Format as currency with two decimals
        average_order_value = f"{average_order_value:,.2f}"  # Format as currency with two decimals

    finally:
        cursor.close()
        connection.close()

    return render_template('seller.html', revenue=revenue, orders_count=orders_count,
                           units_sold=units_sold, average_order_value=average_order_value)

@app.route('/seller-registration', methods=['GET', 'POST'])
@login_required
def seller_registration():
    # Fetch the current user's latest data from the database
    connection = create_connection()
    if connection is None:
        flash('Database connection failed!', 'danger')
        return redirect(url_for('seller_registration'))

    cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easier field access
    try:
        cursor.execute("SELECT verification_status FROM users WHERE id = %s", (current_user.id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found!', 'danger')
            return redirect(url_for('seller_registration'))
        
        # Update current_user's verification_status manually
        verification_status = user_data['verification_status']
        print(f"Current verification status: {verification_status}")

        # Prevent access if the user is a pending seller
        if verification_status == 'pending_seller':
            flash('Your seller application is pending approval.', 'info')
            return redirect(url_for('waiting_for_approval'))  # Redirect to the waiting for approval page

    except Error as e:
        flash(f"An error occurred while fetching user data: {e}", 'danger')
        return redirect(url_for('seller_registration'))
    finally:
        cursor.close()
        connection.close()

    # If the user is already a seller, redirect them to the homepage or dashboard
    if current_user.role == 'seller':
        flash('You are already a seller!', 'info')
        return redirect(url_for('home'))  # Redirect to the home page or dashboard

    # Continue with the rest of the seller registration logic...
    if request.method == 'POST':
        # Get form data for names
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        suffix = request.form.get('suffix')
        address = request.form.get('address')  # Get the address field

        # Get other form data
        id_type = request.form.get('id_type')
        gov_id = request.files.get('gov_id')  # File upload
        dob = request.form.get('dob')
        agree_verification = request.form.get('agree_verification') == 'on'  # Checkbox

        # Validate fields
        if not (id_type and gov_id and dob and agree_verification and address):  # Check that address is also filled
            flash('All fields are required, and you must agree to the verification process!', 'danger')
            return redirect(url_for('seller_registration'))

        # Ensure the upload folder exists
        gov_id_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'id')
        if not os.path.exists(gov_id_folder):
            os.makedirs(gov_id_folder)

        # Handle file upload
        if gov_id and allowed_file(gov_id.filename, app.config['ALLOWED_EXTENSIONS']['id']):
            filename = secure_filename(gov_id.filename)
            gov_id_path = os.path.join(gov_id_folder, filename)
            print(f"File will be saved to: {gov_id_path}")
            gov_id.save(gov_id_path)
            # Save relative path for database storage
            relative_path = os.path.relpath(gov_id_path, 'static').replace('\\', '/')
        else:
            flash('Invalid file type for Government ID. Allowed types: png, jpg, jpeg, pdf.', 'danger')
            return redirect(url_for('seller_registration'))

        # Update database with name changes, address, and other seller registration info
        connection = create_connection()
        if connection is None:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('seller_registration'))

        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE users 
                SET first_name = %s, 
                    middle_name = %s, 
                    last_name = %s, 
                    suffix = %s, 
                    address = %s,  -- Include address here
                    id_type = %s, 
                    gov_id_path = %s, 
                    dob = %s, 
                    is_verification_agreed = %s,
                    verification_status = %s
                WHERE id = %s
            """, (first_name, middle_name, last_name, suffix, address, id_type, relative_path, dob, agree_verification, 'pending_seller', current_user.id))
            connection.commit()
            flash('Your seller application has been submitted for approval!', 'success')
            return redirect(url_for('home'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('seller_registration.html', user=current_user)

# @app.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     # Fetch current user data
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)

#     user = None
#     try:
#         cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
#         user = cursor.fetchone()

#         if not user:
#             flash('User not found.', category='danger')
#             return redirect(url_for('profile'))  # Handle missing user case
#     except Exception as e:
#         flash(f"Database error: {e}", category='danger')
#         return redirect(url_for('profile'))
#     finally:
#         cursor.close()
#         connection.close()

#     # Retain the current profile picture if not updated
#     profile_picture = user.get('profile_picture') if user else 'default.png'  # Default image

#     # Handle profile picture upload
#     if 'profile_picture' in request.files:
#         profile_file = request.files['profile_picture']
#         if profile_file:
#             # Save the profile picture (assume save_file handles storage)
#             profile_picture = save_file(profile_file, 'profile')  # Specify the 'profile' folder

#     # Update profile data in the database
#     if request.method == 'POST':
#         try:
#             # Prepare the updated fields
#             fields_to_update = {
#                 'first_name': request.form.get('first_name', '').strip() or None,
#                 'middle_name': request.form.get('middle_name', '').strip() or None,
#                 'last_name': request.form.get('last_name', '').strip() or None,
#                 'suffix': request.form.get('suffix', '').strip() or None,
#                 'address': request.form.get('address', '').strip() or None,
#                 'mobile_no': request.form.get('mobile_no', '').strip() or None,
#                 'username': request.form.get('username', '').strip() or None,
#                 'email': request.form.get('email', '').strip() or None,
#                 'profile_picture': profile_picture,  # Use the updated picture if provided
#             }

#             # Handle password update if provided
#             password = request.form.get('password', '').strip()
#             confirm_password = request.form.get('confirm_password', '').strip()
#             if password and password == confirm_password:
#                 fields_to_update['password'] = generate_password_hash(password)

#             # Filter out fields with `None` (no change for blank inputs)
#             fields_to_update = {
#                 key: value for key, value in fields_to_update.items() if value is not None
#             }

#             # Construct and execute the update query
#             if fields_to_update:  # Only run query if there are fields to update
#                 connection = create_connection()
#                 cursor = connection.cursor(dictionary=True)
#                 update_query = "UPDATE users SET " + ", ".join(
#                     f"{key} = %s" for key in fields_to_update.keys()
#                 ) + " WHERE id = %s"
#                 cursor.execute(update_query, (*fields_to_update.values(), current_user.id))
#                 connection.commit()

#                 flash('Profile updated successfully!', category='success')
#             else:
#                 flash('No changes were made.', category='info')

#         except Exception as e:
#             flash(f"An error occurred: {e}", category='danger')
#         finally:
#             cursor.close()
#             connection.close()

#         return redirect(url_for('profile'))

#     return render_template('profile.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Fetch current user data
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    user = None
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
        user = cursor.fetchone()

        if not user:
            flash('User not found.', category='danger')
            return redirect(url_for('profile'))  # Handle missing user case
    except Exception as e:
        flash(f"Database error: {e}", category='danger')
        return redirect(url_for('profile'))
    finally:
        cursor.close()
        connection.close()

    # Retain the current profile picture if not updated
    profile_picture = user.get('profile_picture') if user else 'default.png'  # Default image

    # Handle profile picture upload
    if 'profile_picture' in request.files:
        profile_file = request.files['profile_picture']
        if profile_file:
            # Save the profile picture (assume save_file handles storage)
            profile_picture = save_file(profile_file, 'profile')  # Specify the 'profile' folder

    # Update profile data in the database
    if request.method == 'POST':
        try:
            # Prepare the updated fields
            fields_to_update = {
                'first_name': request.form.get('first_name', '').strip() or None,
                'middle_name': request.form.get('middle_name', '').strip() or None,
                'last_name': request.form.get('last_name', '').strip() or None,
                'suffix': request.form.get('suffix', '').strip() or None,
                'address': request.form.get('address', '').strip() or None,
                'mobile_no': request.form.get('mobile_no', '').strip() or None,
                'username': request.form.get('username', '').strip() or None,
                'email': request.form.get('email', '').strip() or None,
                'profile_picture': profile_picture,  # Use the updated picture if provided
            }

            # Handle password update if provided
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            if password and password == confirm_password:
                fields_to_update['password'] = generate_password_hash(password)

            # Filter out fields with `None` (no change for blank inputs)
            fields_to_update = {
                key: value for key, value in fields_to_update.items() if value is not None
            }

            # Construct and execute the update query
            if fields_to_update:  # Only run query if there are fields to update
                connection = create_connection()
                cursor = connection.cursor(dictionary=True)
                update_query = "UPDATE users SET " + ", ".join(
                    f"{key} = %s" for key in fields_to_update.keys()
                ) + " WHERE id = %s"
                cursor.execute(update_query, (*fields_to_update.values(), current_user.id))
                connection.commit()

                flash('Profile updated successfully!', category='success')
            else:
                flash('No changes were made.', category='info')

        except Exception as e:
            flash(f"An error occurred: {e}", category='danger')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# def save_profile_pic(file): #DI PA NAGANA
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         profile_picture = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(profile_picture)  # Save the file to the specified path
#         return profile_picture
#     return None

@app.route('/pending-sellers', methods=['GET'])  # Method to fetch pending sellers
@login_required
def pending_sellers():
    # Ensure only the superadmin can access this
    if current_user.role != 'superadmin':
        flash('Access denied.', category='danger')
        return redirect(url_for('home'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Modified query to also select 'mobile_no' and 'address'
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, mobile_no, address, gov_id_path 
            FROM users 
            WHERE verification_status = 'pending_seller'
        """)
        pending_seller = cursor.fetchall()

        # Normalize gov_id_path to use forward slashes
        for seller in pending_seller:
            seller['gov_id_path'] = seller['gov_id_path'].replace('\\', '/')
    except Exception as e:
        flash(f"Database error: {e}", category='danger')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        connection.close()

    return render_template('admin_pending_seller.html', pending_seller=pending_seller, user=current_user)



@app.route('/approve-seller/<int:user_id>', methods=['POST'])
@login_required
def approve_seller(user_id):
    if current_user.role != 'superadmin':
        flash('Access denied.', category='danger')
        return redirect(url_for('home'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Update the user status to approved and change the role to seller
        cursor.execute("UPDATE users SET verification_status = 'approved_seller', role = 'seller' WHERE id = %s", (user_id,))

        # Insert into sellers table with the user_id being inserted as seller_id
        cursor.execute('''
            INSERT INTO sellers (seller_id, user_id, shop_name, bio, account_creation_date)
            VALUES (%s, %s, NULL, NULL, NOW())
        ''', (user_id, user_id))  # Use user_id as seller_id in the sellers table
        connection.commit()

        flash('Seller approved and profile created successfully!', category='success')

    except Exception as e:
        flash(f"Error approving seller: {e}", category='danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('pending_sellers'))



@app.route('/reject_seller/<int:user_id>', methods=['POST']) #method for rejecting pending seller
@login_required
def reject_seller(user_id):
    # Ensure only the superadmin can access this
    if current_user.role != 'superadmin':
        flash('Access denied.', category='danger')
        return redirect(url_for('home'))

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Update verification_status to NULL when rejecting the seller
        query = "UPDATE users SET verification_status = NULL WHERE id = %s"
        cursor.execute(query, (user_id,))

        # Commit the changes
        connection.commit()

        flash('Seller rejected successfully.', category='success')
    except Exception as e:
        flash(f"Error rejecting seller: {e}", category='danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('pending_sellers'))


# def save_file(file, folder_name):
#     """
#     Save the uploaded file to the specified folder and return only the filename.
#     :param file: File object from the form
#     :param folder_name: Subfolder to save the file (e.g., 'ids', 'profile', 'products')
#     :return: The filename of the saved file (e.g., 'samplee.jpg')
#     """
#     if file:
#         # Ensure secure filename
#         filename = secure_filename(file.filename)

#         # Construct the target folder path
#         folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        
#         # Ensure the folder exists
#         if not os.path.exists(folder_path):
#             os.makedirs(folder_path)

#         # Construct full file path
#         file_path = os.path.join(folder_path, filename)
        
#         # Save the file
#         try:
#             file.save(file_path)
#             # Return just the filename (e.g., 'samplee.jpg') to store in the database
#             return filename
#         except Exception as e:
#             print(f"Error saving file: {e}")
#             return None
#     return None

def save_file(file, folder_name):
    """
    Save the uploaded file to the specified folder and return only the filename.
    :param file: File object from the form
    :param folder_name: Subfolder to save the file (e.g., 'ids', 'profile', 'products')
    :return: The filename of the saved file (e.g., 'samplee.jpg')
    """
    if file:
        # Ensure secure filename
        filename = secure_filename(file.filename)

        # Construct the target folder path
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Construct full file path
        file_path = os.path.join(folder_path, filename)
        
        # Save the file
        try:
            file.save(file_path)
            # Return just the filename (e.g., 'samplee.jpg') to store in the database
            return filename
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    return None






@app.route('/upload_gov_id', methods=['POST']) #pang upload ng gov id
def upload_gov_id():
    file = request.files.get('gov_id')
    if not file:
        flash("No file selected.", "danger")
        return redirect(url_for('profile'))

    # Save the file
    try:
        file_path = save_file(file, 'id')
        if file_path:
            current_user.gov_id_path = file_path  # Save path to the database
            create_connection.session.commit()
            flash("Government ID uploaded successfully!", "success")
        else:
            flash("Invalid file type.", "danger")
    except Exception as e:
        flash(f"Error uploading file: {str(e)}", "danger")

    return redirect(url_for('profile'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'GET':
        # Pass the current_user directly to the template
        return render_template('change-password.html')

    if request.method == 'POST':
        # Fetch form data
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate form inputs
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", category='danger')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash("New password and confirmation do not match.", category='danger')
            return redirect(url_for('change_password'))

        # Validate current password
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT password FROM users WHERE id = %s", (current_user.id,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], current_password):
                flash("Current password is incorrect.", category='danger')
                return redirect(url_for('change_password'))

            # Update with new password
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
            connection.commit()
            flash("Password changed successfully!", category='success')

        except Exception as e:
            flash(f"An error occurred: {e}", category='danger')

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('change_password'))

@app.route('/waiting-for-approval')
@login_required
def waiting_for_approval():
    return render_template('waiting_for_approval.html')

@app.route('/seller_profile', methods=['GET', 'POST'])
@login_required
def seller_profile():
    if request.method == 'POST':
        # Handle form submission for profile update
        shop_name = request.form.get('shop_name')
        bio = request.form.get('bio')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        suffix = request.form.get('suffix')
        address = request.form.get('address')
        mobile_no = request.form.get('mobile_no')
        store_banner = request.files.get('store_banner')

        # Handle file upload if provided
        store_banner_path = None
        if store_banner:
            try:
                banner_filename = secure_filename(store_banner.filename)
                store_banner.save(os.path.join(app.config['UPLOAD_FOLDER'], banner_filename))
                store_banner_path = f"uploads/{banner_filename}"
            except Exception as e:
                flash(f"Error uploading banner: {e}", "danger")

        # Update database with seller profile details
        connection = create_connection()
        try:
            cursor = connection.cursor()
            # Update `sellers` table
            cursor.execute('''
                INSERT INTO sellers (user_id, shop_name, bio, store_banner_path)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                shop_name = VALUES(shop_name), bio = VALUES(bio), store_banner_path = VALUES(store_banner_path)
            ''', (current_user.id, shop_name, bio, store_banner_path))
            
            # Commit before closing the cursor to ensure all changes are saved
            connection.commit()

            # Now, update `users` table for basic details in a new cursor
            cursor.close()  # Close the previous cursor before creating a new one
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE users
                SET first_name = %s, middle_name = %s, last_name = %s, suffix = %s, address = %s, mobile_no = %s
                WHERE id = %s
            ''', (first_name, middle_name, last_name, suffix, address, mobile_no, current_user.id))
            connection.commit()

            flash("Profile updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating profile: {e}", "danger")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('seller'))

    # GET: Fetch existing seller details
    connection = create_connection()
    seller_data = {}
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT u.first_name, u.middle_name, u.last_name, u.suffix, u.address, u.mobile_no, s.shop_name, s.bio, s.store_banner_path
            FROM users u
            LEFT JOIN sellers s ON u.id = s.user_id
            WHERE u.id = %s
        ''', (current_user.id,))
        seller_data = cursor.fetchone()
        cursor.close()  # Close the cursor after fetching results
    except Exception as e:
        flash(f"Error fetching profile details: {e}", "danger")
    finally:
        connection.close()

    return render_template('seller_profile.html', seller=seller_data)

    # Render the profile page with current seller details
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM sellers WHERE user_id = %s', (current_user.id,))
    seller = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('seller_profile.html', seller=seller)


@app.route('/toggle_product_status/<int:product_id>', methods=['POST'])
@login_required
def toggle_product_status(product_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch the product to check current status
    cursor.execute("SELECT * FROM products WHERE product_id = %s AND seller_id = %s", (product_id, current_user.id))
    product = cursor.fetchone()

    if not product:
        flash("Product not found or unauthorized action.", "danger")
        return redirect(url_for('inventory'))

    # Toggle the product status
    new_status = 'archived' if product['product_status'] == 'active' else 'active'
    cursor.execute("UPDATE products SET product_status = %s WHERE product_id = %s", (new_status, product_id))
    connection.commit()

    action = "archived" if new_status == 'archived' else "unarchived"
    flash(f"Product successfully {action}.", "success")
    return redirect(url_for('inventory'))




@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # If it's a GET request, fetch the product data and render the update form
    if request.method == 'GET':
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            return "Product not found", 404

        # Render the update form with the current product data
        return render_template('update_product.html', product=product)

    # If it's a POST request, update the product data in the database
    elif request.method == 'POST':
        # Fetch current product data
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            return "Product not found", 404

        # Get new data from the form
        product_name = request.form['product-name']
        product_price = request.form['product-price']
        product_stock = request.form['product-stock']
        product_category = request.form['product-category']
        product_condition = request.form['product-condition']
        product_size = request.form['product-size']
        product_description = request.form['product-description']

        # Check if there's a new image file
        if 'product-image' in request.files and request.files['product-image']:
            image = request.files['product-image']
            # Save the image and get the filename
            image_filename = save_file(image, 'products')  # Save under 'uploads/products'
            if image_filename:
                # Extract only the filename (e.g., 'images.jpg') from the saved path
                image_filename = os.path.basename(image_filename)
                print(f"Image uploaded and saved: {image_filename}")  # Debugging line
                product_image = image_filename
            else:
                print("Error: Image file not saved.")  # Debugging line
                product_image = product['product_image']
        else:
            # Keep the old image if no new file is uploaded
            product_image = product['product_image']

        print(f"Product Image: {product_image}")  # Debugging line

        # Update the product in the database with only the filename
        cursor.execute(""" 
            UPDATE products SET product_name = %s, product_price = %s, product_stock = %s,
            product_category = %s, product_condition = %s, product_size = %s, 
            product_description = %s, product_image = %s WHERE product_id = %s
        """, (product_name, product_price, product_stock, product_category, product_condition,
              product_size, product_description, product_image, product_id))

        connection.commit()

        # Return success response and redirect to inventory page
        flash('Product updated successfully', 'success')
        return redirect(url_for('inventory'))


@app.route("/seller_centre")
def seller_centre():
    return render_template ('seller_centre.html')


# @app.route('/cart')
# def cart():
#     if not current_user.is_authenticated:
#         flash('You need to log in to view your cart.')
#         return redirect(url_for('login'))

#     user_id = current_user.id
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)

#     # Fetch all cart items for the user
#     cursor.execute("""
#         SELECT c.cart_id, p.product_id, p.product_name, p.product_price, p.product_image
#         FROM cart c
#         JOIN products p ON c.product_id = p.product_id
#         WHERE c.user_id = %s
#     """, (user_id,))
#     cart_items = cursor.fetchall()

#     # Calculate total price
#     total = sum(item['product_price'] for item in cart_items)

#     cursor.close()
#     connection.close()

#     return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart')
def cart():
    if not current_user.is_authenticated:
        flash('You need to log in to view your cart.')
        return redirect(url_for('login'))

    user_id = current_user.id
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch all cart items for the user
    cursor.execute("""
        SELECT c.cart_id, p.product_id, p.product_name, p.product_price, p.product_image, p.seller_id
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    # Calculate total price
    total = sum(item['product_price'] for item in cart_items)

    cursor.close()
    connection.close()

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/toggle_cart/<int:product_id>', methods=['POST'])
def toggle_cart(product_id):
    if not current_user.is_authenticated:
        flash('You need to log in to manage your cart.')
        return redirect(url_for('login'))

    # Use Flask-Login's current_user for the user ID
    user_id = current_user.id

    # Create database connection and cursor
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Check if the product is already in the user's cart
    cursor.execute("SELECT * FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    cart_item = cursor.fetchone()

    if cart_item:
        # Remove the product from the cart
        cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_item['cart_id'],))
        flash('Item removed from cart.')
    else:
        # Add the product to the cart
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, 1)",
            (user_id, product_id)
        )
        flash('Product added to cart.')

    # Commit changes and close connection
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('product_details', product_id=product_id))


# @app.route('/remove_from_cart/<int:cart_id>')
# def remove_from_cart(cart_id):
#     create_connection.session.execute("DELETE FROM cart WHERE cart_id = :cart_id", {'cart_id': cart_id})
#     create_connection.session.commit()
#     flash('Item removed from cart.')
#     return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if not current_user.is_authenticated:
        flash('You need to log in to remove items from your cart.')
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor()

    # Remove the product from the cart
    cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Item removed from cart.')
    return redirect(url_for('cart'))  # Redirect to cart page

def get_cart_count(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
    cart_count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return cart_count

@app.context_processor
def inject_cart_count():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = get_cart_count(current_user.id)
    return {'cart_count': cart_count}

#FOR WISHLIST
# @app.route('/toggle_wishlist/<int:product_id>', methods=['POST'])
# def toggle_wishlist(product_id):
#     if not current_user.is_authenticated:
#         return jsonify({'success': False, 'message': 'You need to log in to manage your wishlist.'})

#     # Use Flask-Login's current_user for the user ID
#     user_id = current_user.id

#     # Create database connection and cursor
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)

#     # Check if the product is already in the user's wishlist
#     cursor.execute("SELECT * FROM wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
#     wishlist_item = cursor.fetchone()

#     if wishlist_item:
#         # Remove the product from the wishlist
#         cursor.execute("DELETE FROM wishlist WHERE wishlist_id = %s", (wishlist_item['wishlist_id'],))
#         message = 'Item removed from wishlist.'
#         success = True
#     else:
#         # Add the product to the wishlist
#         cursor.execute(
#             "INSERT INTO wishlist (user_id, product_id) VALUES (%s, %s)",
#             (user_id, product_id)
#         )
#         message = 'Product added to wishlist.'
#         success = True

#     # Commit changes and close connection
#     connection.commit()
#     cursor.close()
#     connection.close()

#     return jsonify({'success': success, 'message': message})


@app.route('/toggle-wishlist/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product is already in wishlist
        cursor.execute("""
            SELECT wishlist_id FROM wishlist 
            WHERE user_id = %s AND product_id = %s
        """, (current_user.id, product_id))
        existing_wishlist = cursor.fetchone()
        
        if existing_wishlist:
            # Remove from wishlist
            cursor.execute("""
                DELETE FROM wishlist 
                WHERE wishlist_id = %s
            """, (existing_wishlist['wishlist_id'],))
            in_wishlist = False
        else:
            # Add to wishlist
            cursor.execute("""
                INSERT INTO wishlist (user_id, product_id) 
                VALUES (%s, %s)
            """, (current_user.id, product_id))
            in_wishlist = True
        
        connection.commit()
        return jsonify({'success': True, 'in_wishlist': in_wishlist})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
        
    finally:
        cursor.close()
        connection.close()

# @app.route('/toggle-wishlist/<int:product_id>', methods=['POST'])
# @login_required
# def toggle_wishlist(product_id):
#     try:
#         connection = create_connection()
#         cursor = connection.cursor(dictionary=True)
        
#         # Check if product is already in wishlist
#         cursor.execute("""
#             SELECT * FROM wishlist 
#             WHERE user_id = %s AND product_id = %s
#         """, (current_user.id, product_id))
#         existing_wishlist = cursor.fetchone()
        
#         if existing_wishlist:
#             # Remove from wishlist
#             cursor.execute("""
#                 DELETE FROM wishlist 
#                 WHERE user_id = %s AND product_id = %s
#             """, (current_user.id, product_id))
#             was_added = False
#             message = 'Item removed from wishlist'
#         else:
#             # First check if the product exists in the products table
#             cursor.execute("""
#                 SELECT product_id FROM products 
#                 WHERE product_id = %s
#             """, (product_id,))
#             product_exists = cursor.fetchone()
            
#             if not product_exists:
#                 return jsonify({
#                     'success': False,
#                     'message': 'Product does not exist'
#                 })
            
#             # Add to wishlist with IGNORE to prevent duplicates
#             cursor.execute("""
#                 INSERT IGNORE INTO wishlist (user_id, product_id) 
#                 VALUES (%s, %s)
#             """, (current_user.id, product_id))
#             was_added = True
#             message = 'Item added to wishlist'
        
#         connection.commit()
        
#         # Get updated wishlist count
#         cursor.execute("""
#             SELECT COUNT(*) as count FROM wishlist 
#             WHERE user_id = %s
#         """, (current_user.id,))
#         wishlist_count = cursor.fetchone()['count']
        
#         return jsonify({
#             'success': True,
#             'added': was_added,
#             'message': message,
#             'wishlistCount': wishlist_count
#         })
        
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({
#             'success': False,
#             'error': str(e),
#             'message': 'Error updating wishlist'
#         })
        
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()


# @app.route('/wishlist')
# @login_required  # Ensure the user is logged in
# def wishlist():
#     user_id = current_user.id  # Get the logged-in user's ID

#     # Query to fetch the wishlist for the user, including the wishlist_id
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT w.wishlist_id, p.product_id, p.product_name, p.product_price, p.product_image
#         FROM products p
#         JOIN wishlist w ON p.product_id = w.product_id
#         WHERE w.user_id = %s
#     """, (user_id,))
#     wishlist = cursor.fetchall()  # Fetch all wishlist products
#     cursor.close()
#     connection.close()

#     return render_template('wishlist.html', wishlist=wishlist)

@app.route('/wishlist')
@login_required  # Ensure the user is logged in
def wishlist():
    user_id = current_user.id  # Get the logged-in user's ID
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = 9  # Number of items per page

    # Create database connection
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the total count of wishlist items for the user
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM wishlist w
        WHERE w.user_id = %s
    """, (user_id,))
    total_items = cursor.fetchone()['total']

    # Fetch the wishlist items for the current page
    cursor.execute("""
        SELECT w.wishlist_id, p.product_id, p.product_name, p.product_price, p.product_image
        FROM products p
        JOIN wishlist w ON p.product_id = w.product_id
        WHERE w.user_id = %s
        LIMIT %s OFFSET %s
    """, (user_id, per_page, (page - 1) * per_page))
    wishlist = cursor.fetchall()  # Fetch the current page of wishlist products

    cursor.close()
    connection.close()

    # Calculate the total number of pages
    total_pages = (total_items + per_page - 1) // per_page  # Round up division

    return render_template('wishlist.html', wishlist=wishlist, total_pages=total_pages, current_page=page)



@app.route('/remove_from_wishlist/<int:wishlist_id>', methods=['POST'])
def remove_from_wishlist(wishlist_id):
    if not current_user.is_authenticated:
        flash('You need to log in to manage items from your wishlist.')
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor()    

    try:
        # Remove the product from the wishlist
        cursor.execute("DELETE FROM wishlist WHERE wishlist_id = %s", (wishlist_id,))
        connection.commit()

        # Get the updated wishlist count for the current user
        cursor.execute("SELECT COUNT(*) FROM wishlist WHERE user_id = %s", (current_user.id,))
        wishlist_count = cursor.fetchone()[0]

        flash('Item removed from wishlist.')

        return jsonify({'success': True, 'wishlist_count': wishlist_count})

    except Exception as e:
        connection.rollback()  # Rollback in case of error
        flash(f"An error occurred: {str(e)}", "danger")
        return jsonify({'success': False, 'error': str(e)})

    finally:
        cursor.close()
        connection.close()



def get_wishlist_count(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM wishlist WHERE user_id = %s", (user_id,))
    wishlist_count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return wishlist_count

@app.context_processor
def inject_wishlist_count():
    wishlist_count = 0
    if current_user.is_authenticated:
        wishlist_count = get_wishlist_count(current_user.id)
    return {'wishlist_count': wishlist_count}


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'GET':
        email = request.args.get('email')  # Get email from URL
        return render_template('verify_otp.html', email=email)

    if request.method == 'POST':
        email = request.form['email']
        otp_entered = request.form['otp']

        # Validate the OTP
        if email in otp_dict:
            otp_data = otp_dict[email]
            if otp_data['otp'] == int(otp_entered) and time.time() - otp_data['time'] <= 900:  # 15-minute expiry
                # OTP is valid, update user email_verified to True in the database
                conn = create_connection()
                cursor = conn.cursor()

                try:
                    cursor.execute("""
                        UPDATE users
                        SET email_verified = TRUE
                        WHERE email = %s
                    """, (email,))
                    conn.commit()
                    flash('Email successfully verified!', category='success')
                except Error as e:
                    flash(f"An error occurred: {e}", category='danger')
                finally:
                    cursor.close()
                    conn.close()

                # Remove OTP from the dictionary after successful verification
                del otp_dict[email]

                return redirect(url_for('login'))  # Redirect to login page
            else:
                flash('Invalid OTP or OTP expired. Please try again.', category='danger')
        else:
            flash('OTP verification failed. Please try again.', category='danger')

        return redirect(url_for('verify_otp', email=email))

@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')  # Get email from the form
        
        # Get user from database
        user = get_user_by_email(email)
        if user:
            if user['email_verified'] == 1:  # Check if email is verified
                # Generate a 6-digit verification code
                verification_code = ''.join(random.choices(string.digits, k=6))
                
                # Store the verification code and email in the session
                session['verification_code'] = verification_code
                session['reset_email'] = email
                
                # Send verification code via email
                msg = Message("Password Reset Verification Code", recipients=[email])
                msg.body = f"Your verification code is: {verification_code}"
                mail.send(msg)
                
                flash("A verification code has been sent to your email.", "success")
                return redirect(url_for('verify_code'))
            else:
                flash("No user found with that email address.", "danger")
        else:
            flash("No user found with that email address.", "danger")
    
    return render_template('reset_password_req.html')








@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        entered_code = request.form.get('verification_code')
        
        if entered_code == session.get('verification_code'):
            # Code is valid, redirect to password reset form
            return redirect(url_for('reset_password'))
        
        flash("Invalid verification code. Please try again.", "danger")
    return render_template('verify_code.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # Ensure the user has entered a valid verification code
    if 'verification_code' not in session:
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password'))
        
        # Get email from session
        email = session.get('reset_email')
        if not email:
            flash("No email found in session.", "danger")
            return redirect(url_for('reset_request'))

        # Get user from database
        user = get_user_by_email(email)
        if user:
            if user['email_verified'] == 1:  # Check if the email is verified
                try:
                    # Update the user's password in the database
                    hashed_password = generate_password_hash(new_password)
                    update_password(email, hashed_password)
                    
                    flash("Your password has been successfully updated.", "success")
                    
                    # Clear the session
                    session.pop('verification_code', None)  # Remove verification code from session
                    session.pop('reset_email', None)  # Remove email from session
                    
                    return redirect(url_for('login'))
                except Exception as e:
                    flash(f"An error occurred: {str(e)}", "danger")
            elif user['email_verified'] == 0:
                flash("Your email address has not been verified. Please verify your email before resetting your password.", "danger")
        else:
            flash("No user found with that email address.", "danger")
    
    return render_template('password_form.html')

def get_user_by_email(email):
    """Fetch a user by email and return their data, including email_verified status."""
    connection = create_connection()  # Make sure this method is correctly defined
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        return user_data  # Returns None if no user found
    finally:
        cursor.close()
        connection.close()

def update_password(email, hashed_password):
    """Update the user's password in the database."""
    connection = create_connection()  # Make sure this method is correctly defined
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s", 
            (hashed_password, email)
        )
        connection.commit()  # Commit the changes
    finally:
        cursor.close()
        connection.close()


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = current_user.id
    user_email = current_user.email  # Store the email from the logged-in user

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')  # This should match the email in the users table
        mobile_no = request.form.get('mobile_no')
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        courier = request.form.get('courier')
        shipping_fee = Decimal(request.form.get('shipping_fee', '38.00'))  # Ensure Decimal type
        total_price = Decimal(request.form.get('total_price', '0.00'))  # Ensure Decimal type

        # Check if the email in the form matches the current user's email
        if email != user_email:
            flash("You cannot change your email address.", "danger")
            return redirect(url_for('checkout'))  # Redirect back to checkout

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # Step 1: Group items by seller
            cursor.execute("""
                SELECT c.cart_id, c.product_id, p.product_price, p.seller_id, p.product_name
                FROM cart c
                JOIN products p ON c.product_id = p.product_id
                WHERE c.user_id = %s
            """, (user_id,))
            cart_items = cursor.fetchall()  # Fetch all items

            if not cart_items:
                flash("Your cart is empty.", "warning")
                return redirect(url_for('cart'))  # Ensure cart is not empty

            # Step 2: Get the most recent transaction_id
            cursor.execute("SELECT MAX(transaction_id) AS max_transaction_id FROM orders")
            result = cursor.fetchone()  # Fetch the result
            transaction_id = (result['max_transaction_id'] or 0) + 1  # Increment the latest transaction_id by 1

            # Group items by seller
            seller_orders = {}
            for item in cart_items:
                seller_id = item['seller_id']
                if seller_id not in seller_orders:
                    seller_orders[seller_id] = {'items': [], 'total_price': Decimal('0.00')}
                seller_orders[seller_id]['items'].append(item)
                seller_orders[seller_id]['total_price'] += Decimal(item['product_price'])  # Ensure Decimal type

            # Step 3: Create an order for each seller using the same transaction_id
            for seller_id, order_data in seller_orders.items():
                # Add shipping fee to the total price
                final_total = order_data['total_price'] + shipping_fee  # Both are now Decimal

                order_query = """
                    INSERT INTO orders (user_id, transaction_id, total_price, shipping_fee, courier, order_date, status, shipping_address, 
                                        payment_method, first_name, last_name, mobile_no, email, seller_id)
                    VALUES (%s, %s, %s, %s, %s, NOW(), 'Pending', %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(order_query, (
                    user_id, transaction_id, final_total, shipping_fee, courier, shipping_address, payment_method,
                    first_name, last_name, mobile_no, user_email, seller_id
                ))
                order_id = cursor.lastrowid

                # Insert items into order_items and update stock
                for item in order_data['items']:
                    order_item_query = """
                        INSERT INTO order_items (order_id, product_id, quantity, price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    quantity = 1  # Assuming quantity is always 1 for each product in cart
                    subtotal = quantity * Decimal(item['product_price'])  # Ensure Decimal type
                    cursor.execute(order_item_query, (order_id, item['product_id'], quantity, item['product_price'], subtotal))

                    # Step 4: Reduce the stock by 1
                    update_stock_query = """
                        UPDATE products
                        SET product_stock = product_stock - 1
                        WHERE product_id = %s AND product_stock >= 1
                    """
                    cursor.execute(update_stock_query, (item['product_id'],))

                    # Step 5: Archive the product if stock reaches 0
                    archive_product_query = """
                        UPDATE products
                        SET product_status = 'archived'
                        WHERE product_id = %s AND product_stock = 0
                    """
                    cursor.execute(archive_product_query, (item['product_id'],))

            # Step 6: Clear cart after successful order
            cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

            connection.commit()  # Commit all the changes to the database

            # Prepare order details
            order_details = {
                'transaction_id': transaction_id,
                'first_name': first_name,
                'last_name': last_name,
                'total_price': final_total,
                'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'shipping_address': shipping_address,
                'status': 'Pending',
            }

            order_items = []
            for order_data in seller_orders.values():
                for item in order_data['items']:
                    order_items.append({
                        'product_name': item['product_name'],
                        'quantity': 1,  # Assuming quantity is 1
                        'price': item['product_price'],
                        'subtotal': item['product_price'],  # Since quantity is 1
                    })

            # Send the order confirmation email
            send_order_confirmation_email(user_email, order_details, order_items)

            flash("Order placed successfully!", "success")
            return redirect(url_for('order_summary', transaction_id=transaction_id))

        except Exception as e:
            flash(f"An error occurred during checkout: {str(e)}", "danger")
            connection.rollback()  # Rollback in case of error
            print("Checkout Error:", str(e))

        finally:
            cursor.close()
            connection.close()

    # Rendering the checkout page with the total price, shipping address, etc.
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Get the total price for all cart items
        cursor.execute("""
            SELECT SUM(p.product_price) AS total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user_id,))
        total = cursor.fetchone()['total'] or Decimal('0.00')

        # Fetch the user's shipping address
        cursor.execute("""
            SELECT address
            FROM users
            WHERE id = %s
        """, (user_id,))
        user_address = cursor.fetchone()
        shipping_address = user_address['address'] if user_address else ""
        shipping_fee = 38
    finally:
        cursor.close()
        connection.close()

    if total == Decimal('0.00'):
        flash("Your cart is empty. Add items before proceeding to checkout.", "warning")
        return redirect(url_for('cart'))  # Ensure there's a return statement here

    return render_template('checkout.html', total=total, shipping_address=shipping_address, shipping_fee=shipping_fee)




@app.route('/order-history', methods=['GET'])
@login_required
def order_history():
    user_id = current_user.id

    # Fetch user's orders including the transaction_id
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT order_id, transaction_id, order_date, status, shipping_address
            FROM orders
            WHERE user_id = %s
            GROUP BY transaction_id
            ORDER BY order_date DESC
        """
        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()
        print(orders)  # Debugging: Check the structure of the fetched orders
    finally:
        cursor.close()
        connection.close()

    return render_template('order_history.html', orders=orders)

# @app.route('/order-history', methods=['GET'])
# @login_required
# def order_history():
#     user_id = current_user.id

#     # Fetch user's orders and their items
#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)
#     try:
#         # Fetch orders
#         order_query = """
#             SELECT order_id, transaction_id, order_date, status, shipping_address
#             FROM orders
#             WHERE user_id = %s
#             GROUP BY transaction_id
#             ORDER BY order_date DESC
#         """
#         cursor.execute(order_query, (user_id,))
#         orders = cursor.fetchall()
        
#         # For each order, fetch its items
#         for order in orders:
#             item_query = """
#                 SELECT product_id, product_name, product_image, price, quantity
#                 FROM order_items
#                 WHERE order_id = %s
#             """
#             cursor.execute(item_query, (order['order_id'],))
#             order['items'] = cursor.fetchall()
        
#         print(orders)  # Debugging
#     except Exception as e:
#         print("Error:", e)
#         orders = []
#     finally:
#         cursor.close()
#         connection.close()

#     return render_template('order_history.html', orders=orders)


# @app.route('/order_summary/<int:transaction_id>')
# @login_required
# def order_summary(transaction_id):
#     user_id = current_user.id
#     connection = create_connection()

#     try:
#         cursor = connection.cursor(dictionary=True)

#         # Fetch the order
#         cursor.execute("""
#             SELECT * 
#             FROM orders 
#             WHERE transaction_id = %s AND user_id = %s
#         """, (transaction_id, user_id))
#         order = cursor.fetchone()  # Fetch a single order

#         # If no order found, redirect with a flash message
#         if not order:
#             flash("No orders found for this transaction.", "danger")
#             return redirect(url_for('order_history'))

#         print("Order fetched:", order)  # Debugging

#         # Fetch the order items
#         cursor.execute("""
#             SELECT 
#                 p.product_name, 
#                 p.product_image, 
#                 oi.quantity, 
#                 oi.price, 
#                 (oi.quantity * oi.price) AS subtotal,
#                 o.status AS order_status
#             FROM order_items oi
#             JOIN products p ON oi.product_id = p.product_id
#             JOIN orders o ON oi.order_id = o.order_id
#             WHERE oi.order_id = %s
#         """, (order['order_id'],))  # Only target this specific order ID

#         order_items = cursor.fetchall()  # Fetch all items related to this order
#         print("Order items fetched:", order_items)  # Debugging

#         # Handle case if no items are fetched
#         if not order_items:
#             flash("No items found for this order.", "danger")
#             return redirect(url_for('order_history'))

#         # Dynamically calculate total price
#         total_price = sum(item['subtotal'] for item in order_items)
#         print("Total price calculated:", total_price)

#     except Exception as e:
#         flash(f"An error occurred: {str(e)}", "danger")
#         print("Error Details:", str(e))
#         return redirect(url_for('order_history'))

#     finally:
#         # Close the cursor and connection
#         cursor.close()
#         connection.close()

#     # Render the order summary page with fetched data
#     return render_template(
#         'order_summary.html',
#         order=order,
#         order_items=order_items,
#         total_price=total_price
#     )

@app.route('/order_summary/<int:transaction_id>')
@login_required
def order_summary(transaction_id):
    user_id = current_user.id
    connection = create_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch the orders associated with the transaction_id
        cursor.execute("""
            SELECT * 
            FROM orders 
            WHERE transaction_id = %s AND user_id = %s
        """, (transaction_id, user_id))
        orders = cursor.fetchall()  # There may be multiple orders for this transaction

        # If no orders found, redirect with a flash message
        if not orders:
            flash("No orders found for this transaction.", "danger")
            return redirect(url_for('order_history'))

        print("Orders fetched:", orders)  # Debugging

        # Collect all order IDs for this transaction
        order_ids = [order['order_id'] for order in orders]
        print("Order IDs for transaction:", order_ids)  # Debugging

        if not order_ids:
            flash("No order IDs found for this transaction.", "danger")
            return redirect(url_for('order_history'))

        # Fetch the order items for all collected order IDs
        format_strings = ','.join(['%s'] * len(order_ids))  # Create placeholders for SQL IN clause
        print("Format strings for SQL:", format_strings)  # Debugging

        cursor.execute(f"""
            SELECT 
                oi.order_id,
                p.product_name, 
                p.product_image, 
                oi.quantity, 
                oi.price, 
                (oi.quantity * oi.price) AS subtotal,
                o.status AS order_status
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.order_id IN ({format_strings})
        """, order_ids)

        order_items = cursor.fetchall()
        print("Order items fetched:", order_items)  # Debugging

        # Handle case if no items are fetched
        if not order_items:
            flash("No items found for this order.", "danger")
            return redirect(url_for('order_history'))

        # Group order_items by order_id
        grouped_order_items = defaultdict(list)
        for item in order_items:
            grouped_order_items[item['order_id']].append(item)

        print("Grouped order items:", grouped_order_items)  # Debugging

        # Dynamically calculate total price for each order
        total_price = sum(item['subtotal'] for item in order_items)
        print("Total price calculated:", total_price)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        print("Error Details:", str(e))
        return redirect(url_for('order_history'))

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

    # Render the order summary page with fetched data
    return render_template(
        'order_summary.html',
        orders=orders,
        grouped_order_items=grouped_order_items,
        total_price=total_price
    )


# def send_order_confirmation_email(user_id, order_id, transaction_id):
#     try:
#         # Fetch order details from the database
#         connection = create_connection()
#         cursor = connection.cursor(dictionary=True)

#         # Fetch order details
#         cursor.execute("""
#             SELECT o.first_name, o.last_name, o.total_price, o.order_date, o.shipping_address, o.status, o.email
#             FROM orders o
#             WHERE o.transaction_id = %s
#         """, (transaction_id,))
#         order = cursor.fetchone()

#         # Fetch order items
#         cursor.execute("""
#             SELECT oi.product_name, oi.quantity, oi.price, oi.subtotal
#             FROM order_items oi
#             JOIN products p ON oi.product_id = p.product_id
#             WHERE oi.order_id = %s
#         """, (order_id,))
#         order_items = cursor.fetchall()

#         # Email recipient (the user who placed the order)
#         recipient_email = order['email']

#         # Render the email body with HTML template
#         html_body = render_template('order_confirmation_email.html', order=order, order_items=order_items)

#         # Create email message
#         message = Message(
#             subject=f"Order Confirmation - Transaction ID: {transaction_id}",
#             recipients=[recipient_email],
#             html=html_body
#         )

#         # Send the email
#         mail.send(message)

#         print("Order confirmation email sent successfully.")

#     except Exception as e:
#         print(f"Failed to send order confirmation email: {str(e)}")

#     finally:
#         cursor.close()
#         connection.close()

def send_order_confirmation_email(user_email, order_details, order_items):
    try:
        # Email recipient (the user who placed the order)
        recipient_email = user_email

        # Render the email body with HTML template
        html_body = render_template('order_confirmation_email.html', order=order_details, order_items=order_items)

        # Create email message
        message = Message(
            subject=f"Order Confirmation - HAUL THRIFT SHOP",
            recipients=[recipient_email],
            html=html_body
        )

        # Send the email
        mail.send(message)

        print("Order confirmation email sent successfully.")

    except Exception as e:
        print(f"Failed to send order confirmation email: {str(e)}")



# Outside your route, in a test block or shell@app.route('/orders', methods=['GET'])
@app.route('/orders', methods=['GET'])
@login_required
def view_orders():
    if current_user.role not in ['admin', 'superadmin']:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT o.order_id, o.status, o.order_date, o.total_price, 
                   CONCAT(o.first_name, ' ', o.last_name) AS customer_name, o.shipping_address
            FROM orders o
            ORDER BY o.order_date DESC
        """)
        orders = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template('manage_orders.html', orders=orders)

@app.route('/update_order/<int:order_id>', methods=['POST']) 
@login_required
def update_order_status(order_id):
    if current_user.role not in ['admin', 'superadmin']:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    new_status = request.form.get('status')

    if new_status not in ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled']:
        flash("Invalid status!", "danger")
        return redirect(url_for('view_orders'))

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
        connection.commit()
        flash("Order status updated successfully.", "success")
    except Exception as e:
        flash("Failed to update status. Try again.", "danger")
        print("Update Error:", e)
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('view_orders'))

# @app.route('/seller-orders', methods=['GET'])
# @login_required
# def view_seller_orders():
#     if current_user.role not in ['seller', 'superadmin']:
#         flash("Unauthorized access!", "danger")
#         return redirect(url_for('home'))

#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)

#     try:
#         cursor.execute("""
#             SELECT o.order_id, o.status, o.order_date, o.total_price, 
#                    CONCAT(o.first_name, ' ', o.last_name) AS customer_name, o.shipping_address
#             FROM orders o
#             ORDER BY o.order_date DESC
#         """)
#         orders = cursor.fetchall()
#     finally:
#         cursor.close()
#         connection.close()

#     return render_template('seller_orders.html', orders=orders)

# @app.route('/seller-orders', methods=['GET'])
# @login_required
# def view_seller_orders():
#     # Ensure only sellers and superadmins can access this route
#     if current_user.role not in ['seller', 'superadmin']:
#         flash("Unauthorized access!", "danger")
#         return redirect(url_for('home'))

#     connection = create_connection()
#     cursor = connection.cursor(dictionary=True)

#     try:
#         # Query to fetch orders containing ONLY the seller's products
#         cursor.execute("""
#             SELECT DISTINCT o.order_id, o.status, o.order_date, o.total_price, 
#                    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
#                    o.shipping_address
#             FROM orders o
#             INNER JOIN order_items oi ON o.order_id = oi.order_id
#             INNER JOIN products p ON oi.product_id = p.product_id
#             INNER JOIN users c ON o.user_id = c.id
#             WHERE p.seller_id = %s
#             ORDER BY o.order_date DESC
#         """, (current_user.id,))
#         orders = cursor.fetchall()
#     finally:
#         cursor.close()
#         connection.close()

#     return render_template('seller_orders.html', orders=orders)

@app.route('/seller-orders', methods=['GET'])
@login_required
def view_seller_orders():
    if current_user.role != 'seller':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))

    seller_id = current_user.id  # Assuming `current_user.id` gives the logged-in seller's ID.

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Query to get seller-specific orders and their products
        cursor.execute("""
            SELECT 
                o.order_id, o.status, o.order_date, o.total_price,
                CONCAT(o.first_name, ' ', o.last_name) AS customer_name,
                o.shipping_address, 
                p.product_name, ot.quantity, ot.price
            FROM orders o
            JOIN order_items ot ON o.order_id = ot.order_id
            JOIN products p ON ot.product_id = p.product_id
            WHERE p.seller_id = %s
            ORDER BY o.order_date DESC
        """, (seller_id,))

        # Fetch all rows
        rows = cursor.fetchall()

        # Group orders by `order_id`
        orders = {}
        for row in rows:
            order_id = row['order_id']
            if order_id not in orders:
                orders[order_id] = {
                    "order_id": row['order_id'],
                    "customer_name": row['customer_name'],
                    "shipping_address": row['shipping_address'],
                    "status": row['status'],
                    "total_price": row['total_price'],
                    "order_date": row['order_date'],
                    "items": []
                }
            # Add product details to the order's `items` list
            orders[order_id]["items"].append({
                "product_name": row['product_name'],
                "quantity": row['quantity'],
                "price": row['price']
            })

    finally:
        cursor.close()
        connection.close()

    # Convert orders dict to a list for template rendering
    return render_template('seller_orders.html', orders=list(orders.values()))


# @app.route('/seller/orders/<int:order_id>/update', methods=['GET'])
# @login_required
# def update_seller_order_status(order_id):
#     # Ensure the user is a seller
#     if current_user.role != 'seller':
#         flash("Unauthorized access.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     seller_id = current_user.id
#     new_status = request.args.get('status')  # Parse status from URL query parameter

#     print(f"Order ID: {order_id}, Seller ID: {seller_id}, New Status: {new_status}")  # Debug

#     # Validate the new status
#     valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled']
#     if new_status not in valid_statuses:
#         flash("Invalid status value.", "danger")
#         print("Invalid status provided.")  # Debug
#         return redirect(url_for('view_seller_orders'))

#     connection = create_connection()
#     if not connection:
#         flash("Database connection failed.", "danger")
#         print("Failed to connect to database.")  # Debug
#         return redirect(url_for('view_seller_orders'))

#     cursor = connection.cursor(dictionary=True)

#     try:
#         # Validate the order belongs to the seller
#         cursor.execute("""
#             SELECT 1
#             FROM order_items ot
#             JOIN products p ON ot.product_id = p.product_id
#             WHERE ot.order_id = %s AND p.seller_id = %s
#         """, (order_id, seller_id))
#         result = cursor.fetchone()
#         print("Validation result:", result)  # Debug
#         if not result:
#             flash("Order not found or permission denied.", "danger")
#             return redirect(url_for('view_seller_orders'))

#         # Update the order status
#         cursor.execute("""
#             UPDATE orders
#             SET status = %s
#             WHERE order_id = %s
#         """, (new_status, order_id))
#         connection.commit()
#         print(f"Order {order_id} status updated to {new_status}.")  # Debug

#         flash(f"Order status updated to '{new_status}' successfully.", "success")
#         return redirect(url_for('view_seller_orders'))

#     except Exception as e:
#         connection.rollback()  # Rollback any changes in case of error
#         flash("An error occurred while updating the order status.", "danger")
#         print(f"Error occurred: {str(e)}")  # Log the exception
#         return redirect(url_for('view_seller_orders'))

#     finally:
#         # Close the cursor and connection
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()

# @app.route('/seller/orders/<int:order_id>/update', methods=['GET'])
# @login_required
# def update_seller_order_status(order_id):
#     # Ensure the user is a seller
#     if current_user.role != 'seller':
#         flash("Unauthorized access.", "danger")
#         return redirect(url_for('view_seller_orders'))  # Redirect to orders management page

#     seller_id = current_user.id
#     new_status = request.args.get('status')  # Parse status from URL query parameter

#     # Validate the new status
#     valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled']
#     if new_status not in valid_statuses:
#         flash("Invalid status value.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     connection = create_connection()
#     if not connection:
#         flash("Database connection failed.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     cursor = connection.cursor(dictionary=True)

#     try:
#         # Validate the order belongs to the seller
#         cursor.execute("""
#             SELECT ot.product_id, ot.quantity
#             FROM order_items ot
#             JOIN products p ON ot.product_id = p.product_id
#             WHERE ot.order_id = %s AND p.seller_id = %s
#         """, (order_id, seller_id))

#         order_items = cursor.fetchall()
#         if not order_items:
#             flash("Order not found or permission denied.", "danger")
#             return redirect(url_for('view_seller_orders'))

#         # Clear any additional unread results if necessary
#         cursor.fetchall()

#         # Update the order status
#         cursor.execute("""
#             UPDATE orders
#             SET status = %s
#             WHERE order_id = %s
#         """, (new_status, order_id))
#         connection.commit()

#         # If the new status is 'Cancelled', restore the product stock and set product_status to 'Active'
#         if new_status == 'Cancelled':
#             for item in order_items:
#                 restore_stock_query = """
#                     UPDATE products
#                     SET product_stock = product_stock + %s, product_status = 'Active'
#                     WHERE product_id = %s
#                 """
#                 cursor.execute(restore_stock_query, (item['quantity'], item['product_id']))

#             connection.commit()
#             flash(f"Order status updated to '{new_status}', stock restored, and product status set to 'Active' successfully.", "success")
#         else:
#             flash(f"Order status updated to '{new_status}' successfully.", "success")

#         return redirect(url_for('view_seller_orders'))

#     except Exception as e:
#         connection.rollback()  # Rollback any changes in case of error
#         flash("An error occurred while updating the order status.", "danger")
#         print(f"Error occurred: {str(e)}")
#         return redirect(url_for('view_seller_orders'))

#     finally:
#         # Close the cursor and connection
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()

# @app.route('/seller/orders/<int:order_id>/update', methods=['GET'])
# @login_required
# def update_seller_order_status(order_id):
#     if current_user.role != 'seller':
#         flash("Unauthorized access.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     seller_id = current_user.id
#     new_status = request.args.get('status')  # Get status from query parameter

#     # Validate the new status
#     valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled']
#     if new_status not in valid_statuses:
#         flash("Invalid status value.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     connection = create_connection()
#     if not connection:
#         flash("Database connection failed.", "danger")
#         return redirect(url_for('view_seller_orders'))

#     cursor = connection.cursor(dictionary=True)

#     try:
#         # Validate the order belongs to the seller
#         cursor.execute("""
#             SELECT ot.product_id, ot.quantity
#             FROM order_items ot
#             JOIN products p ON ot.product_id = p.product_id
#             WHERE ot.order_id = %s AND p.seller_id = %s
#         """, (order_id, seller_id))

#         order_items = cursor.fetchall()
#         if not order_items:
#             flash("Order not found or permission denied.", "danger")
#             return redirect(url_for('view_seller_orders'))

#         # Update the order status
#         cursor.execute("""
#             UPDATE orders
#             SET status = %s
#             WHERE order_id = %s
#         """, (new_status, order_id))
#         connection.commit()

#         # Handle stock restoration for 'Cancelled' orders
#         if new_status == 'Cancelled':
#             restore_stock_query = """
#                 UPDATE products p
#                 JOIN order_items oi ON p.product_id = oi.product_id
#                 SET p.product_stock = p.product_stock + oi.quantity,
#                     p.product_status = 'Active'
#                 WHERE oi.order_id = %s
#             """
#             cursor.execute(restore_stock_query, (order_id,))
#             connection.commit()
#             flash("Order cancelled. Stock restored and product status set to 'Active'.", "success")
#         else:
#             flash(f"Order status updated to '{new_status}' successfully.", "success")

#     except Exception as e:
#         connection.rollback()  # Rollback changes in case of error
#         print(f"Error occurred: {e}")
#         flash("An error occurred while updating the order status.", "danger")
#     finally:
#         cursor.close()
#         connection.close()

#     return redirect(url_for('view_seller_orders'))

@app.route('/seller/orders/<int:order_id>/update', methods=['POST'])
@login_required
def update_seller_order_status(order_id):
    print(f"Updating order {order_id}")
    if current_user.role != 'seller':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('view_seller_orders'))

    seller_id = current_user.id
    data = request.get_json()  # Get JSON data from the request
    new_status = data.get('status')  # Extract the status from the JSON

    # Validate the new status
    valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        flash("Invalid status value.", "danger")
        return redirect(url_for('view_seller_orders'))

    connection = create_connection()
    if not connection:
        flash("Database connection failed.", "danger")
        return redirect(url_for('view_seller_orders'))

    cursor = connection.cursor(dictionary=True)

    try:
        # Validate the order belongs to the seller
        cursor.execute("""
            SELECT ot.product_id, ot.quantity
            FROM order_items ot
            JOIN products p ON ot.product_id = p.product_id
            WHERE ot.order_id = %s AND p.seller_id = %s
        """, (order_id, seller_id))

        order_items = cursor.fetchall()
        if not order_items:
            flash("Order not found or permission denied.", "danger")
            return redirect(url_for('view_seller_orders'))

        # Update the order status
        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE order_id = %s
        """, (new_status, order_id))
        connection.commit()

        # Handle stock restoration for 'Cancelled' orders
        if new_status == 'Cancelled':
            restore_stock_query = """
                UPDATE products p
                JOIN order_items oi ON p.product_id = oi.product_id
                SET p.product_stock = p.product_stock + oi.quantity,
                    p.product_status = 'Active'
                WHERE oi.order_id = %s
            """
            cursor.execute(restore_stock_query, (order_id,))
            connection.commit()
            flash("Order cancelled. Stock restored and product status set to 'Active'.", "success")
        else:
            flash(f"Order status updated to '{new_status}' successfully.", "success")

    except Exception as e:
        connection.rollback()  # Rollback changes in case of error
        print(f"Error occurred: {e}")
        flash("An error occurred while updating the order status.", "danger")
    finally:
        cursor.close()
        connection.close()

    return jsonify(success=True)  # Return a JSON response


#dinagdag ni ross 12/8/2024 (to display sales)
@app.route('/sales')
def go_to_sales():
    return render_template('/sales.html')

#dinagdag ni ross 12/8/2024 (to create sales analysis)
@app.route('/get_sales_info')
def sales_analysis():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT products.product_name, product_category, order_items.price
            SUM(order_items.price) AS TOTAL SALES
            FROM order_items
            JOIN products
            ON products.product_id = order_items.product_id """)
        data = cursor.fetchall()
        analysis = [{"name": row[0], "category": row[1], "price": row[2]} for row in data]
        return jsonify(analysis)
        
    except Exception as e:
        print('error occured')

#dinagdag ni ross 12/9/2024 (to submit ratings)
@app.route('/rating', methods=['POST'])
def submit_rating():
    try:
        data = request.get_json()
        rating = data.get('rating')
        feedback = data.get('feedback')
    
        if not(1 <= rating <= 5):
            return jsonify({'error':'Invalid rating'})
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO review (stars, feedback)
                VALUES (%s, %s)
            """, (rating, feedback))
            conn.commit()
            conn.close()
            

    except Exception as e:
        print('error')


#dinagdag ni ross (to display ratings)
@app.route('/show_ratings')
def ratings():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ratings.feedback, avg(ratings.star) 
            AS overall_rating
            FROM ratings
            JOIN products
            ON products.product_id = ratings.product_id
            """)
        data = cursor.fetchall()
        review = [{"feedback": row[0], "stars": row[1]} for row in data]
        conn.close()
        return jsonify(review)

        
    except Exception as e:
        print('error')

#route to seller order history
@app.route('/history')
def history():
    return render_template('/seller-order-history.html')

#dinagdag ni ross 12/9/2024 (to show order history)
@app.route('/seller_order_history')
@login_required
def show_history():
    seller_id = current_user.id
    conn = create_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
                SELECT products.product_name, products.product_image, 
                    products.product_price, order_items.quantity, products.created_at
                FROM products
                JOIN order_items ON order_items.product_id = products.product_id
                JOIN orders ON orders.order_id = order_items.order_id
                WHERE products.seller_id = %s
                AND orders.status = 'Completed'
            """, (seller_id,))  
        
        data = cursor.fetchall()

        if not data:
            return jsonify({'message': 'No orders found for this seller.'}), 404
        

        prod_details = [{"name": row[0], "image": row[1], "price": row[2], 
                         "quantity": row[3], "date": row[4]} for row in data]
        
        print(prod_details)
        
        return jsonify(prod_details)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while fetching order history'}), 500
    finally:

        if conn:
            conn.close()

# @app.route('/seller_order_history')
# @login_required
# def show_history():
#     """
#     Fetches order history for the current seller.
#     Returns a JSON response with order details.
#     """
#     seller_id = current_user.id  # Assuming `current_user` provides the authenticated user's ID
#     conn = create_connection()

#     try:
#         cursor = conn.cursor()

#         # SQL query to fetch order history for the seller
#         cursor.execute("""
#             SELECT 
#                 products.product_name, 
#                 products.product_image, 
#                 products.product_price, 
#                 order_items.quantity, 
#                 orders.order_date
#             FROM products
#             JOIN order_items ON order_items.product_id = products.product_id
#             JOIN orders ON orders.order_id = order_items.order_id
#             WHERE products.seller_id = %s
#               AND orders.status = 'Confirmed'
#         """, (seller_id,))
        
#         data = cursor.fetchall()

#         # If no data is found
#         if not data:
#             return jsonify({'message': 'No orders found for this seller.'}), 404

#         # Format the result
#         prod_details = [
#             {
#                 "name": row[0],
#                 "image": row[1] if row[1] else "default.jpg",  # Fallback to default image if null
#                 "price": float(row[2]),  # Convert price to float for frontend compatibility
#                 "quantity": int(row[3]),  # Convert quantity to integer
#                 "date": row[4].strftime('%Y-%m-%d')  # Format the date
#             }
#             for row in data
#         ]
        
#         return jsonify(prod_details)

#     except Exception as e:
#         # Log the error for debugging
#         print(f"Error fetching seller order history: {e}")
#         return jsonify({'error': 'An error occurred while fetching order history.'}), 500

#     finally:
#         # Ensure the connection is closed
#         if conn:
#             conn.close()






@app.route('/admin/products', methods=['GET'])
@login_required
def admin_view_products():
    if current_user.role != 'superadmin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    # Create a connection to the database
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Updated query to fetch first name and last name from the users table
        cursor.execute("""
            SELECT p.*, u.first_name, u.last_name, s.shop_name 
            FROM products p
            JOIN sellers s ON p.seller_id = s.seller_id
            JOIN users u ON s.user_id = u.id
        """)
        products = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    # Render the products page and pass the products data
    return render_template('admin_view_products.html', products=products)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    if current_user.role != 'superadmin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('superadmin'))

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Delete the product from the products table
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        connection.commit()

        flash("Product deleted successfully.", "success")
        return redirect(url_for('admin_view_products'))

    except Exception as e:
        # Rollback in case of any error
        connection.rollback()
        flash(f"Error occurred: {str(e)}", "danger")
        return redirect(url_for('admin_view_products'))

    finally:
        cursor.close()
        connection.close()    


@app.route('/manage-users', methods=['GET', 'POST'])
@login_required
def admin_manage_user():
    connection = create_connection()
    if connection is None:
        flash('Database connection failed!', 'danger')
        return redirect(url_for('superadmin_dashboard'))

    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            # Handle role update
            if 'update_role' in request.form:
                user_id = request.form['user_id']
                new_role = request.form['role']

                cursor.execute("""
                    UPDATE users
                    SET role = %s
                    WHERE id = %s
                """, (new_role, user_id))

                connection.commit()
                flash('User role updated successfully!', 'success')
                return redirect(url_for('admin_manage_user'))

            # Handle user deletion
            if 'delete_user' in request.form:
                user_id = request.form['delete_user']

                # Delete the user from the database
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                connection.commit()

                flash('User deleted successfully!', 'success')
                return redirect(url_for('admin_manage_user'))

        # Fetch users with roles 'seller' and 'user'
        cursor.execute("SELECT * FROM users WHERE role IN ('seller', 'user')")
        users = cursor.fetchall()

        return render_template('manage_users.html', users=users, user=current_user)

    except Error as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('superadmin_dashboard'))
    finally:
        cursor.close()
        connection.close()

@app.route('/rate-seller', methods=['POST'])
@login_required
def rate_seller():
    buyer_id = current_user.id
    seller_id = request.form['seller_id']
    rating = int(request.form['rating'])
    review = request.form['review']
    product_id = request.form['product_id']  # Store the product ID

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if the buyer has already rated the product
        cursor.execute("""
            SELECT * FROM seller_ratings
            WHERE buyer_id = %s AND product_id = %s
        """, (buyer_id, product_id))

        existing_rating = cursor.fetchone()

        if existing_rating:
            # If the rating already exists, flash a message and don't insert the new rating
            flash("You have already rated this product.", "info")
        else:
            # Insert the rating and review into the seller_ratings table
            cursor.execute("""
                INSERT INTO seller_ratings (buyer_id, seller_id, product_id, rating, review)
                VALUES (%s, %s, %s, %s, %s)
            """, (buyer_id, seller_id, product_id, rating, review))

            connection.commit()
            flash('Your rating has been submitted successfully!', 'success')

    except Exception as e:
        flash(f'Error submitting rating: {e}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('rate_order'))



@app.route('/rate-orders', methods=['GET'])
@login_required
def rate_order():
    # Create a cursor object to interact with the database
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)  # Fetch results as dictionary

    # Query to get completed orders for the current user, with associated products and rating status
    cursor.execute("""
        SELECT o.order_id, o.total_price, o.order_date, o.status, o.seller_id, p.product_id, p.product_name, 
               p.product_description, p.product_category, p.product_size, p.product_price, p.product_condition, 
               (SELECT COUNT(*) FROM seller_ratings pr WHERE pr.product_id = p.product_id AND pr.buyer_id = %s) AS rated
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.user_id = %s AND o.status = 'Completed'
    """, [current_user.id, current_user.id])

    # Fetch all results
    completed_orders = cursor.fetchall()

    # Close the cursor after use
    cursor.close()

    # If there are no completed orders
    if not completed_orders:
        flash("You have no completed orders yet.", 'info')

    # Return the data as a dictionary to the template
    return render_template('order_ratings.html', orders=completed_orders)

@app.route('/seller/<int:seller_id>')
def seller_details(seller_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch seller details
    cursor.execute("""
        SELECT sellers.shop_name, sellers.bio, sellers.updated_at, users.profile_picture
        FROM sellers
        JOIN users ON sellers.user_id = users.id
        WHERE sellers.seller_id = %s
    """, (seller_id,))
    seller = cursor.fetchone()

    if not seller:
        abort(404, description="Seller not found")

    # Calculate last active status
    if seller['updated_at']:
        last_active = seller['updated_at']
        time_diff = datetime.now() - last_active
        minutes = time_diff.total_seconds() // 60

        if minutes < 1:
            active_status = "Active just now"
        elif minutes < 60:
            active_status = f"Active {int(minutes)} minutes ago"
        elif minutes < 1440:
            hours = minutes // 60
            active_status = f"Active {int(hours)} hours ago"
        else:
            days = minutes // 1440
            active_status = f"Active {int(days)} days ago"
    else:
        active_status = "Active unknown"

    # Fetch average rating and rating count for the seller
    cursor.execute("""
        SELECT AVG(rating) AS average_rating, COUNT(rating) AS rating_count
        FROM seller_ratings
        WHERE seller_id = %s
    """, (seller_id,))
    rating_data = cursor.fetchone()

    seller['average_rating'] = rating_data['average_rating'] or 0
    seller['rating_count'] = rating_data['rating_count'] or 0

    # Fetch reviews with buyer details
    cursor.execute("""
        SELECT sr.rating, sr.review, u.first_name AS buyer_name
        FROM seller_ratings sr
        JOIN users u ON sr.buyer_id = u.id
        WHERE sr.seller_id = %s
        ORDER BY sr.id DESC
    """, (seller_id,))
    reviews = cursor.fetchall()

    # Fetch active products by the seller (excluding archived products)
    cursor.execute("""
        SELECT product_id, product_name, product_price, product_image
        FROM products
        WHERE seller_id = %s AND product_status != 'archived'
    """, (seller_id,))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'seller_details.html',
        seller=seller,
        active_status=active_status,
        reviews=reviews,
        products=products
    )

# email_to_test = 'aquinojxse@gmail.com'
# user = User.get_by_email(email_to_test)
# print(user)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)