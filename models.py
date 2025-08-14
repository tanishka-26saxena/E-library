from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(80), unique= True, nullable= False)
    passhash = db.Column(db.String(100), unique= True, nullable= False)
    name = db.Column(db.String(100), nullable= True)
    

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    author = db.Column(db.String(100), nullable = False)
    file = db.Column(db.String)
    description = db.Column(db.String, nullable = False)
    image = db.Column(db.String)
    feedback = db.relationship('feedback', backref='book', lazy=True)

class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable= False)
    date_created = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable = False)
    image = db.Column(db.String)
    books = db.relationship('Book', backref='section', lazy=True)

class Reader(db.Model):
    __tablename__ = 'reader'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passhash = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    books_issued = db.relationship('Book', secondary='books_issued', backref='readers', lazy=True)
    registration_date = db.Column(db.DateTime, nullable=False)
    books_count = db.Column(db.Integer, default=0)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)
    
books_issued = db.Table('books_issued',
    db.Column('reader_id', db.Integer, db.ForeignKey('reader.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)

class Request_book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('reader.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='pending')
    expiry_date = db.Column(db.DateTime, nullable=True)

class feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('reader.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    ratings = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String, nullable=True)
    feedback_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    reader = db.relationship('Reader', backref=db.backref('feedbacks', lazy=True))








    