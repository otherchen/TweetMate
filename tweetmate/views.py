from tweetmate import app
from flask import render_template, session, redirect, request, url_for
from multiprocessing import Pool, Manager
from alchemyapi import AlchemyAPI
from functools import wraps
import tweepy
import datetime

### CONSTANTS ###
CONSUMER_KEY = "Tg3cnT83iIGskDX4XYzLfSKEM"
CONSUMER_SECRET = "89rVUFooDhKyNomRlElY6MGsfcNapN9Utvsbnz2FCLqd0Ccd8l"

### Mandatory Secret Key ###
app.secret_key = 'super_secret_key'

### Create the AlchemyAPI Object ###
alchemyapi = AlchemyAPI()

### Decorators ###
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'access_key' in session or not 'access_secret' in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

### Login View ###    
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
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, url_for('call_back', _external=True))

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

### Logout View ###
@app.route('/logout')
def logout():
    """ 
    Logout and remove all session data
    """
    session.clear()
    return redirect(url_for('login'))

### Twitter Callback Function ###
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
    return redirect(url_for('dashboard'))

### Profile Dashboard ###
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Displays profile info and some analytics on tweets
    """
    # Do something with the twitter api
    api = tweepy.API(getAuth())
    user = api.me()
    timeline = api.user_timeline()
    messages = api.sent_direct_messages()

    # Sentiment analysis results
    timeline_results = analyze(timeline)
    messages_results = analyze(messages)

    # Adding and counting all scores
    scores_sum = timeline_results['scores_sum']   + messages_results['scores_sum']
    scores_count = timeline_results['scores_count']  + messages_results['scores_count']

    # Putting in a check in case API calls run out
    if scores_count is 0:
        scores_count = 1

    # Time vs Tweets Array
    tl_data = []
    tl_index = 0
    for tweet in timeline:
        tl_date = time_millis(tweet.created_at)
        tl_data.append([tl_date, float(timeline_results['scores_list'][tl_index])])
        tl_index += 1

    # Time vs DM's Array
    dm_data = []
    dm_index = 0
    for message in messages:
        dm_date = time_millis(message.created_at)
        dm_data.append([dm_date, float(messages_results['scores_list'][dm_index])])
        dm_index += 1

    # Calculating overall statistics
    avg_score = scores_sum/scores_count
    if avg_score > .75:
        avg_type = "Fantastic"
    elif avg_score > .5:
        avg_type = "Enjoyable"
    elif avg_score > .25:
        avg_type = "Chillen"
    elif avg_score > .1:
        avg_type = "Okay"
    elif avg_score < -.75:
        avg_type = "Offensive"
    elif avg_score < -.5:
        avg_type = "Rotten"
    elif avg_score < -.25:
        avg_type = "Poor"
    elif avg_score < -.1:
        avg_type = "Meh"
    else:
        avg_type = "Neutral"  

    return render_template('dashboard.html', user=user, timeline=timeline, messages=messages, timeline_results=timeline_results,
        messages_results=messages_results, avg_score=avg_score, avg_type=avg_type, tl_data=tl_data, dm_data=dm_data)

### Friendship Search ###
@app.route('/friendships', methods=['GET', 'POST'])
@login_required
def friendships():
    """
    Displays the results of twitter analysis. The contents and 
    purpose of this page is to be determined.
    """
    # Connect to Twitter
    api = tweepy.API(getAuth())
    user = api.me()

    # Setting default return values
    friends = []
    fship = {}
    query = ""
    selected = ""

    # Perform search and queries using Tweepy API
    if request.method == 'GET' and ('q' in request.args or 'id' in request.args):
        if 'q' in request.args:
            query = request.args.get('q')
            friends = api.search_users(query)
        elif 'id' in request.args:
            fid = request.args.get('id')
            selected = api.get_user(int(fid))
            fship = api.show_friendship(source_id=user.id, target_id=int(fid))

    return render_template('friendships.html', user=user, friends=friends, fship=fship, query=query, selected=selected)

### Tweet Search ###
@app.route('/tweet_search', methods=['GET', 'POST'])
@login_required
def tweet_search():
    """
    Returns the tweet search results
    """
    # Connect to Twitter
    api = tweepy.API(getAuth())
    user = api.me()

    # Returned variables
    found_tweets = []
    tweet_sentiments = {}
    search_data = []
    query = ""

    # Process search query
    if request.method == 'GET' and 'q' in request.args:
        query = request.args.get('q')
        found_tweets = api.search(q=query, count=50)
        tweet_sentiments = analyze(found_tweets)

        # Time vs DM's Array
        index = 0
        for tweet in found_tweets:
            date = time_millis(tweet.created_at)
            search_data.append([date, float(tweet_sentiments['scores_list'][index])])
            index += 1

    return render_template('tweet_search.html', user=user, found_tweets=found_tweets, tweet_sentiments=tweet_sentiments, query=query, search_data=search_data)

### Making a Tweet ###
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Displays the results of twitter analysis. The contents and 
    purpose of this page is to be determined.
    """
    # Connect to Twitter
    api = tweepy.API(getAuth())

    # Tweeting using Tweepy API
    if request.method == 'POST':
        api.update_status(status=request.form.get('tweet'))

    return redirect(url_for('dashboard'))

### Awesome Helper Functions ###
def getAuth():
    """
    Helper method to create and return the 'auth' object from the access_key 
    and access_secret stored in the session object.
    """
    # Recreating the OAuthHandler
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_key'], session['access_secret'])

    # Give up the auth object
    return auth

def analyze(items):
    """ 
    Returns a dictionary full of sentiment analysis information
    """
    # Creating empty storage vessels
    scores_count = 0
    scores_sum = 0.0
    scores_list = []
    types_list = []
    positive_count = 0
    negative_count = 0

    # Reading the content of the list and storing it's sentiment
    # scores and types into arrays. Also finds the max/min scores
    # and the total number of scores/types within the array
    for item in items:
        response = alchemyapi.sentiment('text', item.text)
        if response['status'] == 'OK':
            types_list.append(response['docSentiment']['type'])
            if 'score' in response['docSentiment']:
                scores_list.append(response['docSentiment']['score'])
                scores_sum += float(response['docSentiment']['score'])
                if float(response['docSentiment']['score']) > 0:
                    positive_count += 1;
                elif float(response['docSentiment']['score']) < 0:
                    negative_count += 1;
            else: 
                scores_list.append(0.0)
            scores_count += 1
        else:
            scores_list.append(0.0)
            types_list.append("API Error")
            print('Error in sentiment analysis call: ', response['statusInfo'])

    # Returning dictionary object
    return {
        "scores_sum":scores_sum,
        "scores_count":scores_count,
        "scores_list":scores_list,
        "types_list":types_list,
        "positive_count":positive_count,
        "negative_count":negative_count
    }

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def time_millis(dt):
    return unix_time(dt) * 1000.0