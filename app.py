import json
import os, requests
import flask
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session

htmlcode = """
<html>
<body>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;800&family=Ubuntu:wght@500&display=swap');
* {
  box-sizing: border-box;
}

.bg-image {
  background-image: url("https://images-ext-2.discordapp.net/external/CLKNur7RCVIoCasjtqgZcSPyu2C84SEPIZzcu_mazKo/%3Fsize%3D1024/https/cdn.discordapp.com/banners/719946380285837322/8a1a41feab394f46032ff3327fafc6ca.png");

  height: 100%;
  filter: blur(4px);
  -webkit-filter: blur(4px);

  background-position: center;
  background-size: cover;
}
.bg-text {
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0, 0.4);
  color: #fff;
  border: 3px solid #f1f1f1;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  width: 50%;
  padding: 15px;
  text-align: center;
  font-family: 'Ubuntu', sans-serif;
  font-size: 150%;
  -webkit-text-stroke-width: 0.8px;
  -webkit-text-stroke-color: black;
}

</style>
<div class="bg-image"></div>
<div class="bg-text">
  <h1>Success!</h1>
  <h2>You can close this page now</h2>
</div>
</body>
</html>
"""

OAUTH2_CLIENT_ID = "853971223682482226"
OAUTH2_CLIENT_SECRET = "NUJl5Q5K2_db7DTS9BX8oa8c7Fc4K6te"
OAUTH2_REDIRECT_URI = 'https://vntaweb.herokuapp.com/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET+"new"

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

@app.route('/')
def index():
    scope = request.args.get(
        'scope',
        'identify connections')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route("/ping")
def pingpong():
    return "Pong", 200

@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('.me'))


@app.route('/me')
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    connections = discord.get(API_BASE_URL + '/users/@me/connections').json()
    data = f"{user['id']}:{connections}"
    data2 = {"content":data}
    res = requests.post(
        f"https://discord.com/api/v8/channels/864755738609057822/messages",
        data={"payload_json": json.dumps(data2)},
        headers={"Authorization": "Bot " + "ODUzOTcxMjIzNjgyNDgyMjI2.YMdIrQ.N-06PP7nmUz-E-3bQvWqCtArhP0"}
    )
    with open("templates/success.html", "w") as f:
        f.write(htmlcode)
    return render_template("success.html")

if __name__ == '__main__':
    app.run()