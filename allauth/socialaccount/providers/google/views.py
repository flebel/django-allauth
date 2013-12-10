import logging
import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login, render_authentication_error
from allauth.socialaccount.models import SocialLogin, SocialAccount, SocialToken
from allauth.socialaccount.adapter import get_adapter
from allauth.account.utils import user_email

from .forms import GoogleConnectForm
from .provider import GoogleProvider


logger = logging.getLogger(__name__)

PROFILE_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'


def google_complete_login(app, token):
    resp = requests.get(PROFILE_URL,
                        params={ 'access_token': token.token })
    resp.raise_for_status()
    extra_data = resp.json()
    # extra_data is something of the form:
    #
    # {u'family_name': u'Penners', u'name': u'Raymond Penners',
    #  u'picture': u'https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg',
    #  u'locale': u'nl', u'gender': u'male',
    #  u'email': u'raymond.penners@gmail.com',
    #  u'link': u'https://plus.google.com/108204268033311374519',
    #  u'given_name': u'Raymond', u'id': u'108204268033311374519',
    #  u'verified_email': True}
    #
    # TODO: We could use verified_email to bypass allauth email verification
    uid = str(extra_data['id'])
    user = get_adapter() \
        .populate_new_user(email=extra_data.get('email'),
                           last_name=extra_data.get('family_name'),
                           first_name=extra_data.get('given_name'))
    email_addresses = []
    email = user_email(user)
    if email and extra_data.get('verified_email'):
        email_addresses.append(EmailAddress(email=email,
                                            verified=True,
                                            primary=True))
    account = SocialAccount(extra_data=extra_data,
                            uid=uid,
                            provider=GoogleProvider.id,
                            user=user)
    return SocialLogin(account,
                       email_addresses=email_addresses)


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    profile_url = PROFILE_URL

    def complete_login(self, request, app, token, **kwargs):
        return google_complete_login(app, token)

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)


def login_by_token(request):
    ret = None
    if (request.method == 'POST'):
        form = GoogleConnectForm(request.POST)
        if form.is_valid():
            try:
                app = providers.registry.by_id(GoogleProvider.id).get_app(request)
                access_token = form.cleaned_data['access_token']
                token = SocialToken(app=app, token=access_token)
                login = google_complete_login(app, token)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except requests.RequestException:
                logger.exception('Error accessing Google user profile')
    if not ret:
        ret = render_authentication_error(request)
    return ret
