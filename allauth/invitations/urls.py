from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^(?P<invitation_key>\w+)/$', views.accept, name='invitations_accept'),
)
