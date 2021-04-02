from flask_sqlalchemy import SQLAlchemy
import bcrypt


db = SQLAlchemy()


# Model for database

# User table, with general information for users
# Money is treated equal for lenders and borrowers
class User (db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    money = db.Column(db.Integer, nullable=False)
    # Relationship with tables Lender and Borrower
    lender = db.relationship("Lender", uselist=False, backref="user")
    borrower = db.relationship("Borrower", uselist=False, backref="user")

# Function to made hash password
def hashPassword(password):
    return bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())


# Function to validate hash password
def validatePassword(password, password_hash):
    if bcrypt.hashpw(password.encode("utf8"), password_hash) == password_hash:
        return True
    else:
        return False


# Lender table with specific information of lenders
class Lender(db.Model):
    __tablename__ = "lender"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))


# Borrower table with specific information of borrower
class Borrower(db.Model):
    __tablename__ = "borrower"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    money_for =  db.Column(db.String, nullable=False)
    description =  db.Column(db.String(255), nullable=False)
    needed_money = db.Column(db.Integer)


# Lender_Borrower table, with information from transactions
# between lenders and borrower
class Lender_Borrower(db.Model):
    __tablename__ = "lender_borrower"
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lender.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'))
    mount_lent = db.Column(db.Integer)
    lender = db.relationship("Lender", uselist=False, backref="lender_borrower")
    borrower = db.relationship("Borrower", uselist=False, backref="lender_borrower")

