# TweetMate
TweetMate is a web app that allows users to search for and perform sentiment analysis on recent tweets. This serves as an accessory to Twitter and helps enhance the information we can gather from tweets. I know that there are many other Twitter sentiment analysis projects out there but I wanted to build my own as an academic exercise at AngelHack SV 2015. I finished about 3/4 of the project at the hackathon then completed and deployed it 3 days later.

### Technologies
1. **Languages**: Python, HTML, CSS, JavaScript
2. **Frameworks**: Flask, Bootstrap
3. **WSGI Server**: Gunicorn

### API's and Libraries
1. **[Tweepy](http://www.tweepy.org/)**: Great Python library for accessing the Twitter API
2. **[AlchemyAPI](http://www.alchemyapi.com/)**: Provides many semantic text analysis APIs
3. **[HighCharts](http://www.highcharts.com/)**: Simple and effective API for adding interactive charts 

### Features
1. **OAuth Login**: Log in directly using an existing Twitter account. Note that you must be registered with Twitter to use TweetMate. If for some reason you don't already have a Twitter account, you can sign up for one [here](https://twitter.com/signup)! 

2. **Dashboard**: View your recent tweets and direct messages along with their sentiment analysis scores. Combined, these scores are used to calculate if you've been negative or positive lately on Twitter. The scores produced for each tweet will be between -1 and 1 (-1 being the most negative and 1 being the most positive). Learn more about sentiment analysis [here](https://en.wikipedia.org/wiki/Sentiment_analysis).

3. **Friendships**: Search for users by name or username. Find out whether someone is following you, blocking you, or muting you. Also find out if you're following or blocking someone else.

4. **Twitter Search**: Search for tweets by keyword or phrase. Find out how the Twittersphere is feeling about a certain topic through the positivity and/or negativity of each tweet.
