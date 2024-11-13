
import json
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


USER_DATA = 'data/users.json'
RECORD_DATA = 'data/records.json'
GOAL_DATA = 'data/goals.json'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json(USER_DATA)
        
        if username in users:
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        
        users[username] = generate_password_hash(password)
        save_json(users, USER_DATA)
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json(USER_DATA)
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')



L_DATA = 'data/l.json'

L_DATA = 'data/l.json'

def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    records = load_json(RECORD_DATA).get(username, [])
    goals = load_json(GOAL_DATA).get(username, [])

    monthly_income = 0
    savings_percentage = 0
    remaining_savings = 0
    projected_savings = 0

    if os.path.exists(L_DATA):
        saved_data = load_json(L_DATA)
        monthly_income = saved_data.get('monthly_income', 0)
        savings_percentage = saved_data.get('savings_percentage', 0)
    
    if request.method == 'POST':
        if 'monthly_income' in request.form:
            monthly_income = float(request.form['monthly_income'])
            if monthly_income > 0:
                savings_percentage = (savings_percentage * saved_data.get('monthly_income', 1)) / monthly_income if saved_data else savings_percentage
                projected_savings = (savings_percentage / 100) * monthly_income
            else:
                savings_percentage = 0
                projected_savings = 0
            saved_data = {'monthly_income': monthly_income, 'savings_percentage': savings_percentage}
            save_json(saved_data, L_DATA)
            flash('Income updated successfully!', 'success')

        if 'savings_percentage' in request.form:
            savings_percentage = float(request.form['savings_percentage'])
            if monthly_income > 0:
                projected_savings = (savings_percentage / 100) * monthly_income
            else:
                projected_savings = 0
            saved_data = {'monthly_income': monthly_income, 'savings_percentage': savings_percentage}
            save_json(saved_data, L_DATA)
            flash('Savings percentage updated successfully!', 'success')

    saved_amount_from_records = sum(record['amount'] for record in records if record['category'] == 'Income')

    goal_progress = sum(goal['saved_amount'] for goal in goals) or sum(goal['target_amount'] * 0.33 for goal in goals)
    target_amount = sum(goal['target_amount'] for goal in goals)

    total_spent = sum(record['amount'] for record in records if record['category'] != 'Income')
    
    return render_template('dashboard.html', records=records, goals=goals,
                           monthly_income=monthly_income, savings_percentage=savings_percentage, 
                           remaining_savings=remaining_savings, projected_savings=projected_savings,
                           total_spent=total_spent, saved_amount_from_records=saved_amount_from_records,
                           goal_progress=goal_progress, target_amount=target_amount)
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        username = session['username']
        
        records = load_json(RECORD_DATA)
        if username not in records:
            records[username] = []
        records[username].append({"amount": amount, "category": category, "date": date})
        save_json(records, RECORD_DATA)
        
        flash('Record added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('addrecord.html')

@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')

@app.route('/set_goal', methods=['GET', 'POST'])
def set_goal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        goal_name = request.form['goal_name']
        target_amount = float(request.form['target_amount'])
        username = session['username']
        
        goals = load_json(GOAL_DATA)
        if username not in goals:
            goals[username] = []
        goals[username].append({"goal_name": goal_name, "target_amount": target_amount, "saved_amount": 0})
        save_json(goals, GOAL_DATA)
        
        flash('Goal set successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('set_goals.html')

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)
