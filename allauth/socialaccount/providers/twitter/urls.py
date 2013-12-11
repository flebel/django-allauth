from django.conf.urls import patterns, url

from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from . import views
from .provider import TwitterProvider

urlpatterns = default_urlpatterns(TwitterProvider)

# urlpatterns += patterns('',
#     url('^twitter/login/token/$', views.login_by_token,
#         name="twitter_login_by_token"),
#     )
