from tweetmate import app
from flask import render_template, session, redirect, request
import tweepy

### CONSTANTS ###
CONSUMER_KEY = "Tg3cnT83iIGskDX4XYzLfSKEM"
CONSUMER_SECRET = "89rVUFooDhKyNomRlElY6MGsfcNapN9Utvsbnz2FCLqd0Ccd8l"
CALLBACK_URL = "http://localhost:5000/"

### Mandatory Secret Key ###
app.secret_key = 'secret_key'

@app.route('/login')
def login():
    """
    Logs the user into their Twitter account
    """
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    session['request_token'] = auth.request_token
    return redirect(redirect_url)

@app.route('/')
def index():
    """
    Creates the user's access token and stores it in the session.
    Displays the results of user's actions afterwards.
    """
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    verifier = request.args.get('oauth_verifier')
    token = session.pop('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    api = tweepy.API(auth)
    api.update_status(status='Hello World')
    user = {'name': 'Andrew'}  # fake user
    return render_template('index.html', user=user)