from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.forms import ModelForm

from gameapp.models import ExchangeOffer, CustomerOffer

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')

        self.user = authenticate(username=username, password=password)
        if self.user is None:
            raise ValidationError('wrong username or password')


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AddOfferForm(ModelForm):

    class Meta:
        model = ExchangeOffer
        fields = ['offer_type', 'game', 'price', 'description']
        labels = {
            'offer_type': 'Offer Type',
            'game': 'Game',
            'description': 'Description',
        }
    price = forms.DecimalField(
        label='Price (if applicable)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '0.00'})
    )


class MakeOfferForm(ModelForm):
    class Meta:
        model = CustomerOffer
        fields = ['game_name', 'price', 'description']
        labels = {
                'game_name': 'Game',
                'description': 'Description',
        }

    price = forms.DecimalField(
        label='Price (if applicable)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '0.00'})
    )


class AcceptForm(forms.Form):
    customer_offer_id = forms.IntegerField(widget=forms.HiddenInput())