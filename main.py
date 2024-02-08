from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from flask import Flask
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6honzWlSihBXox7C0sKR6b'
db.init_app(app)

bootstrap = Bootstrap5(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


all_books = []


def float_validation(form, field):
    if not isinstance(field.data, float):
        raise ValidationError()


class AddBook(FlaskForm):
    name = StringField('Book Name', validators=[DataRequired(message="Book Name field is required")])
    author = StringField('Book Author', validators=[DataRequired(message="Author field is required")])
    rating = FloatField('Rating', validators=[float_validation])
    add = SubmitField('Add Book')


class Edit(FlaskForm):
    new_rating = FloatField("New Rating", validators=[float_validation])
    change = SubmitField('Change Rating')


@app.route('/')
def home():
    # with app.app_context():
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_bs = result.scalars()
    second_session = db.session.execute(db.select(Book).order_by(Book.title))
    second_all_bs = second_session.scalars()

    return render_template("index.html", robook=second_all_bs, books=all_bs)


@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddBook()
    if form.validate_on_submit():
        new = {
            'title': request.form.get("name"),
            'author': request.form.get("author"),
            'rating': request.form.get("rating")
        }
        all_books.append(new)
        with app.app_context():
            db.session.add(Book(title=new['title'], author=new['author'], rating=new['rating']))
            db.session.commit()
        print(all_books)
        return redirect("/")
    return render_template("add.html", form=form)


@app.route("/edit/<int:book_id>", methods=['POST', 'GET'])
def edit_rating(book_id):
    form = Edit()
    if request.method == "POST" and form.validate_on_submit():
        new_score = request.form.get("new_rating")
        book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        book_to_update.rating = new_score
        db.session.commit()
        return redirect('/')

    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    book_name = book.title
    return render_template("edit_page.html", form=form, book=book)


@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect("/")


# with app.app_context():
#     result = db.session.execute(db.select(Book).order_by(Book.title))
#     all_bs = result.scalars()
#     print(result.)
#     if all_bs.first() is None:
#         print("OK")
#     # for item in all_bs:
#     #     # print(item.author, item.title)


if __name__ == "__main__":
    app.run(debug=True)
