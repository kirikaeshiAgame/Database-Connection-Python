from flask import Flask, render_template, request, redirect, url_for
from database import Database

app = Flask(__name__)
db = Database()
db.open_connection()

@app.route('/')
def index():
    query = """
    SELECT b.book_id, b.title, b.genre, b.publication_year, b.isbn, 
           a.first_name || ' ' || a.last_name AS author_name
    FROM lab_schema.books b
    JOIN lab_schema.book_authors ba ON b.book_id = ba.book_id
    JOIN lab_schema.authors a ON ba.author_id = a.author_id
    """
    books = db.fetch_all(query)
    return render_template('index.html', books=books)

@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    genre = request.form['genre']
    publication_year = request.form['year']
    isbn = request.form['isbn']
    author = request.form['author']

    author_names = author.split()
    if len(author_names) < 2:
        return "Введите полное имя автора (имя и фамилию)", 400

    first_name = author_names[0]
    last_name = author_names[1]

    query = """
    SELECT lab_schema.save_books(%s, %s, %s::integer, %s, %s, %s)
    """
    try:
        db.execute_query(query, (title, genre, publication_year, isbn, first_name, last_name))
    except Exception as e:
        return f"Ошибка при добавлении книги: {e}", 500
    return redirect(url_for('index'))

@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    query = "SELECT lab_schema.delete_books(%s)"
    try:
        db.execute_query(query, (book_id,))
    except Exception as e:
        return f"Ошибка при удалении книги: {e}", 500
    return redirect(url_for('index'))

@app.route('/filter', methods=['GET'])
def filter_books():
    filter_conditions = []
    params = []

    title_filter = request.args.get('title_filter')
    if title_filter:
        filter_conditions.append("b.title ILIKE %s")
        params.append(f"%{title_filter}%")

    genre_filter = request.args.get('genre_filter')
    if genre_filter:
        filter_conditions.append("b.genre ILIKE %s")
        params.append(f"%{genre_filter}%")

    author_filter = request.args.get('author_filter')
    if author_filter:
        filter_conditions.append("a.first_name || ' ' || a.last_name ILIKE %s")
        params.append(f"%{author_filter}%")

    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')
    if start_year and end_year:
        filter_conditions.append("b.publication_year BETWEEN %s AND %s")
        params.extend([start_year, end_year])
    elif start_year:
        filter_conditions.append("b.publication_year >= %s")
        params.append(start_year)
    elif end_year:
        filter_conditions.append("b.publication_year <= %s")
        params.append(end_year)

    filter_query = " AND ".join(filter_conditions)
    query = """
    SELECT b.book_id, b.title, b.genre, b.publication_year, b.isbn, 
           a.first_name || ' ' || a.last_name AS author_name
    FROM lab_schema.books b
    JOIN lab_schema.book_authors ba ON b.book_id = ba.book_id
    JOIN lab_schema.authors a ON ba.author_id = a.author_id
    """
    if filter_query:
        query += " WHERE " + filter_query

    books = db.fetch_all(query, tuple(params))
    return render_template('index.html', books=books)

if __name__ == "__main__":
    app.run(debug=True)