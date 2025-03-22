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
    title = db.Column(db.String(200), nullable=False)
    release = db.Column(db.String(15))
    imdbid = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Movie %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    movies = Movie.query.order_by(Movie.date_created).all()
    return render_template('index.html', movies=movies, previous=request.referrer)

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
def update(id): #to be used later
    movie = Movie.query.get_or_404(id)
    if request.method == 'POST':
        movie.title = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error, movie not updated'
    else:
        return render_template('update.html', movie=movie, previous=request.referrer)

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
    return render_template('search.html', movie_list=movie_list, previous=request.referrer)

@app.route('/add/add/<string:imdbID>', methods=['POST', 'GET'])
def add_movie(imdbID):
    response = requests.get(f'http://www.omdbapi.com/?i={imdbID}&apikey={apikey}')
    title = response.json()['Title']
    release_date = response.json()['Released']
    movie = Movie(title=title, imdbid=imdbID, release=release_date)
    try:
        db.session.add(movie)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error, movie no added'

@app.route('/details/<string:imdbID>')
def details(imdbID):
    response = requests.get(f'http://www.omdbapi.com/?i={imdbID}&apikey={apikey}')
    movie = response.json()
    return render_template('details.html', movie=movie, previous=request.referrer)

if __name__ == '__main__':
    app.run(debug=True)