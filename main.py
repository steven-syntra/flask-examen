from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "IUYijhLKIUyLkj"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))
    password_check = db.Column(db.String(50))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/numpy")
def numpy():
    return "<h1>Zet hier de oplossing van de Numpy vraag</h1>"


@app.route("/login", methods=["GET", "POST"])
def login():

    # POST
    if request.method == "POST": # na het verzenden van inloggegevens

        # user opslaan in de sessie
        post_user = request.form["nm"]
        session.permanent = True
        session["user"] = post_user

        # gebruiker opzoeken in de database
        found_user = users.query.filter_by(name=post_user).first()

        # gebruiker bestaat al
        if found_user:
            session["email"] = found_user.email

        # gebruiker bestaat nog niet
        else:
            # gebruiker aanmaken in de database
            usr = users(post_user, "")
            db.session.add(usr)
            db.session.commit()

        flash(f"Login successful!")
        return redirect(url_for("welcome_user"))

    # GET
    else:  # na het opvragen van het inlogformulier

        # gebruiker is al ingelogd
        if "user" in session:
            flash(f"Already logged in!")
            return redirect(url_for("welcome_user"))

        # gebruiker is nog niet ingelogd
        return render_template("login.html")


@app.route("/user", methods=["GET", "POST"])
def welcome_user():

    # als de gebruiker ingelogd is
    if "user" in session:
        user = session["user"]

        if request.method == "POST": # als de gebruiker zijn email opstuurt

            # email opslaan in sessie
            email = request.form["email"]
            session["email"] = email

            # gebruiker opzoeken in de database, en updaten
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()

            flash("Email was saved")

        elif "email" in session:
            email = session["email"]

        else:
            email = None

        return render_template("user.html", email=email)

    # als de gebruiker NIET ingelogd is
    else:
        flash(f"You are not logged in!")
        return redirect(url_for("login"))


@app.route("/view")
def view():
    return render_template("view.html", data=users.query.all())


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    flash( f"You have been logged out!", "info" )
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    return redirect(url_for("user", name="Admin!"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
