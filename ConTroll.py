from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
import keys
from twitter_auth import twitterBlueprint, twitter
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
app.register_blueprint(twitterBlueprint) # twitter authentication module

oauth = OAuth(app)

blocks = dict()
def getTroll(inTweet):
    # restricting our blocks to a single twitter account during testing
    if inTweet['user']['screen_name'] in userBlacklist:
        return is_troll(inTweet['text'])
    else:
        return False

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

@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/')
def index():
    tweets = None
    if g.user is not None:
        resp = twitter.request('statuses/mentions_timeline.json')
        if resp.status == 200:
            tweets = resp.data
            for tweet in tweets:
                tweet['troll'] = getTroll(tweet)
        else:
            flash('Unable to load tweets from Twitter.')
    return render_template('index.html', tweets=tweets)


@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
        )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))

@app.route('/block', methods=['GET'])
def block():
    mentionsResp = twitter.request('statuses/mentions_timeline.json')

    if mentionsResp.status == 200:
        mentions= mentionsResp.data

        for mention in mentions:
            if getTroll(mention) and mention['user']['screen_name'] not in blocks.keys():
                screen_name = mention['user']['screen_name']
                resp = twitter.post('blocks/create.json',data={
                    'screen_name': screen_name
                })

                if g.user['user_id'] not in blocks.keys():
                    blocks[g.user['user_id']] = [screen_name]
                elif screen_name not in blocks[g.user['user_id']]:
                    blocks[g.user['user_id']].append(screen_name)

    return redirect(url_for('index'))

@app.route('/clear', methods=['GET'])
def clear(from_blacklist=True):

    response = twitter.request('blocks/list.json')
    for blockUser in response.data['users']:
        blockScreenName = blockUser['screen_name']
        if blockScreenName in userBlacklist:
            unblockResponse = twitter.post('blocks/destroy.json', data={
                'screen_name': blockScreenName
            })
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
