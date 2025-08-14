from flask import current_app as app
from flask import send_file
from datetime import datetime
from flask import render_template, url_for, request, redirect, session
from models import db, User, Section, Book , Reader,Request_book, feedback, check_password_hash 
from datetime import timedelta
from werkzeug.utils import secure_filename 
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use("Agg")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_login' , methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username = username).first()
    if username == '' or password == '':
        return redirect(url_for('admin_login'))
    if not user.check_password(password):
        return redirect(url_for('admin_login'))
    session['user_id'] = user.id
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard', methods=['POST' , 'GET'])
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
  
    parameter = request.args.get('parameter')  
    query = request.args.get('query')

    if parameter == 'Name' and query:  
        sections = Section.query.filter(Section.name.ilike(f'%{query}%')).all() 
    else:
        sections = Section.query.all() 
    
    return render_template('admin_dashboard.html' , admin = User.query.get(session['user_id']), Section = sections)

@app.route('/admin_dashboard/update_section/<int:id>' , methods=['POST'])
def update_section(id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    section = Section.query.get(id)

    if request.method == 'POST':
        section.name = request.form.get('name')
        
        if 'image' in request.files:
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_path = '/static/covers/' + filename.split('.')[0] + '.jpeg'
                section.image = image_path

        section.description = request.form.get('description')
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', admin=User.query.get(session['user_id']), section=section)

@app.route('/admin_dashboard/display_users' ,  methods=['GET', 'POST'])
def display_users():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    users = Reader.query.all()
    return render_template('display_users.html' , users=users)
    
@app.route('/display_users/revoke_book/<int:reader_id>/<int:book_id>' , methods=['POST'])
def revoke_book(reader_id , book_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        reader = Reader.query.get(reader_id)
        book = Book.query.get(book_id)

        if reader and book:
            if book in reader.books_issued:
                reader.books_issued.remove(book)
                reader.books_count -= 1
                db.session.commit()
    
    return redirect(url_for('display_users'))

@app.route('/admin_dashboard/add_section' , methods=['POST'])
def add_section():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.files['image'] 
        
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_path = '/static/covers/' + filename.split('.')[0] + '.jpeg'
        else:
            image_path = None
        
        date_created = request.form.get('date')
        
        if not title or not description or not date_created:
            return redirect(url_for('admin_dashboard'))
        
        date_created = datetime.strptime(date_created, '%Y-%m-%d')
        
        new_section = Section(name=title, description=description, date_created=date_created, image=image_path)
        
        db.session.add(new_section)
        db.session.commit()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/delete_section/<int:id>' , methods=['POST'])
def delete_section(id):
    if 'user_id' not in session:
        return redirect(url_for(admin_login))
    
    if request.method == 'POST':
        section = Section.query.get(id)
        if section:
            Book.query.filter_by(section_id = id).delete()
        
        db.session.delete(section)
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/books' , methods=['POST' , 'GET'])
def display_books():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    books = Book.query.all()

    return render_template('books.html', admin = User.query.get(session['user_id']) , books=Book.query.all())

@app.route('/books/view_books/<int:id>', methods=['POST', 'GET'])
def view_books(id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    section = Section.query.get(id)
    parameter = request.args.get('parameter')  
    query = request.args.get('query')

    if parameter == 'Title' and query:  
        books = Book.query.filter(Book.name.ilike(f'%{query}%')).all() 
    elif parameter == 'Author' and query: 
        books = Book.query.filter(Book.author.ilike(f'%{query}%')).all()
    else:
        books = Book.query.filter_by(section_id=id).all() 

    return render_template('books.html', books=books, section=section, section_id=id)

@app.route('/books/admin_book_details/<int:book_id>', methods=['GET'])
def admin_book_details(book_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    book = Book.query.get(book_id)

    return render_template('admin_book_detail.html', book=book)

@app.route('/add_book/<int:section_id>', methods=['POST' , 'GET'])
def add_book(section_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    file = None  
    image = None 

    if request.method == 'POST':
        name = request.form.get('title')
        description = request.form.get('description')
        if 'file' in request.files:
            file_upload = request.files['file']
            if file_upload:
                filename = secure_filename(file_upload.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_upload.save(file_path)
                file_path = 'static/pdfs/' + filename.split('.')[0] + '.pdf'
                file = file_path
        
        author = request.form.get('author')
        
        if 'image' in request.files:
            image_upload = request.files['image']
            if image_upload:
                filename = secure_filename(image_upload.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_upload.save(image_path)
                image_path = '/static/covers/' + filename.split('.')[0] + '.jpeg'
                image = image_path

        if not name or not author or not description :
            return redirect(url_for('view_books', id=section_id))

        section = Section.query.get(section_id)
        new_book = Book(name=name, description=description, file=file, author=author, image=image, section_id=section_id)
        db.session.add(new_book)
        db.session.commit()
    return redirect(url_for('view_books', id=section_id))

@app.route('/books/update_book/<int:id>' , methods=['POST'])
def update_book(id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    book = Book.query.get(id)

    if request.method == 'POST':
        book.name = request.form.get('name')
        book.description = request.form.get('description')
        
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_path = 'static/pdfs/' + filename.split('.')[0] + '.pdf'
                book.file = file_path
        
        book.author = request.form.get('author')

        if 'image' in request.files:
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_path = '/static/covers/' + filename.split('.')[0] + '.jpeg'
                book.image = image_path

        db.session.commit()
        return redirect(url_for('view_books', id=book.section_id))

    return render_template('books.html', admin=User.query.get(session['user_id']), book=book , section_id=book.section_id)

@app.route('/books/delete_book/<int:id>' , methods=['POST'])
def delete_book(id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        book = Book.query.get(id)
        
        db.session.delete(book)
        db.session.commit()

    return redirect(url_for('view_books', id=book.section_id))

@app.route('/admin_book_details/view_book/<int:id>', methods=['GET'])
def view_book(id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    book = Book.query.get(id)
    if not book:
        return redirect(url_for('display_books'))

    book_file = book.file
    
    return send_file(book_file, mimetype='application/pdf')

@app.route('/user_registeration')
def user_registeration():
    return render_template('user_registeration.html')

@app.route('/user_registeration', methods=['POST' , 'GET'])
def user_registeration_post():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('passhash')

        used_username = Reader.query.filter_by(username = username).first()
        if used_username:
            return redirect(url_for(user_registeration))
    
        used_email = Reader.query.filter_by(email=email).first()
        if used_email:
            return redirect(url_for(user_registeration))
    
        new_reader = Reader(username = username, password = password, name=name, email=email, registration_date = datetime.now())

        db.session.add(new_reader)
        db.session.commit()

        return redirect(url_for('user_login'))
    
    return render_template('user_registeration.html')

@app.route('/user_login')
def user_login():
    return render_template('user_login.html')

@app.route('/user_login', methods=['POST'])
def user_login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    reader = Reader.query.filter_by(username=username).first()

    if not username or not password:
        return redirect(url_for('user_login'))

    if not reader:
        return redirect(url_for('user_login'))

    if not reader.check_password(password):
        return redirect(url_for('user_login'))

    session['user_id'] = reader.id
    return redirect(url_for('user_dashboard'))

@app.route('/user_dashboard', methods=['POST' , 'GET'])
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    section = Section.query.all()
  
    parameter = request.args.get('parameter')  
    query = request.args.get('query')

    if parameter == 'Name' and query:  
        sections = Section.query.filter(Section.name.ilike(f'%{query}%')).all() 
    else:
        sections = Section.query.all() 
   
    return render_template('user_dashboard.html' , reader = Reader.query.get(session['user_id']) , Section = sections)

@app.route('/user_books' , methods=['POST' , 'GET'])
def user_books():
    books = Book.query.all()
    return render_template('user_books.html', reader = Reader.query.get(session['user_id']) , books=Book.query.all())

@app.route('/books/book_details/<int:book_id>', methods=['GET'])
def book_details(book_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('display_books'))

    return render_template('user_book_detail.html', book=book)

@app.route('/books/user_view_books/<int:id>', methods=['POST', 'GET'])
def user_view_books(id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    section = Section.query.get(id)

    books = Book.query.filter_by(section_id=id).all()
  
    parameter = request.args.get('parameter')  
    query = request.args.get('query')

    if parameter == 'Title' and query:  
        books = Book.query.filter(Book.name.ilike(f'%{query}%')).all() 
    elif parameter == 'Author' and query: 
        books = Book.query.filter(Book.author.ilike(f'%{query}%')).all()
    else:
        books = Book.query.filter_by(section_id=id).all() 

    return render_template('user_books.html', books=books, section=section, section_id=id)

@app.route('/books/user_request_book/<int:book_id>', methods = ['POST', 'GET'])
def user_request_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    reader_id = session['user_id']

    oldRequest = Request_book.query.filter_by(reader_id=reader_id, book_id=book_id).first()

    if oldRequest:
        book = Book.query.get(book_id)
        return redirect(url_for('user_view_books', id=book.section_id))
    
    if Request_book.query.filter_by(reader_id=session['user_id'], status='accepted').count() >= 5:

        return redirect(url_for('user_view_books'))
    
    if Request_book.query.filter_by(reader_id=reader_id , book_id=book_id , status = "accepted").first():
        return redirect(url_for('user_dashboard'))
    
    newRequest = Request_book(reader_id = reader_id , book_id=book_id)

    db.session.add(newRequest)
    db.session.commit()

    book = Book.query.get(book_id)
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/admin/view_requests')
def view_requests():
    book_requests = Request_book.query.filter_by(status='pending').all()
    return render_template('view_requests.html', book_requests=book_requests, Reader=Reader, Book=Book)

@app.route('/admin/request_action/<int:id>/<action>' , methods=['POST'])
def request_action(id, action):
    book_request = Request_book.query.get(id)
    if request.method == 'POST':
        if action == 'Accept':
            book_request.status = "accepted"
        
            reader = Reader.query.get(book_request.reader_id)
            book = Book.query.get(book_request.book_id)
            if book is not None:
                reader.books_issued.append(book)
        
            book_request.expiry_date = datetime.now() + timedelta(days=7)
            reader.books_count+=1
        
            db.session.commit()
                
        elif action == 'Deny':
            db.session.delete(book_request) 
            db.session.commit()
            return redirect(url_for('view_requests'))
        
    return redirect(url_for('view_requests'))

@app.route('/my_books')
def my_books():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    reader_id = session['user_id']
    reader = Reader.query.get(reader_id)

    my_books = reader.books_issued

    for book in my_books:
        request = Request_book.query.filter_by(reader_id=reader_id, book_id=book.id, status='accepted').first()
        if request and request.expiry_date and request.expiry_date < datetime.now():
            reader.books_issued.remove(book)

    db.session.commit()

    return render_template('my_books.html', my_books=my_books)

@app.route('/return_books/<int:id>', methods=['POST'])
def return_book(id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    book_return = Request_book.query.filter_by(reader_id=session['user_id'], book_id=id, status='accepted').first()

    if book_return:
        book_return.status = 'pending'

        reader = Reader.query.get(session['user_id'])
        if reader.books_count > 0:
            reader.books_count -= 1
        
        book = Book.query.get(id)
        if book in reader.books_issued:
            reader.books_issued.remove(book)

        db.session.commit()

    return redirect(url_for('my_books'))

@app.route('/feedback', methods=['POST'])
def give_feedback():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        reader_id = session.get('user_id')
        book_id = request.args.get('book_id')
        ratings = request.form.get('ratings')  
        comments = request.form.get('comments')

        if reader_id is None or book_id is None or ratings is None:
            return redirect(url_for('my_books'))
        
        user_feedback = feedback(reader_id=reader_id, book_id=book_id, comments=comments , ratings=ratings, feedback_date=datetime.now())
        db.session.add(user_feedback)
        db.session.commit()

    return redirect(url_for('my_books'))

@app.route('/admin_stats')
def admin_stats():

    total_books = len(Book.query.all())
    total_sections = len(Section.query.all())
    total_Readers = len(Reader.query.all())
  
    Sections = Section.query.all()
    sec= []
    count = []

    for s in Sections:
        sec.append(s.name)
        book_count = len(Book.query.filter_by(section_id = s.id).all())
        count.append(book_count)
  
    plt.bar(sec, count , color ="#164863")
    plt.title('No. of books per Section')
    plt.xlabel('Section')
    plt.xticks(rotation=15, ha='right' , fontsize=8)
    plt.ylabel('No. of books')
    plt.savefig('static/covers/img.png')

    plt.clf()
    return render_template("stats.html" , total_books=total_books , total_sections=total_sections , total_Readers = total_Readers)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))