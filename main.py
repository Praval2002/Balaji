from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,cast, Date
from werkzeug.utils import secure_filename
from datetime import datetime,date
import sqlite3
from sqlalchemy import text
from calendar import monthrange
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'
DATABASE = 'Bala_test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Bala_test.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=True)
    expenses = db.Column(db.Numeric(10, 2), nullable=True)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    expenses_list = db.relationship('Expense', backref='user')

class Expense(db.Model):
    __tablename__ = 'expense'

    expense_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('cleared', 'pending'), default='pending')
    amount = db.Column(db.Numeric(10, 2), nullable=True)
    expense_image = db.Column(db.String(255), nullable=True)

with app.app_context():
    db.create_all()

def check_user_credentials(username, password):
    conn = sqlite3.connect('Bala_test.db') 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user  
    else:
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print("pass",password)
        if not username or not password:
            flash('Both fields are required!', 'error')
            return render_template('index.html')
        print(f"Attempting to login with username: '{username}'")  
        user = check_user_credentials(username, password)
        if user:
            print("User found:", user)
            session['user_id'] = user[0]
            if user[6] == 'admin':
                return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('user_home'))
        else:
            print("Invalid credentials")
            return render_template('index.html', error='Invalid username or password')

@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/clear_expense/<int:id>', methods=['POST'])
def clear_expense(id):
   conn = sqlite3.connect(DATABASE)
   cursor = conn.cursor()
   
   cursor.execute('UPDATE expense SET status = "cleared" WHERE expense_id = ?', (id,))
   conn.commit()
   conn.close()
   
   return redirect(url_for('monthly_expenses'))

# @app.route('/user_home', methods=['GET', 'POST'])
# def user_home():
#     if request.method == 'POST':
#         amount = request.form['amount']
#         expense_date = request.form['expense_date']
#         expense_image = request.files.get('expense_image')
#         if expense_image:
#             filename = secure_filename(expense_image.filename)
#             expense_image_path = os.path.join('static/uploads', filename)
#             expense_image.save(expense_image_path)
#         else:
#             expense_image_path = None  
#         user_id = session.get('user_id')
#         print(f"Amount: {amount}")
#         print(f"Expense Date: {expense_date}")
#         print(f"User ID: {user_id}")
#         query = '''INSERT INTO expense (user_id, amount, expense_date, expense_image, status)
#                    VALUES (?, ?, ?, ?, ?)'''
#         conn = sqlite3.connect(DATABASE)
#         cursor = conn.cursor()
#         cursor.execute(query, (user_id, amount, expense_date, expense_image_path, 'pending'))
#         conn.commit()
#         conn.close()
#         return redirect(url_for('expense_claim_success'))

#     return render_template('user_home.html')

@app.route('/admin_add_expense', methods=['GET', 'POST'])
def admin_add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        expense_date = request.form['date']
        user_id = request.form['user']
        print(user_id)
        expense_image = request.files.get('image')
        if expense_image:
            filename = secure_filename(expense_image.filename)
            expense_image_path = os.path.join('static/uploads', filename)
            expense_image.save(expense_image_path)
        else:
            expense_image_path = None  
        print(f"Amount: {amount}")
        print(f"Expense Date: {expense_date}")
        print(f"User ID: {user_id}")
        query = '''INSERT INTO expense (user_id, amount, expense_date, expense_image, status)
                   VALUES (?, ?, ?, ?, ?)'''
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(query, (user_id, amount, expense_date, expense_image_path, 'pending'))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_home'))

    return render_template('admin_add_expense.html')


if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')


@app.route('/expense_claim_success')
def expense_claim_success():
    return render_template('expense_claim_success.html')
@app.route('/add_expense')
def add_expense():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return render_template('add_expense.html',users=users)
@app.route('/view_expenses')
def view_expenses():

    return render_template('view_expenses.html')
@app.route('/view_claims')
def view_claims():
    user_id = session.get('user_id')

    query = '''SELECT expense_id, expense_date, amount, status, expense_image 
               FROM expense WHERE user_id = ?'''
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    claims = cursor.fetchall()
    conn.close()

    return render_template('view_claims.html', claims=claims)


@app.route('/monthly_expenses')
def monthly_expenses():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT expense.amount, expense.expense_image, expense.expense_date, user.name, expense.expense_id  
        FROM expense 
        JOIN user ON expense.user_id = user.id 
        WHERE expense.status = 'pending' 
        AND date(expense.expense_date) >= date(?)
        AND date(expense.expense_date) <= date(?)
    """, (start_date, end_date))
    pending_expenses = cursor.fetchall()

    cursor.execute("""
        SELECT user.id, user.name, user.salary,
               COALESCE(SUM(expense.amount), 0) as total_expenses
        FROM user
        LEFT JOIN expense ON user.id = expense.user_id
        AND expense.status = 'cleared'
        AND date(expense.expense_date) >= date(?)
        AND date(expense.expense_date) <= date(?)
        WHERE user.role = 'user'
        GROUP BY user.id
    """, (start_date, end_date))
    
    cleared_data = cursor.fetchall()
    user_salaries = {
        row[0]: {
            'name': row[1],
            'salary': float(row[2]),
            'total_expenses': float(row[3]),
            'remaining': float(row[2]) - float(row[3])
        }
        for row in cleared_data
    }
    
    conn.close()
    return render_template('monthly_expenses.html', 
                         pending_expenses=pending_expenses,
                         user_salaries=user_salaries,start_date=start_date,end_date=end_date)
@app.route('/manage_users')
def manage_users():
    query = '''SELECT * from user'''
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/user_input')
def user_input():
    return render_template('user_input.html')
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    print("Deleting user with ID:", id)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()


    return render_template('manage_users.html', users=users, message='User deleted successfully')
@app.route('/add_user', methods=['POST'])
def add_user():
    print("Adding a new user...")
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    salary = request.form.get('salary')
    role = request.form.get('role')

    if not name or not username or not salary or not role:
        return render_template('manage_users.html', message='All fields are required')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user (name, username, password , salary, role, created_at) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, username, password ,salary, role, created_at))
    conn.commit()
    conn.close()


    return render_template('admin_home.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('You have been logged out!', 'info')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True,port=8080)
