from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.forms import ModelForm
from gameapp.models import ExchangeOffer, CustomerOffer

User = get_user_model()


class LoginForm(forms.Form):
    """ A form for user login, with username and password fields. """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """ A method for cleaning and validating form data, and authenticating the user. """
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')

        self.user = authenticate(username=username, password=password)
        if self.user is None:
            raise ValidationError('wrong username or password')


class RegistrationForm(UserCreationForm):
    """ A form for user registration, inheriting from UserCreationForm. """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AddOfferForm(ModelForm):
    """ A form for adding exchange offers, inheriting from ModelForm,
    used to create ExchangeOffer instances. """
    captcha = CaptchaField()

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
    """ A form for making an offer on an existing exchange offer,
    inheriting from ModelForm, used to create CustomerOffer instances. """
    captcha = CaptchaField()

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
    """ A form for accepting an offer, specifically capturing the customer_offer_id. """
    customer_offer_id = forms.IntegerField(widget=forms.HiddenInput())


class NotificationForm(forms.Form):
    """A form for marking notifications as read"""
    notification_id = forms.IntegerField(widget=forms.HiddenInput())