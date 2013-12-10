from django import forms


class TwitterConnectForm(forms.Form):
    oauth_token = forms.CharField(required=True)
    oauth_token_secret = forms.CharField(required=True)
