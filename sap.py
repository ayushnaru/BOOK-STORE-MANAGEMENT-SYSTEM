from flask import Flask, render_template, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(_name_)
CORS(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",                # update your username if needed
    password="2530",  # **use your actual MySQL password**
    database="book_store"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books')
def get_books():
    cursor = db.cursor()
    cursor.execute("""
        SELECT b.isbn, b.title, a.author_name, p.publisher_name, b.price
        FROM books b
        JOIN author a ON b.author_id = a.author_id
        JOIN publisher p ON b.publisher_id = p.publisher_id
    """)
    books = []
    for row in cursor.fetchall():
        books.append({
            'isbn': row[0],
            'title': row[1],
            'author': row[2],
            'publisher': row[3],
            'price': float(row[4])
        })
    return jsonify(books)

@app.route('/add_book_smart', methods=['POST'])
def add_book_smart():
    data = request.get_json()
    cursor = db.cursor()
    # Check or create author
    cursor.execute("SELECT author_id FROM author WHERE author_name=%s", (data['author_name'],))
    author = cursor.fetchone()
    if not author:
        cursor.execute("INSERT INTO author (author_name) VALUES (%s)", (data['author_name'],))
        db.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        author_id = cursor.fetchone()[0]
    else:
        author_id = author[0]
    # Check or create publisher
    cursor.execute("SELECT publisher_id FROM publisher WHERE publisher_name=%s", (data['publisher_name'],))
    publisher = cursor.fetchone()
    if not publisher:
        cursor.execute("INSERT INTO publisher (publisher_name) VALUES (%s)", (data['publisher_name'],))
        db.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        publisher_id = cursor.fetchone()[0]
    else:
        publisher_id = publisher[0]
    # Add book
    cursor.execute(
        "INSERT INTO books (isbn, title, author_id, publisher_id, price) VALUES (%s, %s, %s, %s, %s)",
        (data['isbn'], data['title'], author_id, publisher_id, data['price'])
    )
    db.commit()
    return '', 204

if _name_ == '_main_':
    app.run(debug=True)
