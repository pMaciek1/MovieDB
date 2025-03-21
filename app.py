from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from api import apikey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)
#db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Movie %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    movies = Movie.query.order_by(Movie.date_created).all()
    return render_template('index.html', movies=movies)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Movie.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error, movie not deleted'

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    movie = Movie.query.get_or_404(id)
    if request.method == 'POST':
        movie.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error, movie not updated'
    else:
        return render_template('update.html', movie=movie)

@app.route('/add/', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        return redirect(f'/add/search?title={title}')

    else:
        return render_template('add.html')

@app.route('/add/search')
def search():
    title = request.args.get('title')
    headers = {"accept": "application/json"}
    response_list = requests.get(f'http://www.omdbapi.com/?s={title}&apikey={apikey}', headers=headers)
    movie_list = []
    for movie in response_list.json()['Search']:
        movie_list.append(movie)
    #return movie_list
    return render_template('search.html', movie_list=movie_list)

@app.route('/add/add/<string:imdbID>', methods=['POST', 'GET'])
def add_movie(imdbID):
    response = requests.get(f'http://www.omdbapi.com/?i={imdbID}&apikey={apikey}')
    title = response.json()['Title']
    movie = Movie(content=title)
    try:
        db.session.add(movie)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error, movie no added'

if __name__ == '__main__':
    app.run(debug=True)