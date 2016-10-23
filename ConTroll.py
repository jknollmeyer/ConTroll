from flask import Flask
from flask import session, request, url_for, flash, g, session
from flask import redirect, render_template
from twitter_auth import twitterBlueprint, twitter
from troll_analysis import is_troll

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
app.register_blueprint(twitterBlueprint) # twitter authentication module

blocks = dict()

def getTroll(inTweet):
    # restricting our blocks to a single twitter account during testing
    if inTweet['user']['screen_name'] == 'controllapphh':
        return is_troll(inTweet['text'])
    else:
        return False


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
    return render_template('index.html', tweets=tweets, blocks=blocks)


# get list of tweets for the user
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
        #flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
        flash('Successfully tweeted your tweet!')
    return redirect(url_for('index'))


# block users who meet the definition of troll
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

if __name__ == '__main__':
    app.run()
