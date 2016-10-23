# module for setting up authentication with Twitter
from flask import g, session, request, url_for, flash
from flask import redirect, Blueprint

import keys
from flask_oauthlib.client import OAuth

twitterBlueprint = Blueprint('twitter_auth', __name__)
oauth = OAuth(twitterBlueprint)

twitter = oauth.remote_app(
    'twitter',
    consumer_key=keys.CONSUMER_KEY,
    consumer_secret=keys.CONSUMER_SECRET,
    base_url="https://api.twitter.com/1.1/",
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

@twitterBlueprint.route('/login')
def login():
    callback_url = url_for('twitter_auth.oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@twitterBlueprint.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@twitterBlueprint.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))