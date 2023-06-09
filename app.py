from datetime import date, datetime
import urllib.request
import bs4 as bs
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, render_template, request
from flask import Flask, request, render_template, request, session, redirect
import pickle
import requests
import pandas as pd
from patsy import dmatrices
import sqlite3
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

HOST=os.environ.get("HOST")
USER=os.environ.get("USER")
PASSWORD=os.environ.get("PASSWORD")
DATABASE=os.environ.get("DATABASE")
PORT=os.environ.get("PORT")

app.config['MYSQL_HOST'] = HOST
app.config['MYSQL_USER'] = USER
app.config['MYSQL_PASSWORD'] =PASSWORD
app.config['MYSQL_DB'] = DATABASE
app.config['MYSQL_PORT'] = PORT

mysql = MySQL(app)
app.secret_key = '17041973984'


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/aboutpr')
def aboutpr():
    return render_template("aboutpr.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if 'email' in request.form and 'password1' in request.form and 'password2' in request.form:
            email = request.form['email']
            password1 = request.form['password1']
            password2 = request.form['password2']

            if password1 != password2:
                return 'Passwords do not match!'
            else:
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO signup (email, password) VALUES (%s, %s)", (email, password1))
                mysql.connection.commit()
                cur.close()
                return redirect('/login')

        else:
            return 'Invalid form data'

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login form data
        email = request.form['email']
        password = request.form['password']

        # Check if the email and password are valid
        result = check_credentials(email, password)
        if result == 'exists':
            # Credentials exist, redirect to homepage
            session['email'] = email
            store_login_timing(email)
            return redirect('/')
        elif result == 'not_found':
            # No matching credentials found, display error
            return redirect('/signup')
        elif result == 'incorrect':
            # Incorrect email or password entered, display error
            error = 'Incorrect email or password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


def check_credentials(email, password):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM signup WHERE email = %s", (email,))
    result = cur.fetchone()
    cur.close()

    if result:
        # Email exists in the signup table, check password
        if result[2] == password:  # Assuming password is stored in index 2
            # Email and password match
            return 'exists'
        else:
            # Incorrect email or password entered
            return 'incorrect'
    else:
        # Email not found in the signup table
        return 'not_found'


def store_login_timing(email):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO login (email, session_timing) VALUES (%s, NOW())", (email,))
    mysql.connection.commit()
    cur.close()


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        review = request.form['review']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO contact (name, email, review) VALUES (%s, %s, %s)", (name, email, review))
        mysql.connection.commit()
        cur.close()

        return redirect('/')

    return render_template('contact.html')


# load the nlp model and tfidf vectorizer from disk
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])


def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list

# convert list of numbers to list (eg. "[1,2,3]" to [1,2,3])


def convert_to_list_num(my_list):
    my_list = my_list.split(',')
    my_list[0] = my_list[0].replace("[", "")
    my_list[-1] = my_list[-1].replace("]", "")
    return my_list


def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())


@app.route("/home")
def home():
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions)


@app.route("/populate-matches", methods=["POST"])
def populate_matches():
    # getting data from AJAX request
    res = json.loads(request.get_data("data"))
    movies_list = res['movies_list']

    movie_cards = {"https://image.tmdb.org/t/p/original"+movies_list[i]['poster_path'] if movies_list[i]['poster_path'] else "/static/movie_placeholder.jpeg": [movies_list[i]['title'], movies_list[i]['original_title'],
                                                                                                                                                                movies_list[i]['vote_average'], datetime.strptime(movies_list[i]['release_date'], '%Y-%m-%d').year if movies_list[i]['release_date'] else "N/A", movies_list[i]['id']] for i in range(len(movies_list))}

    return render_template('recommend.html', movie_cards=movie_cards)


@app.route("/recommend", methods=["POST"])
def recommend():
    # getting data from AJAX request
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    rel_date = request.form['rel_date']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies_org = request.form['rec_movies_org']
    rec_year = request.form['rec_year']
    rec_vote = request.form['rec_vote']
    rec_ids = request.form['rec_ids']

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies_org = convert_to_list(rec_movies_org)
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)

    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = convert_to_list_num(cast_ids)
    rec_vote = convert_to_list_num(rec_vote)
    rec_year = convert_to_list_num(rec_year)
    rec_ids = convert_to_list_num(rec_ids)

    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

    for i in range(len(cast_chars)):
        cast_chars[i] = cast_chars[i].replace(r'\n', '\n').replace(r'\"', '\"')

    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: [rec_movies[i], rec_movies_org[i],
                                    rec_vote[i], rec_year[i], rec_ids[i]] for i in range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i],
                             cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i],
                                    cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    if (imdb_id != ""):
        # web scraping to get user reviews from IMDB site
        sauce = urllib.request.urlopen(
            'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        soup_result = soup.find_all(
            "div", {"class": "text show-more__control"})

        reviews_list = []  # list of reviews
        reviews_status = []  # list of comments (good or bad)
        for reviews in soup_result:
            if reviews.string:
                reviews_list.append(reviews.string)
                # passing the review to our model
                movie_review_list = np.array([reviews.string])
                movie_vector = vectorizer.transform(movie_review_list)
                pred = clf.predict(movie_vector)
                reviews_status.append('Positive' if pred else 'Negative')

        # getting current date
        movie_rel_date = ""
        curr_date = ""
        if (rel_date):
            today = str(date.today())
            curr_date = datetime.strptime(today, '%Y-%m-%d')
            movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d')

        # combining reviews and comments into a dictionary
        movie_reviews = {reviews_list[i]: reviews_status[i]
                         for i in range(len(reviews_list))}

        # passing all the data to the html file
        return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                               vote_count=vote_count, release_date=release_date, movie_rel_date=movie_rel_date, curr_date=curr_date, runtime=runtime, status=status, genres=genres, movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)

    else:
        return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                               vote_count=vote_count, release_date=release_date, movie_rel_date="", curr_date="", runtime=runtime, status=status, genres=genres, movie_cards=movie_cards, reviews="", casts=casts, cast_details=cast_details)


if __name__ == '__main__':
    app.run(debug=True)
