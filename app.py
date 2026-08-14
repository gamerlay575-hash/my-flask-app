from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Session အတွက် လိုအပ်သော Key

# SQLite Database ချိတ်ဆက်ခြင်း
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Table ဖန်တီးခြင်း
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# HTML Layout
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Login System</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px; text-align: center; }
        input { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #0056b3; }
        .msg { color: red; font-size: 14px; margin-bottom: 10px; }
        a { color: #007bff; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p class="msg">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

LOGIN_HTML = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<h2>Login</h2>
<form method="POST">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Log In</button>
</form>
<p style="margin-top:15px;">Account မရှိသေးပါက <a href="/register">Register လုပ်ပါ</a></p>
""")

REGISTER_HTML = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
<h2>Register</h2>
<form method="POST">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" style="background:#28a745;">Register</button>
</form>
<p style="margin-top:15px;">Account ရှိပြီးသားဆိုပါက <a href="/login">Login ဝင်ပါ</a></p>
""")

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return f"""
        <div style="text-align:center; margin-top:50px; font-family:Arial;">
            <h1>Welcome, {session['username']}! 👋</h1>
            <p>Login အောင်မြင်စွာ ဝင်ရောက်ထားပါတယ်။</p>
            <a href="/logout" style="padding:10px 20px; background:red; color:white; text-decoration:none; border-radius:5px;">Logout</a>
        </div>
        """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash("Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
            
    return render_template_string(LOGIN_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("ဒီ Username နဲ့ အကောင့်ရှိပြီးသားဖြစ်ပါသည်။")
        else:
            # Password ကို Hash လုပ်ပြီး Database ထဲ သိမ်းဆည်းခြင်း
            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Register လုပ်ခြင်း အောင်မြင်ပါသည်။ Login ဝင်ပါ။")
            return redirect(url_for('login'))
            
    return render_template_string(REGISTER_HTML)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Database table များ မရှိသေးပါက ဆောက်ပေးမည်
    app.run(debug=True)
