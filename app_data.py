from flask import current_app as app
from models import db, User, Book, Section, Reader
from datetime import datetime

# def delete_books():
#     # Delete all books
#     db.session.query(Book).delete()
#     db.session.commit()
    
def database():

    db.create_all()

    # delete_books()


    section = [
           Section(name="Science", date_created="11-11-2022" , image = "pxfuel.jpg", description = "Welcome to the Science Section of our library, where curiosity knows no bounds and discovery awaits around every corner. Immerse yourself in the captivating world of science, where the mysteries of the universe are unraveled and the complexities of life are explored."),
           Section(name="Fiction", date_created="11-12-2022" , image = "pxfuel.jpg" , description = "Welcome to the Fiction Section of our library, where imagination knows no bounds and stories come alive on every page. Dive into a world of endless possibilities, where characters leap off the paper and transport you to far-off lands, distant galaxies, and through the depths of the human experience."),
           Section(name="History", date_created="11-10-2022" , image = "pxfuel.jpg" , description = "Welcome to the captivating realm of fiction history housed within the walls of our esteemed library. Traverse through time and imagination as you embark on a journey through the annals of human history, reimagined through the lens of creative storytelling. ")
           ]

    book = [
        Book(name = "A Brief History of Time",section_id = 1 , author = "Stephen Hawking", file ="static\\pdfs\\book1.pdf", description = "This classic book explores the fundamental concepts of physics, including the nature of time, black holes, and the origin of the universe, written in a way accessible to general readers", image = "static\\covers\\lib1.jpg" ),
        Book(name = "Cosmos" ,section_id = 1 , author = "Carl Sagan" , file = "static\\pdfs\\book1.pdf" , description = "In this captivating book, Sagan takes readers on a journey through the universe, discussing topics such as the origins of life, the search for extraterrestrial intelligence, and the wonders of space exploration." , image = "static\\covers\\lib1.jpg" ),
        Book(name = "1984" , section_id = 2 , author = "George Orwell" , file = "static\\pdfs\\book1.pdf", description = "A dystopian novel set in a totalitarian society where the government exercises complete control over its citizens." , image = "static\\covers\\lib1.jpg"),
        Book(name = "To Kill a Mockingbird" , section_id = 2 , author = "Harper Lee" , file = "static\\pdfs\\book1.pdf" , description = " A classic novel that explores themes of racial injustice and moral growth in the American South during the 1930s." , image = "static\\covers\\lib1.jpg"),
        Book(name = "Guns, Germs, and Steel: The Fates of Human Societies" , section_id = 3 , author = "Jared Diamond" , file = "static\\pdfs\\book1.pdf" , description = "This Pulitzer Prize-winning book explores the reasons behind the rise of civilizations and the inequalities among them, examining factors such as geography, agriculture, and technology." , image = "static\\covers\\lib1.jpg"),
        Book(name = "A People's History of the United States" ,section_id = 3 , author = "Howard Zinn" , file = "static\\pdfs\\book1.pdf" , description = "This influential book offers a different perspective on American history, focusing on the experiences of ordinary people, marginalized groups, and dissenters rather than political leaders and elites." , image = "static\\covers\\lib1.jpg")
        ]


    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password='admin', name='admin')
        db.session.add(admin)
        db.session.commit()

    reader = Reader.query.filter_by(email='john@example.com').first()
    if not reader:
        reader = Reader(username='reader1', passhash='password1', name='John Doe', email='john@example.com', registration_date=datetime.now())
        db.session.add(reader)
        db.session.commit()


database()
database()
    




