from django import forms


class GoogleConnectForm(forms.Form):
    access_token = forms.CharField(required=True)
