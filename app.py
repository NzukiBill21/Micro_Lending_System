import os
import random
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import secrets


from config import Config
from models import db, User, Borrower
from forms_auth import LoginForm, RegisterForm

# ✅ Initialize Flask
app = Flask(__name__)
app.config.from_object(Config)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/uploads'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# ✅ Ensure uploads folder exists
os.makedirs(os.path.join("static", "uploads"), exist_ok=True)

# ✅ DB & Migrations
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        flash("✅ Registration successful! You can log in now.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        flash("❌ Invalid username or password!", "danger")
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    borrowers = Borrower.query.all()
    total_borrowers = len(borrowers)
    total_loans = sum(b.loan_amount for b in borrowers)

    return render_template(
        "dashboard.html",
        user=current_user,
        total_borrowers=total_borrowers,
        total_loans=total_loans
    )


def seed_borrowers():
    """Add 20 borrowers to DB only if they don't already exist."""
    if Borrower.query.count() >= 20:
        return

    ethnic_groups = [
        ["Wanjiku", "Kamau", "Wairimu", "Muthoni"],
        ["Mutiso", "Mwikali", "Mutua", "Ndinda"],
        ["Muriuki", "Nkatha", "Mutuma", "Karimi"],
        ["Odhiambo", "Atieno", "Ochieng", "Akinyi"],
        ["Wekesa", "Naliaka", "Barasa", "Mukami"],
        ["Abdi", "Farhia", "Hassan", "Amina"],
        ["Nyaboke", "Onsongo", "Kemunto", "Morara"],
        ["Chacha", "Marwa", "Nyamongo", "Mwita"],
        ["Kiptoo", "Chebet", "Kiplagat", "Jepkoech"]
    ]

    for _ in range(20):
        group = random.choice(ethnic_groups)
        name = random.choice(group)
        loan_amount = random.randint(500_000, 10_000_000)
        status = random.choice(["Active", "Pending", "Defaulted"])
        borrower = Borrower(name=name, loan_amount=loan_amount, status=status)
        db.session.add(borrower)
    
    db.session.commit()

@app.route("/borrowers")
@login_required
def borrowers():
    seed_borrowers()
    all_borrowers = Borrower.query.all()
    return render_template("borrowers.html", borrowers=all_borrowers)

@app.route("/add_loan", methods=["GET", "POST"])
@login_required
def add_loan():
    if request.method == "POST":
        name = request.form.get("name")
        loan_amount = request.form.get("loan_amount")
        status = request.form.get("status")

        borrower = Borrower(name=name, loan_amount=float(loan_amount), status=status)
        db.session.add(borrower)
        db.session.commit()

        flash(f"✅ Borrower {name} added with KES {loan_amount}", "success")
        return redirect(url_for("borrowers"))

    return render_template("add_borrower.html")

@app.route("/edit_borrower/<int:borrower_id>", methods=["GET", "POST"])
@login_required
def edit_borrower(borrower_id):
    borrower = Borrower.query.get_or_404(borrower_id)
    if request.method == "POST":
        borrower.name = request.form.get("name") or borrower.name
        borrower.loan_amount = float(request.form.get("loan_amount") or borrower.loan_amount)
        borrower.status = request.form.get("status") or borrower.status

        db.session.commit()
        flash(f"✅ Borrower {borrower.name} updated!", "success")
        return redirect(url_for("borrowers"))

    return render_template("edit_borrower.html", borrower=borrower)

@app.route("/borrower/<int:borrower_id>")
@login_required
def view_borrower(borrower_id):
    borrower = Borrower.query.get_or_404(borrower_id)
    return render_template("view_borrower.html", borrower=borrower)

@app.route("/delete_borrower/<int:borrower_id>")
@login_required
def delete_borrower(borrower_id):
    borrower = Borrower.query.get_or_404(borrower_id)
    db.session.delete(borrower)
    db.session.commit()
    flash(f"❌ Borrower {borrower.name} deleted!", "danger")
    return redirect(url_for("borrowers"))

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('settings'))

    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(url_for('settings'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        # Delete old pic if not default
        if current_user.profile_pic and current_user.profile_pic != 'default.jpeg':
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic))
            except Exception as e:
                print(f"Failed to delete old profile pic: {e}")

        # Save new filename in DB
        current_user.profile_pic = unique_filename
        db.session.commit()

        flash('Profile picture updated!', 'success')
    else:
        flash('Invalid file type. Only images allowed.', 'danger')

    return redirect(url_for('settings'))



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
