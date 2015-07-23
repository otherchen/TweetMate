# TweetMate
TweetMate is a web app that allows users to search for and perform sentiment analysis on recent tweets. This serves as an accessory to Twitter and helps enhance the information we can gather from tweets. I know that there are many other Twitter sentiment analysis projects out there but I wanted to build my own as an academic exercise at AngelHack SV 2015. I finished about 3/4 of the project at the hackathon then completed and deployed it 3 days later.

### Technologies
1. Languages: Python, HTML, CSS, JavaScript
2. Frameworks: Flask, Bootstrap
3. WSGI Server: Gunicorn

### API's and Libraries
1. [Tweepy](http://www.tweepy.org/): Great Python library for accessing the Twitter API
2. [AlchemyAPI](http://www.alchemyapi.com/): Provides many semantic text analysis APIs
3. [HighCharts](http://www.highcharts.com/): Simple and effective API for adding interactive charts 

### Features
1. OAuth Login: You log in directly using your Twitter account. This means that you must be registered with Twitter before you can use TweetMate. If for some reason you don't already have a Twitter account, you can sign up for one [here](https://twitter.com/signup)! 
2. Dashboard: View your 20 most recent tweets along with their sentiment analysis scores, signifying if you've been positive or negative lately on Twitter. The range goes from -1 to 1 (-1 being most negative and 1 being most positive). You can also see the direct messages that you have sent along with their sentiment scores. At the bottom of the page, there is a line graph plotting the sentiment scores over time.
3. Friendships:
4. Twitter Search:
