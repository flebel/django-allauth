import json
import logging

import requests

from allauth.socialaccount.helpers import complete_social_login, render_authentication_error
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialLogin, SocialAccount, SocialToken
from allauth.socialaccount.adapter import get_adapter
from requests_oauthlib import OAuth1

from .forms import TwitterConnectForm
from .provider import TwitterProvider


logger = logging.getLogger(__name__)

VERIFY_CREDENTIALS_URL = 'https://api.twitter.com/1.1/account/verify_credentials.json'


def twitter_complete_login(extra_data):
    uid = extra_data['id']
    user = get_adapter() \
        .populate_new_user(username=extra_data.get('screen_name'),
                           name=extra_data.get('name'))
    account = SocialAccount(user=user,
                            uid=uid,
                            provider=TwitterProvider.id,
                            extra_data=extra_data)
    return SocialLogin(account)


class TwitterAPI(OAuth):
    """
    Verifying twitter credentials
    """
    def get_user_info(self):
        user = json.loads(self.query(VERIFY_CREDENTIALS_URL))
        return user


class TwitterOAuthAdapter(OAuthAdapter):
    provider_id = TwitterProvider.id
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    # Issue #42 -- this one authenticates over and over again...
    # authorize_url = 'https://api.twitter.com/oauth/authorize'
    authorize_url = 'https://api.twitter.com/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = TwitterAPI(request, app.client_id, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        return twitter_complete_login(extra_data)


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)


def login_by_token(request):
    ret = None
    if (request.method == 'POST'):
        form = TwitterConnectForm(request.POST)
        if form.is_valid():
            try:
                app = providers.registry.by_id(TwitterProvider.id).get_app(request)
                oauth_token = form.cleaned_data['oauth_token']
                oauth_token_secret = form.cleaned_data['oauth_token_secret']
                token = SocialToken(app=app, token=oauth_token, token_secret=oauth_token_secret)
                auth = OAuth1(app.client_id, app.secret, token.token, token.token_secret)
                resp = requests.get(VERIFY_CREDENTIALS_URL, auth=auth)
                resp.raise_for_status()
                extra_data = resp.json()
                login = twitter_complete_login(extra_data)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except requests.RequestException:
                logger.exception('Error accessing Twitter user profile')
    if not ret:
        ret = render_authentication_error(request)
    return ret
