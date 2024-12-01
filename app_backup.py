from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.utils import secure_filename
import os
from functools import wraps


app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/upload' #DITO YON
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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
            host='localhost',
            user='root',
            password='',
            database='ecom',
            port = 3307 )
        print("Connection to MySQL DB successful")
        return connection
    except Error as e:
        print(f"The error {e} has occurred")


# call product nigagawa ni ross
def call_product(self, id):
    self.item = id

    connection = create_connection()
    if connection == None:
        print('failed to connect')
        return redirect('index.html')
    cursor = connection.cursor()
    try:
        cursor.execute(
            'SELECT product_name, price FROM products WHERE productID = %s', 
            (self.item)
        )
        product = cursor.fetchone()
        cursor.execute(
            'INSERT INTO '
        )
    except mysql.connector.Error as err:
        pass


#User class now inherits from UserMixin (provides default behavior)
class User(UserMixin):
    def __init__(self, id, email, username, password, role, first_name, middle_name, last_name, suffix, address, mobile_no, id_type=None, gov_id_path=None, dob=None, profile_picture =None):
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
                    user_data.get('dob')
                )
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_id(self):
        """Flask-Login uses this to store and retrieve the user ID"""
        return str(self.id)
    # @staticmethod
    # def get_by_id(user_id):
    #     connection = create_connection()
    #     cursor = connection.cursor(dictionary=True)
    #     try:
    #         cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    #         user_data = cursor.fetchone()
    #         if user_data:
    #             return User(
    #                 user_data['id'], 
    #                 user_data['email'], 
    #                 user_data['username'], 
    #                 user_data['password'],
    #                 user_data['role']
    #             )
    #         return None
    #     finally:
    #         cursor.close()
    #         connection.close()

# Load user callback (needed for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
def allowed_file(filename): #para ito sa mga file na iuupload hinahati nya ung image name tas titingnan kung allowed ba ang jpg png o gifs
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products.html')
def products():
    return render_template('products.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')


# @app.route('/login.html')
# def login():
#     return render_template('login.html')

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

@app.route('/product_details.html')
def product_details():
    return render_template('product_details.html')

# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form['username']
#     email = request.form['email']
#     password = generate_password_hash(request.form['password'])

#     conn = create_connection()
#     if conn is None:
#         flash('Database connection failed!')
#         return redirect(url_for('login'))

#     cursor = conn.cursor()
    
#     try:
#         cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
#         conn.commit()
#         flash('Registration successful!')
#     except Error as e:
#         flash(f"An error occurred: {e}")
#     finally:
#         cursor.close()
#         conn.close()

#     return redirect(url_for('login'))

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']
    
#     connection = create_connection()
#     if connection is None:
#         flash('Database connection failed!')
#         return redirect(url_for('login'))

#     cursor = connection.cursor()
    
#     try:
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()
        
#         if user and check_password_hash(user[3], password):  # Check password
#             user_obj = User(user[0], user[1], user[2], user[3],user[4])  # Create user object
#             login_user(user_obj)  # Log the user in using Flask-Login
#             flash('Login successful!', category='success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid credentials!')
#     except Error as e:
#         flash(f"An error occurred: {e}")
#     finally:
#         cursor.close()
#         connection.close()

#     return redirect(url_for('login'))  # Redirect back to login page if login fails

@app.route('/login', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        abort(404)

    if request.method == 'GET':
        # Serve the registration form
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = create_connection()
        if connection is None:
            flash('Database connection failed!')
            return redirect(url_for('login'))

        cursor = connection.cursor(dictionary=True)  # Enable dictionary-based access
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()  # Fetch user details as a dictionary
            
            if user and check_password_hash(user['password'], password):  # Use column names
                # Instantiate User object with dictionary values
                user_obj = User(
                    user['id'],
                    user['email'],
                    user['username'],
                    user['password'],
                    user['role'],
                    user['first_name'],
                    user.get('middle_name', ''),  # Optional field
                    user['last_name'],
                    user.get('suffix', ''),       # Optional field
                    user['address'],
                    user['mobile_no'],
                    user.get('id_type', ''),      # Optional field
                    user.get('gov_id_path', ''),  # Optional field
                    user.get('dob', '')           # Optional field
                )
                login_user(user_obj)  # Log the user in using Flask-Login
                
                if user_obj.role == 'superadmin':
                    flash('Logged in as Superadmin!', category='success')
                    return redirect(url_for('superadmin'))
                elif user_obj.role == 'seller':
                    return redirect(url_for('seller'))
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

# def role_required(role): #--------ETO AY FOR REUSABLITY(wala pa sa orig)
#     def decorator(func):
#         @wraps(func)  # Preserves the original function's metadata (name, docstring)
#         def wrapper(*args, **kwargs):
#             # Check if user is logged in
#             if not current_user.is_authenticated:
#                 flash("You need to log in first!", category= 'danger')
#                 return redirect(url_for('login'))

#             # Check if user has the required role
#             if current_user.role != role:
#                 # flash("You don't have permission to access this page!", category= 'danger')
#                 # return redirect(url_for('index'))
#                 abort(404)

#             # If checks pass, call the original function
#             return func(*args, **kwargs)    
#         return wrapper
#     return decorator

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

# @app.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     if request.method == 'POST':
#         # Retrieve the updated profile data from the form
#         new_username = request.form.get('username')
#         new_email = request.form.get('email')

#         # Get the current user ID
#         user = current_user

#         # Update the user information in the database
#         connection = create_connection()
#         cursor = connection.cursor()
#         try:
#             cursor.execute("""
#                 UPDATE users SET username = %s, email = %s WHERE id = %s
#             """, (new_username, new_email, user.id))
#             connection.commit()

#             # Update current_user details after updating
#             user.username = new_username
#             user.email = new_email
#             flash('Profile updated successfully!', category='success')
#         except Exception as e:
#             connection.rollback()
#             flash(f'An error occurred: {str(e)}', category='error')
#         finally:a
#             cursor.close()
#             connection.close()

#     return render_template('profile.html', user=current_user)

# @app.route('/superadmin') #--------(wala pa sa orig)
# @role_required('superadmin')
# def superadmin():
#     return render_template('superadmin.html') 

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

@app.route('/logout')
@login_required
def logout():
    logout_user()  # This will log the user out
    flash('You have been logged out.')
    return redirect(url_for('index'))  # Redirect to the home page after logout

# Sell product function (ross)
# @app.route('/add-product', methods=['GET','POST'])
# def sell_product():
#     if request.method == 'GET':
#         render_template('inventory.html')

#     if request.method == 'POST':
#         product_name = request.form('product-name')
#         price = request.form('product-price')
#         quantity = request.form('product-quantity')
#         category = request.form('product-category')
#         description = request.form('product-description')
#         image = request.form('product-image')

#     connection = create_connection()
#     if connection == None:
#         flash('Error Connecting to Database')
#         return render_template ('profile.html')
    
#     else:
#         cursor = connection.cursor()
#         try:
#             cursor.execute(
#                 'INSERT INTO products(product_name, price, quantity, category, description, image) VALUES (%s, %s, %s, %s, %s, %s)',
#                 (product_name, price, quantity, category, description, image)
#             )
#             print('upload product succesful')
#             connection.commit()

#         except mysql.connector.Error as err:
#             pass
#         finally:
#             cursor.close()
#             connection.close()
# Sell product function (ross)

@app.route('/display_products', methods=['GET'])
def display_product():
    if request.method == 'GET':
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM products ORDER BY RAND() LIMIT 1")
            product = cursor.fetchone()
            if product is None:
                flash("No products avaible")
                return redirect("inventory.html")
            else:
                ID, name, price, quantity, category, description, image = product
                return ID, name, price, quantity, category, description, image 
        except mysql.connector.Error as err:
            flash(f'Error retrieving products: {err}')


@app.route('/add-product', methods=['POST'])
def sell_product():
    # if request.method == 'GET':
    #     return render_template('inventory.html')  # Return the template for GET requests

    if request.method == 'POST':
        # Safely retrieve form data
        product_name = request.form.get('product-name')
        price = request.form.get('product-price')
        quantity = request.form.get('product-quantity')
        category = request.form.get('product-category')
        description = request.form.get('product-description')
        image = request.form.get('product-image')

        # Validate required fields
        if not all([product_name, price, quantity, category, description, image]):
            flash('Please fill out all fields.')
            return render_template('inventory.html')  # Return to the form with a message

        # Database connection
        connection = create_connection()
        if connection is None:
            flash('Error Connecting to Database')
            return render_template('inventory.html')  # Show an error page if the DB fails

        else:
            cursor = connection.cursor()
            try:
                # Insert into the database
                cursor.execute(
                    'INSERT INTO products (product_name, price, quantity, category, description, image) VALUES (%s, %s, %s, %s, %s, %s)',
                    (product_name, price, quantity, category, description, image)
                )
                connection.commit()
                flash('Product uploaded successfully!')
            except mysql.connector.Error as err:
                flash(f'Error inserting data into the database: {err}')
            finally:
                cursor.close()
                connection.close()

            return redirect(url_for('inventory'))  # Redirect after successful insertion


# @app.route('/add_to_cart/')
# product_id = request.form()
# call_product()

# @app.route('/superadmin') #-------jose
# @login_required
# @role_required
# def superadmin():
#     if current_user.role == 'superadmin':
#         return render_template('superadmin.html')
#     else:
#         abort(404)

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
    
@app.route('/inventory')
@login_required
def inventory():
    # Fetch inventory data from the database if needed
    # inventory_data = fetch_inventory_data(current_user.id)
    connection = create_connection() # -------- Jeremy (Line 579 to 590)
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products WHERE seller_id = %s", (current_user.id,))
        products = cursor.fetchall()
    except Error as e:
        flash(f'Error retrieving products: {e}')
        products = []
    finally:
        cursor.close()
        connection.close()
    return render_template('inventory.html', user=current_user)

@app.route('/seller-registration', methods=['GET', 'POST']) #-------jose
@login_required
def seller_registration():
    if current_user.role == 'seller':
        flash('You are already a seller!', 'info')
        return redirect(url_for('index'))  # Redirect back to the home page or dashboard

    if request.method == 'POST':
        # Get form data for names
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        suffix = request.form.get('suffix')

        # Get other form data
        id_type = request.form.get('id_type')
        gov_id = request.files.get('gov_id')  # File upload
        dob = request.form.get('dob')
        agree_verification = request.form.get('agree_verification') == 'on'  # Checkbox

        # Validate fields
        if not (id_type and gov_id and dob and agree_verification):
            flash('All fields are required, and you must agree to the verification process!', 'danger')
            return redirect(url_for('seller_registration'))

        # Ensure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Handle file upload
        if gov_id and allowed_file(gov_id.filename):
            filename = secure_filename(gov_id.filename)
            gov_id_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"File will be saved to: {gov_id_path}")
            gov_id.save(gov_id_path)
        else:
            flash('Invalid file type for Government ID. Allowed types: png, jpg, jpeg, pdf.', 'danger')
            return redirect(url_for('seller_registration'))

        # Update database with name changes and other seller registration info
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
                    id_type = %s, 
                    gov_id_path = %s, 
                    dob = %s, 
                    is_verification_agreed = %s,
                    verification_status = %s
                WHERE id = %s
            """, (first_name, middle_name, last_name, suffix, id_type, gov_id_path, dob, agree_verification, 'pending', current_user.id))
            connection.commit()
            flash('Your seller application has been submitted for approval!', 'success')
            return redirect(url_for('index'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('seller_registration.html', user=current_user)


UPLOAD_FOLDER = 'path/to/upload/directory'  # Adjust the path where you want to store the profile pictures
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
            profile_picture = save_profile_pic(profile_file)

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

def save_profile_pic(file): #DI PA NAGANA
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        profile_picture = os.path.join(UPLOAD_FOLDER, filename)
        file.save(profile_picture)  # Save the file to the specified path
        return profile_picture
    return None



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)