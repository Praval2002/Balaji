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


SELECT expense.amount, expense.expense_image, expense.expense_date, user.name 
FROM expense 
JOIN user ON expense.user_id = user.id 
WHERE expense.status = 'pending' 
AND expense.expense_date BETWEEN '2025-01-01' AND '2025-01-31';
