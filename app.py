from flask import Flask, render_template, request, redirect, session
from db import db, User, Borrower, Lender, Lender_Borrower, hashPassword, validatePassword

app = Flask(__name__)

# BD configs
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://codingdojo:codingodojo@localhost/borrowapp"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///borrowapp.db" # Sqlite3 testing
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'CODING_DOJO'

# Connect db with app var
db.init_app(app)
# Add context for app
with app.app_context():
    db.create_all()  # For creating for model

# Login function
@app.route("/",methods=["GET","POST"])
@app.route("/login",methods=["GET","POST"])
def login():
    # Error message for validation process
    error=None
    if request.method == "POST":
        # If request of login, validation is made
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        # User and password validation
        if user == None  or not validatePassword(password,user.password_hash):
            error = "Error. Email or password not valid"
            return render_template("login.html", error=error)  
        else:
            # If user or password valid, check if lender or borrower
            # and redirect
            session['user_id'] = user.id # Session created
            lender = Lender.query.filter_by(user_id=user.id).first()
            borrower = Borrower.query.filter_by(user_id=user.id).first()
            if lender == None:
                return redirect("/borrower/" + str(user.id))
            elif borrower == None:
                return redirect("/lender/" + str(user.id))
    # Show login webpage
    return render_template("login.html")


# Logout Function
@app.route('/logout')
def logout():
    # If session exist, close it
    if 'user_id' in session :
        session.pop('user_id',None)
    # Redirect to login webpage
    return redirect("/login")


# Register function
@app.route("/register",methods=["GET"])
def register():
    return render_template("register.html")


# Lender register function
@app.route("/register_lender", methods=["POST"])
def register_lender():
    # If registration request made
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        money = request.form.get("money")
        # Check if registered user
        user = User.query.filter_by(email=email).first()
        if user == None:
            new_user = User(first_name=first_name,
                                last_name=last_name,
                                email=email,
                                money=money
                                )
            new_user.password_hash = hashPassword(password)
            lender = Lender(user=new_user)
            db.session.add(new_user)
            db.session.commit()
        else:
            redirect("/register")
    # Redirect to login page
    return redirect("/login")


# Borrower register function
@app.route("/register_borrower", methods=["POST"])
def register_borrower():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        money = 0
        money_for = request.form.get("money_for")
        description = request.form.get("description")
        needed_money = request.form.get("needed_money")
        # Check if registered user
        user = User.query.filter_by(email=email).first()
        if user == None:
            new_user = User(first_name=first_name,
                                last_name=last_name,
                                email=email,
                                money=money,
                                )
            new_user.password_hash = hashPassword(password)
            borrower = Borrower(money_for=money_for,
                                description=description,
                                needed_money=needed_money,
                                user = new_user
                                )
            db.session.add(new_user)
            db.session.commit()
        else:
            redirect("/register")
    return redirect("/login")


# Lender function
@app.route("/lender/<int:id>", methods=["GET", "POST"])
def lender(id):
    # Verify a session was created for the selected user
    if 'user_id' in session and session['user_id'] == id:
        user = User.query.filter_by(id=id).first()
        lender = Lender.query.filter_by(user_id=id).first()
        # Obtain user data
        first_name = user.first_name
        last_name = user.last_name
        money = user.money
        # Current needed Borrowers
        list_help = User.query.join(Borrower, User.id==Borrower.user_id)\
        .add_columns(User.id, User.first_name, User.last_name, Borrower.money_for,
        Borrower.description, Borrower.needed_money, User.money)\
        .filter(Borrower.needed_money - User.money > 0 ).all()
        # Helped Borrowers by lent
        list_lent = db.session.query(Lender_Borrower, Borrower, User)\
            .add_columns(Lender_Borrower.id, User.first_name, User.last_name, Borrower.money_for,
            Borrower.description, Borrower.needed_money, User.money, Lender_Borrower.mount_lent)\
            .filter(Lender_Borrower.lender_id == lender.id,
                    Lender_Borrower.borrower_id == Borrower.id,
                    User.id == Borrower.user_id).all()
        # Show information
        return render_template("lender.html",first_name=first_name,
                                last_name=last_name,
                                money=money,
                                list_help=list_help,
                                list_lent=list_lent
                                )
    else:
        # Redirect to logout function
        return redirect("/logout")


# Lend function
@app.route("/lend", methods=["POST"])
def lend():
    if request.method == "POST":
        # When the lend requirement is made,
        # get data from the lender and borrower
        lent_money = request.form.get("lent_money")
        borrower_id = request.form.get("id")
        lender_id = session['user_id']
        lender = User.query.filter_by(id=lender_id).first()
        borrower = User.query.filter_by(id=borrower_id).first()
        lender.money -= int(lent_money)
        borrower.money += int(lent_money)
        # Table lender_borrower for insertion of new lend
        lender = Lender.query.filter_by(user_id=lender_id).first()
        borrower = Borrower.query.filter_by(user_id=borrower_id).first()
        lender_borrower = Lender_Borrower.query.filter_by(lender_id=lender.id,
                                            borrower_id=borrower.id).first()
        if lender_borrower == None:                                            
            lender_borrower = Lender_Borrower(  lender_id=lender.id,
                                            borrower_id=borrower.id,
                                            mount_lent=lent_money )
            db.session.add(lender_borrower)
        else:
            # If not first lend, update amount
            lender_borrower.mount_lent += int(lent_money)
        db.session.commit()
    return redirect("/lender/" + str(session["user_id"]))


# Borrower function
@app.route("/borrower/<int:id>", methods=["GET", "POST"])
def borrower(id):
    # Verify a session was created for the selected user
    if 'user_id' in session and session['user_id'] == id:
        user = User.query.filter_by(id=id).first()
        borrower = Borrower.query.filter_by(user_id=id).first()
        # Obtain user data
        first_name = user.first_name
        last_name = user.last_name
        email = user.email
        money = user.money
        needed_money = borrower.needed_money
        # List of lenders
        list_lender = db.session.query(Lender_Borrower, Lender, User)\
            .add_columns( User.first_name, User.last_name,User.email,
            Lender_Borrower.mount_lent)\
            .filter(Lender_Borrower.lender_id == Lender.id,
                    Lender_Borrower.borrower_id == borrower.id,
                    User.id == Lender.user_id).all()
        # Show information
        return render_template("borrower.html",first_name=first_name,
                                last_name=last_name,
                                email=email,
                                list_lender=list_lender,
                                money=money,
                                needed_money=needed_money
                                )
    else:
        return redirect("/logout")


if __name__ == '__main__':
    app.run(debug=False)