import os
from flask import Flask, request, render_template, redirect
from models import models

app = Flask(__name__)

# ----------------------------
# Database Configuration
# ----------------------------
db_url = os.getenv("DATABASE_URL")

if db_url:
    # Heroku sometimes gives `postgres://`, but SQLAlchemy expects
    # `postgresql://`
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    # Local fallback (SQLite)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emp_db.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db = models.db
db.init_app(app)
db.app = app

# Ensure tables exist (quick fix for Heroku)
with app.app_context():
    db.create_all()


# ----------------------------
# Routes
# ----------------------------

# Main/index page
@app.route("/")
def index():
    employees = models.Employee.query.order_by(models.Employee.id).all()
    return render_template(
        "index.html", employees=employees
    )


# Add employee
@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        form_data = request.form
        obj = models.Employee(
            name=form_data["name"],
            gender=form_data["gender"],
            address=form_data["address"],
            phone=form_data["phone"],
            salary=form_data["salary"],
            department=form_data["department"],
        )

        try:
            db.session.add(obj)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(e)
            return "There was an error while adding the employee."

    return render_template("add.html")


# Delete employee
@app.route("/delete", methods=["POST"])
def delete():
    emp_id = request.form.get("emp_id")
    if emp_id:
        obj = models.Employee.query.filter_by(id=int(emp_id)).first()
        if obj:
            try:
                db.session.delete(obj)
                db.session.commit()
                return redirect("/")
            except Exception as e:
                print(e)
                return "There was an error while deleting the employee."

        return render_template(
            "index.html", error="Sorry, the employee does not exist."
        )

    return redirect("/")


# Edit employee
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    obj = models.Employee.query.filter_by(id=int(id)).first()
    if not obj:
        return render_template(
            "edit.html", error="Sorry, the employee does not exist."
        )

    if request.method == "POST":
        form_data = request.form
        obj.name = form_data["name"]
        obj.gender = form_data["gender"]
        obj.address = form_data["address"]
        obj.phone = form_data["phone"]
        obj.salary = form_data["salary"]
        obj.department = form_data["department"]

        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(e)
            return "There was an error while updating the employee."

    return render_template("edit.html", emp=obj)


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Heroku sets $PORT
    app.run(host="0.0.0.0", port=port)
