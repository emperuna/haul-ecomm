from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.utils import secure_filename
import os
from functools import wraps


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

app.secret_key = 'dqweqweqw'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not logged in

#-------------------------PANG GENERATE LANG NG PASS NG SUPERADMIN
# hashed_password = generate_password_hash('seller123')
# print(hashed_password)

def create_connection():
    connection = None
    try: 
        connection = mysql.connector.connect(
            host='localhost', port = 3307,
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
    def __init__(self, id, email, username, password, role, first_name, middle_name, last_name, suffix, address, mobile_no, id_type=None, gov_id_path=None, dob=None, profile_picture =None , verification_status=None):
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

    @classmethod
    def get_by_id(cls, user_id):
        connection = create_connection()
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
                    verification_status = user_data.get('verification_status', 'default_value')
                )
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_id(self):
        """Flask-Login uses this to store and retrieve the user ID"""
        return str(self.id)

# Load user callback (needed for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/')
def home():
    return render_template('index.html')


# @app.route('/products')
# def products():
#     search = request.args.get('search', '')
#     category = request.args.get('category', '')
#     condition = request.args.get('condition', '')
#     min_price = request.args.get('min_price', None)
#     max_price = request.args.get('max_price', None)

#     query = "SELECT * FROM products WHERE product_status = 'active'"
#     filters = []

#     # Apply search filter
#     if search:
#         filters.append(f"(product_name LIKE %s OR product_description LIKE %s)")
#         search = f"%{search}%"

#     # Apply category filter
#     if category:
#         filters.append("product_category = %s")

#     # Apply condition filter
#     if condition:
#         filters.append("product_condition = %s")

#     # Apply price range filters
#     if min_price:
#         filters.append("product_price >= %s")
#     if max_price:
#         filters.append("product_price <= %s")

#     # Add filters to the query
#     if filters:
#         query += " AND " + " AND ".join(filters)

#     # Build the parameterized query values
#     values = [search, search] if search else []
#     if category:
#         values.append(category)
#     if condition:
#         values.append(condition)
#     if min_price:
#         values.append(min_price)
#     if max_price:
#         values.append(max_price)

#     # Initialize cursor and fetch results
#     try:
#         create_connection = mysql.connector.connect(
#             host="localhost", user="root", password="", database="ecom"
#         )
#         cursor = create_connection.cursor(dictionary=True) 

#         # Fetch products
#         cursor.execute(query, values)
#         products = cursor.fetchall()

#         # Fetch unique categories and conditions for filters
#         cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
#         categories = cursor.fetchall()

#         cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
#         conditions = cursor.fetchall()

#     except Exception as e:
#         print(f"Error: {e}")
#         products = []
#         categories = []
#         conditions = []
#     finally:
#         # Close database connection
#         if 'cursor' in locals():
#             cursor.close()
#         if 'create_connection' in locals():
#             create_connection.close()

#     return render_template(
#         'products.html', 
#         products=products, 
#         categories=categories, 
#         conditions=conditions
#     )

@app.route('/products')
def products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    condition = request.args.get('condition', '')
    min_price = request.args.get('min_price', None)
    max_price = request.args.get('max_price', None)
    sort_by = request.args.get('sort_by', '')

    query = "SELECT * FROM products WHERE product_status = 'active'"
    filters = []
    values = []

    # Apply search filter
    if search:
        search = f"%{search}%"  # Format the search term
        filters.append("(product_name LIKE %s)")
        values.extend([search])  # Add both search terms for name and description

    # Apply category filter
    if category:
        filters.append("product_category = %s")
        values.append(category)

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

    try:
        # Establish database connection
        with mysql.connector.connect(
            host="localhost", user="root", password="", database="ecom", port=3307
        ) as create_connection:
            cursor = create_connection.cursor(dictionary=True)  # Enable dictionary mode

            # Execute the query with the filters and values
            cursor.execute(query, values)
            products = cursor.fetchall()

            # Fetch all unique categories (even if no products with that category)
            cursor.execute("SELECT DISTINCT product_category FROM products WHERE product_status = 'active'")
            categories = cursor.fetchall()

            # Fetch all unique conditions (even if no products with that condition)
            cursor.execute("SELECT DISTINCT product_condition FROM products WHERE product_status = 'active'")
            conditions = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
        products = []
        categories = []
        conditions = []

    return render_template(
        'products.html', 
        products=products, 
        categories=categories, 
        conditions=conditions
    )



@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

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
            
            # Insert the new user into the database
            cursor.execute("""
                INSERT INTO users (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, password) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, middle_name, last_name, suffix, address, mobile_no, username, email, hashed_password))
            conn.commit()
            flash('Registration successful!', category='success')
        except Error as e:
            flash(f"An error occurred: {e}", category='danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))

@app.route('/cart.html')
def cart():
    return render_template('cart.html')

@app.route('/product/<int:product_id>')
def product_details(product_id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch the selected product
    cursor.execute("""
        SELECT product_id, product_name, product_price, product_category, product_condition,
               product_rating, product_size, product_description, product_image
        FROM products WHERE product_id = %s
    """, (product_id,))
    product = cursor.fetchone()  # Fetch one product as a tuple
    
    # Fetch related products
    cursor.execute("""
        SELECT product_id, product_name, product_price, product_image
        FROM products WHERE product_id != %s LIMIT 4
    """, (product_id,))
    related_products = cursor.fetchall()  # Fetch related products as tuples

    connection.close()
    
    return render_template('product_details.html', product=product, related_products=related_products)

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
                    return redirect(url_for('index'))
            else:
                flash('Invalid credentials!', category='danger')
        except Error as e:
            flash(f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    return redirect(url_for('login'))

def role_required(role): 
    def decorator(func):
        @wraps(func)  # Preserves the original function's metadata (name, docstring)
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if not current_user.is_authenticated:
                flash("You need to log in first!", category='danger')
                return redirect(url_for('login'))

            # Check if user has the required role
            if current_user.role != role:
                abort(404)  # Forbidden if user does not have the required role

            # If checks pass, call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404  

# @app.route('/inventory', methods=['POST'] )
# def product_listing():
#     if request.method == 'POST':
#         product_name =  request.form['product-name']
#         price = request.form['product-price']

#         conn = create_connection()
#         if conn == None:
#             flash('Database connection failed!')
#             return redirect(url_for('login'))
#         else:
#             cursor=conn.cursor()
#             try:
#                 cursor.execute(
#                     "INSERT INTO products (product_name, price) VALUES (%s, %s)", (product_name, price)
#                 )
#                 conn.commit()
#                 flash('stored succesfully')
#             except mysql.connector.Error as err:
#                 pass
#             finally:
#                 cursor.close()
#                 conn.close()

@app.route('/inventory', methods=['GET'])
@login_required
def inventory():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Fetch products from the database for the current seller (or all products)
        cursor.execute("SELECT * FROM products WHERE seller_id = %s", (current_user.id,))
        products = cursor.fetchall()  # Get all products for the seller

        # Pass products to the template
        return render_template('inventory.html', products=products)
    
    except mysql.connector.Error as err:
        flash(f"Error fetching products: {err}", 'danger')
        return redirect(url_for('index'))
    
    finally:
        cursor.close()
        connection.close()


@app.route('/logout')
@login_required
def logout():
    logout_user()  # This will log the user out
    flash('You have been logged out.')
    return redirect(url_for('index'))  # Redirect to the home page after logout


# @app.route('/add-product', methods=['POST'])
# @login_required
# def add_product():
#     if request.method == 'POST':
#         # Get form data
#         product_name = request.form['product-name']
#         price = request.form['product-price']
#         stock = request.form['product-stock']
#         category = request.form['product-category']
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
        
#         # Insert product into the database
#         connection = create_connection()
#         cursor = connection.cursor()
#         try:
#             cursor.execute('''
#                 INSERT INTO products (seller_id, product_name, product_price, product_stock, product_category, 
#                                       product_condition, product_size, product_description, product_image)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ''', (current_user.id, product_name, price, stock, category, product_condition, product_size, description, image_filename))
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
    if request.method == 'POST':
        # Get form data
        product_name = request.form['product-name']
        price = request.form['product-price']
        stock = request.form['product-stock']
        category = request.form['product-category']
        subcategory = request.form['product-subcategory']  # Get subcategory data
        product_condition = request.form['product-condition']
        product_size = request.form['product-size']
        description = request.form['product-description']
        
        # Get image data
        product_image = request.files['product-image']
        if product_image:
            # Ensure secure filename
            image_filename = secure_filename(product_image.filename)
            
            # Set the folder for product images
            folder_name = 'products'  # Set the subfolder for products
            
            # Construct the target path to save the file
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
            os.makedirs(folder_path, exist_ok=True)  # Create the subfolder if it doesn't exist
            
            # Save the image file in the correct folder
            image_path = os.path.join(folder_path, image_filename)
            product_image.save(image_path)
        else:
            image_filename = None
        
        # Insert product into the database, including the subcategory
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(''' 
                INSERT INTO products (seller_id, product_name, product_price, product_stock, product_category, 
                                      product_subcategory, product_condition, product_size, product_description, product_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (current_user.id, product_name, price, stock, category, subcategory, product_condition, product_size, description, image_filename))
            connection.commit()

            # Return success response
            return jsonify(success=True)
        except Exception as e:
            flash(f"Error adding product: {e}", 'danger')
            return jsonify(success=False)
        finally:
            cursor.close()
            connection.close()


# @app.route('/add_to_cart/')
# product_id = request.form()
# call_product()

@app.route('/superadmin') 
@login_required
@role_required('superadmin')  # Ensure that only superadmins can access this page
def superadmin():
    return render_template('superadmin.html')

@app.route('/seller_dashboard') 
@login_required
@role_required('seller')  
def seller():
    return render_template('seller.html')

@app.route('/seller-registration', methods=['GET', 'POST'])
@login_required
def seller_registration():
    # Prevent access if the user is a pending seller
    print(f"Current verification status: {current_user.verification_status}")
    if current_user.verification_status == 'pending_seller':
        flash('Your seller application is pending approval.', 'info')
        return redirect(url_for('waiting_for_approval'))  # Redirect to the waiting for approval page

    # If the user is already a seller, redirect them to the homepage or dashboard
    if current_user.role == 'seller':
        flash('You are already a seller!', 'info')
        return redirect(url_for('index'))  # Redirect to the home page or dashboard

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
            return redirect(url_for('index'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('seller_registration.html', user=current_user)


# UPLOAD_FOLDER = 'path/to/upload/directory'  # Adjust the path where you want to store the profile pictures
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    profile_picture = user.get('profile_picture') if user else None

    # Handle profile picture upload
    if 'profile_picture' in request.files:
        profile_file = request.files['profile_picture']
        if profile_file:
            # Save the profile picture (assume save_profile_pic handles storage)
            profile_picture = save_file(profile_file)

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

@app.route('/pending-sellers', methods=['GET']) #method para mafetch mga pending sellers
@login_required
def pending_sellers():
    # Ensure only the superadmin can access this
    if current_user.role != 'superadmin':
        flash('Access denied.', category='danger')
        return redirect(url_for('index'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, email, first_name, last_name, gov_id_path FROM users WHERE verification_status = 'pending_seller'")
        pending_seller = cursor.fetchall()

        # Normalize gov_id_path to use forward slashes
        for seller in pending_seller:
            seller['gov_id_path'] = seller['gov_id_path'].replace('\\', '/')
    except Exception as e:
        flash(f"Database error: {e}", category='danger')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        connection.close()

    return render_template('admin_pending_seller.html', pending_seller=pending_seller, user=current_user)



@app.route('/approve-seller/<int:user_id>', methods=['POST'])
@login_required
def approve_seller(user_id):
    if current_user.role != 'superadmin':
        flash('Access denied.', category='danger')
        return redirect(url_for('index'))

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
        return redirect(url_for('index'))

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

def save_file(file, folder_name):
    """
    Save the uploaded file to the specified folder.
    :param file: File object from the form
    :param folder_name: Subfolder to save the file (e.g., 'ids', 'profile', 'products')
    :return: The relative file path for storage
    """
    if file:
        # Ensure secure filename
        filename = secure_filename(file.filename)

        # Construct the target folder path
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        
        # Debug: Print out the folder path to ensure it's correct
        print(f"Saving file to folder: {folder_path}")

        # Ensure the folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder {folder_path} created.")  # Debugging line
        else:
            print(f"Folder {folder_path} already exists.")  # Debugging line

        # Construct full file path
        file_path = os.path.join(folder_path, filename)
        
        # Save the file
        try:
            file.save(file_path)
            print(f"File saved successfully: {file_path}")  # Debugging line
            # Return the relative path (for storing in the database)
            return os.path.join(folder_name, filename)
        except Exception as e:
            print(f"Error saving file: {e}")  # Debugging line
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



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)