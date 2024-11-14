from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/upload' #DITO YON
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

app.secret_key = 'dqweqweqw'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'account'  # Redirect to the login page if not logged in


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
   
    

#User class now inherits from UserMixin (provides default behavior)
class User(UserMixin):
    def __init__(self, id, email, username, password):
        self.id = id
        self.email = email
        self.username = username
        self.password = password

    @staticmethod
    def get_by_email(email):
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                return User(
                    user_data['id'], 
                    user_data['email'], 
                    user_data['username'], 
                    user_data['password']
                )
            return None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_by_id(user_id):
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(
                    user_data['id'], 
                    user_data['email'], 
                    user_data['username'], 
                    user_data['password']
                )
            return None
        finally:
            cursor.close()
            connection.close()

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

@app.route('/index.html')
def home():
    return render_template('index.html', user=current_user)

@app.route('/products.html')
def products():
    return render_template('products.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/account.html')
def account():
    return render_template('account.html')

@app.route('/cart.html')
def cart():
    return render_template('cart.html')

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     conn = create_connection()
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         gender = request.form['gender']
#         birthdate = request.form['birthdate']

#         # Handle profile picture upload
#         if 'profile_picture' in request.files:
#             file = request.files['profile_picture']
#             if file.filename != '' and allowed_file(file.filename):
#                 # Secure the filename and save the file to the UPLOAD_FOLDER
#                 filename = secure_filename(file.filename)
#                 file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 try:
#                     file.save(file_path)
#                     print(f"Profile picture saved successfully to {file_path}")
#                     image_path = filename  # Save only the filename to store in the database
#                 except Exception as e:
#                     print(f"Error saving profile picture: {str(e)}")
#                     image_path = current_user.image_path  # Use the current image if there's an error
#             else:
#                 print("Invalid file or no file selected, using the current image path.")
#                 image_path = current_user.image_path  # Use the current image if the file is invalid
#         else:
#             print("No profile_picture in request.files, using the current image path.")
#             image_path = current_user.image_path  # Fallback to current user's image path

#         try:
#             with conn.cursor() as cursor:
#                 # Insert or update user data in the profile_picture table
#                 sql = """
#                     INSERT INTO profile_picture (name, email, phone, gender, birthdate, profile_picture)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                     ON DUPLICATE KEY UPDATE
#                         name = VALUES(name),
#                         email = VALUES(email),
#                         phone = VALUES(phone),
#                         gender = VALUES(gender),
#                         birthdate = VALUES(birthdate),
#                         profile_pic_path = VALUES(profile_pic_path)
#                 """
#                 cursor.execute(sql, (name, email, phone, gender, birthdate, image_path))
#                 conn.commit()
#             flash('Profile updated successfully!', 'success')
#             return redirect(url_for('profile'))
#         except Exception as e:
#             conn.rollback()
#             flash(f'Error: {str(e)}', 'error')
#         finally:
#             conn.close()
#     else:
#         conn.close()

#     return render_template('profile.html')



@app.route('/product_details.html')
def product_details():
    return render_template('product_details.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    conn = create_connection()
    if conn is None:
        flash('Database connection failed!')
        return redirect(url_for('account'))

    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()
        flash('Registration successful!')
    except Error as e:
        flash(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('account'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    connection = create_connection()
    if connection is None:
        flash('Database connection failed!')
        return redirect(url_for('account'))

    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):  # Check password
            user_obj = User(user[0], user[1], user[2], user[3])  # Create user object
            login_user(user_obj)  # Log the user in using Flask-Login
            flash('Login successful!', category='success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!')
    except Error as e:
        flash(f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('account'))  # Redirect back to account page if login fails


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Retrieve the updated profile data from the form
        new_username = request.form.get('username')
        new_email = request.form.get('email')

        # Get the current user ID
        user = current_user

        # Update the user information in the database
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE users SET username = %s, email = %s WHERE id = %s
            """, (new_username, new_email, user.id))
            connection.commit()

            # Update current_user details after updating
            user.username = new_username
            user.email = new_email
            flash('Profile updated successfully!', category='success')
        except Exception as e:
            connection.rollback()
            flash(f'An error occurred: {str(e)}', category='error')
        finally:
            cursor.close()
            connection.close()

    return render_template('profile.html', user=current_user)

# @app.route('/inventory', methods=['POST'] )
# def product_listing():
#     if request.method == 'POST':
#         product_name =  request.form['product-name']
#         price = request.form['product-price']

#         conn = create_connection()
#         if conn == None:
#             flash('Database connection failed!')
#             return redirect(url_for('account'))
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
def logout():
     logout_user()  # This will log the user out
     flash('You have been logged out.')
     return redirect(url_for('index'))  # Redirect to the home page after logout



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)