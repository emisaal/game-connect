import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from gameapp.models import Game, ExchangeOffer

User = get_user_model()


@pytest.fixture
def user(client):
    """Create a test user and log them in."""
    user = User.objects.create_user(username='testuser', password='validpassword123!@#')
    client.login(username='testuser', password='validpassword123!@#')
    return user


@pytest.fixture
def exchange_offer():
    """ Create a sample exchange offer """
    game = Game.objects.create(name="Game 1", description="Description for Game 1")
    offer = ExchangeOffer.objects.create(owner=User.objects.create(username='user1'), offer_type='S', game=game,
                                         price=10.0, description='Offer 1', status=True)
    return offer
