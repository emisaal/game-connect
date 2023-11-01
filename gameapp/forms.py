from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, Form

from gameapp.models import ExchangeOffer, CustomerOffer, Game, Article

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Enter your email address.'
    )


class AddOfferForm(ModelForm):
    """ A form for adding exchange offers. """
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
    """ A form for making an offer on an existing exchange offer. """
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


class AcceptForm(Form):
    """ A form for accepting an offer. """
    customer_offer_id = forms.IntegerField(widget=forms.HiddenInput())


class NotificationForm(Form):
    """ A form for marking notifications as read. """
    notification_id = forms.IntegerField(widget=forms.HiddenInput())


class NewGameForm(ModelForm):
    """ A form for adding new game to database. """
    class Meta:
        model = Game
        fields = ['name', 'description']


class NewArticleForm(ModelForm):
    """ A form for adding new article to database. """
    class Meta:
        model = Article
        fields = ['game', 'title', 'content']
