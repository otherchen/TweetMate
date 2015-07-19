from tweetmate import app
from flask import render_template, session, redirect, request
import tweepy

### CONSTANTS ###
CONSUMER_KEY = "Tg3cnT83iIGskDX4XYzLfSKEM"
CONSUMER_SECRET = "89rVUFooDhKyNomRlElY6MGsfcNapN9Utvsbnz2FCLqd0Ccd8l"
CALLBACK_URL = "http://localhost:5000/call_back"

### Mandatory Secret Key ###
app.secret_key = 'super_secret_key'

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    1. If request.method is a GET request, render a landing/login page.

    2. If request.method is a POST request, initiate the OAuth dance by
       delegating authorization to Twitter then store the returned 
       request token in the session object.
    """
    if request.method == 'POST':
        # Creating OAuthHandler object with a callback url
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

        # Assigning the redirect_url to the previously assigned callback
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print('Error! Failed to get request token.')

        # Temporarily storing the request token to be passed to the callback view
        session['request_token'] = auth.request_token
        return redirect(redirect_url)
    else:
        # Rendering the landing/login page
        return render_template('login.html')

@app.route('/call_back')
def call_back():
    """
    Creates the user's access token and stores it in the session.
    It also sets the session to be 'permanent' which really defaults
    to 31 days because we want to prevent the user from having to
    go back and do the OAuth dance again.

    Later, probably store the access_key and access_secret in a 
    database like Postgres and get rid of session.permanent = True.
    """
    # Recreate the auth variable with the addiional request token.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    verifier = request.args.get('oauth_verifier')
    token = session.pop('request_token')
    auth.request_token = token

    # Passes in the 'verifier' query parameter that 'proves' the user 
    # has successfuly passed Twitter's authorization. 
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    # Storing the access token in the session object. This is what
    # gives the user access to Twitter's treasure trove.
    session['access_key'] = auth.access_token
    session['access_secret'] = auth.access_token_secret
    session.permanent = True 
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Displays the results of twitter analysis. The contents and 
    purpose of this page is to be determined.
    """
    # Do something with the twitter api
    api = tweepy.API(getAuth())
    user = api.me()

    friends = []
    match = {}

    # Perform different tasks
    if request.method == 'POST':
        if 'tweet' in request.form:
            api.update_status(status=request.form.get('tweet'))
        elif 'user_search' in request.form:
            friends = api.search_users(request.form.get('user_search'), per_page=10)
        elif 'match' in request.form:
            match = api.show_friendship(source_id=user.id, target_id=int(request.form.get('match')))
            # look at sentiment analysis between the two friends

    return render_template('index.html', user=user, friends=friends, match=match)

def getAuth():
    """
    Helper method to create and return the 'auth' object from the access_key 
    and access_secret stored in the session object.
    """
    # Make sure the user is logged in to twitter account
    if session['access_key'] == None or session['access_secret'] == None:
        redirect('/login')

    # Recreating the OAuthHandler
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_key'], session['access_secret'])

    # Give up the auth object
    return auth