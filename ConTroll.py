from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from keys import userBlacklist
from twitter_auth import twitterBlueprint, twitter
from flask_oauthlib.client import OAuth
from trollchecker import is_tweet_troll
app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
app.register_blueprint(twitterBlueprint) # twitter authentication module

oauth = OAuth(app)

blocks = dict()
def getTroll(inTweet):
    # restricting our blocks to a single twitter account during testing
    if inTweet['user']['screen_name'] in userBlacklist:
        return is_tweet_troll(inTweet['text'])
    else:
        return False

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

@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']

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
