from flask import session, Blueprint, redirect, request
from flask.ext.login import login_user, logout_user, current_user
from werkzeug.exceptions import BadRequest
from apikit import jsonify

from nomenklatura import authz
from nomenklatura.providers import PROVIDERS, Stub
from nomenklatura.core import db, url_for
from nomenklatura.model import User


blueprint = Blueprint('sessions', __name__)


@blueprint.route('/sessions')
def status():
    oauth_providers = {}
    for name, provider in PROVIDERS.items():
        if not isinstance(provider, Stub):
            oauth_providers[name] = url_for('.login', provider=name)

    permissions = {}
    for perm in ['read', 'edit', 'manage']:
        permissions[perm] = authz.datasets(perm)

    return jsonify({
        'logged_in': authz.logged_in(),
        'api_key': current_user.api_key if authz.logged_in() else None,
        'user': current_user if authz.logged_in() else None,
        'permissions': permissions,
        'logins': oauth_providers,
        'logout': url_for('.logout')
    })


@blueprint.route('/sessions/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next_url', url_for('index')))


@blueprint.route('/sessions/login/<provider>')
def login(provider):
    if provider not in PROVIDERS:
        raise BadRequest('Unknown provider: %s' % provider)
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    session.clear()
    callback = url_for('.%s_authorized' % provider)
    session['next_url'] = request.args.get('next_url', url_for('index'))
    return PROVIDERS[provider].authorize(callback=callback)


handler = PROVIDERS.get('twitter')


@blueprint.route('/sessions/callback/twitter')
@handler.authorized_handler
def twitter_authorized(resp):
    next_url = session.get('next_url', url_for('index'))
    if resp is None or 'oauth_token' not in resp:
        return redirect(next_url)
    session['twitter_token'] = (resp['oauth_token'],
                                resp['oauth_token_secret'])
    provider = PROVIDERS.get('twitter')
    res = provider.get('users/show.json?user_id=%s' % resp.get('user_id'))
    data = {
        'display_name': res.data.get('name'),
        'twitter_id': res.data.get('id')
    }
    user = User.load(data)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(next_url)


handler = PROVIDERS.get('facebook')


@blueprint.route('/sessions/callback/facebook')
@handler.authorized_handler
def facebook_authorized(resp):
    next_url = session.get('next_url', url_for('index'))
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['facebook_token'] = (resp.get('access_token'), '')
    profile = PROVIDERS.get('facebook').get('/me').data
    data = {
        'display_name': profile.get('name'),
        'email': profile.get('email'),
        'facebook_id': profile.get('id')
    }
    user = User.load(data)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(next_url)


handler = PROVIDERS.get('github')


@blueprint.route('/sessions/callback/github')
@handler.authorized_handler
def github_authorized(resp):
    next_url = session.get('next_url', url_for('index'))
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['github_token'] = (resp['access_token'], '')
    res = PROVIDERS.get('github').get('https://api.github.com/user')
    data = {
        'display_name': res.data.get('name'),
        'email': res.data.get('email'),
        'login': res.data.get('login'),
        'github_id': res.data.get('id')
    }
    user = User.load(data)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(next_url)
