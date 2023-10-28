from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
import pytest

from gameapp.models import Game, Article, ExchangeOffer

User = get_user_model()


@pytest.fixture
def user(client):
    """Create a test user and log them in."""
    user = User.objects.create_user(username='testuser', password='validpassword123!@#')
    client.login(username='testuser', password='validpassword123!@#')
    return user


@pytest.mark.django_db
def test_login_view_valid_login(client):
    """LoginView(FormView): Test a valid login attempt, expecting a successful redirect (HTTP 302)."""
    user_data = {'username': 'testuser', 'password': 'validpassword123!@#'}
    User.objects.create_user(**user_data)
    response = client.post(reverse('login'), data=user_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_view_invalid_login(client):
    """LoginView(FormView): Test an invalid login attempt, expecting a form submission failure (HTTP 200)."""
    user_data = {'username': 'testuser', 'password': 'invalidpassword'}
    response = client.post(reverse('login'), data=user_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_view(client):
    """Test the LogoutView, ensuring the user is logged out and redirected to the login page."""
    user_data = {'username': 'testuser', 'password': 'validpassword123!@#'}
    User.objects.create_user(**user_data)
    client.login(username=user_data['username'], password=user_data['password'])

    response = client.get(reverse('logout'))

    assert response.status_code == 302
    assert response.url == reverse('login')

    session = client.session
    assert session.get('_auth_user_id') is None


@pytest.mark.django_db
def test_register_view_post_valid(client):
    """Test successful user registration via the RegisterView with valid data."""
    data = {
        'username': 'newuser',
        'email': 'newuser@newuser.com',
        'password1': 'newpassword123!@#',
        'password2': 'newpassword123!@#',
    }
    response = client.post(reverse('register'), data=data, follow=True)
    assert response.status_code == 200
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_register_view_post_invalid(client):
    """Test user registration via the RegisterView with invalid data."""
    data = {
        'username': 'newuser',
        'email': 'newuser@newuser.com',
        'password1': 'password123!@#',
        'password2': 'diffpass123!@#',
    }
    response = client.post(reverse('register'), data=data, follow=True)
    assert response.status_code == 200
    assert not User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_main_view(client):
    """Test that the MainView displays the main page with the latest Game, Article, and ExchangeOffer."""

    game = Game.objects.create(name="Sample Game", description="Description for Sample Game")
    article = Article.objects.create(slug="sample-article", game=game, title="Sample Article",
                                     content="Content for Sample Article")
    offer = ExchangeOffer.objects.create(owner=User.objects.create(username="sampleuser"),
                                         offer_type="S", game=game, price=9.99, description="Sample Offer Description")

    response = client.get(reverse('main'))

    assert response.status_code == 200
    assert game.name.encode() in response.content
    assert article.title.encode() in response.content
    assert offer.description.encode() in response.content


@pytest.mark.django_db
def test_games_list_view(client):
    """Test that the GamesListView displays a list of games correctly."""

    game1 = Game.objects.create(name="Game 1", description="Description for Game 1")
    game2 = Game.objects.create(name="Game 2", description="Description for Game 2")

    response = client.get(reverse('games'))

    assert response.status_code == 200
    assert game1.name.encode() in response.content
    assert game2.name.encode() in response.content


@pytest.mark.django_db
def test_articles_list_view(client):
    """Test that the ArticlesListView displays a list of articles correctly."""

    Game.objects.create(id=1, name="Game 1", description="Description for Game 1")
    article1 = Article.objects.create(slug="article-1", game_id="1", title="Article 1", content="Content for Article 1")
    article2 = Article.objects.create(slug="article-2", game_id="1", title="Article 2", content="Content for Article 2")

    response = client.get(reverse('articles'))
    assert response.status_code == 200
    assert article1.title.encode() in response.content
    assert article2.title.encode() in response.content


@pytest.mark.django_db
def test_article_details_view(client, user):
    """Test the ArticleDetailsView with a logged-in user."""

    game = Game.objects.create(name="Game 1", description="Description for Game 1")
    article = Article.objects.create(slug="article-1", game=game, title="Article 1", content="Content for Article 1")

    response = client.get(reverse('article_detail', args=['article-1']))

    assert response.status_code == 200
    assert article.title.encode() in response.content


@pytest.mark.django_db
def test_article_details_view_requires_login(client):
    """Test that the ArticleDetailsView redirects to the login page when not logged in."""

    Game.objects.create(id=1, name="Game 1", description="Description for Game 1")
    Article.objects.create(slug="article-1", game_id="1", title="Article 1", content="Content for Article 1")

    response = client.get(reverse('article_detail', args=['article-1']))

    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_market_list_view(client, user):
    """Test that the MarketListView displays a list of active exchange offers correctly."""

    game1 = Game.objects.create(name="Game 1", description="Description for Game 1")

    offer1 = ExchangeOffer.objects.create(owner=user, offer_type="S", game=game1, price=10.0,
                                          description="Offer 1", status=True)
    offer2 = ExchangeOffer.objects.create(owner=user, offer_type="E", game=game1,
                                          description="Offer 2", status=True)

    inactive_offer = ExchangeOffer.objects.create(owner=user, offer_type="S", game=game1, price=15.0,
                                                  description="Offer 4", status=False)

    response = client.get(reverse('market'))

    assert response.status_code == 200
    assert offer1.description.encode() in response.content
    assert offer2.description.encode() in response.content
    assert inactive_offer.description.encode() not in response.content


@pytest.mark.django_db
def test_user_page_view(client, user):
    """Test the UserPageView with a logged-in user."""

    game1 = Game.objects.create(name="Game 1", description="Description for Game 1")
    offer1 = ExchangeOffer.objects.create(owner=user, offer_type="S", game=game1, price=10.0,
                                          description="Offer 1", status=True)
    offer2 = ExchangeOffer.objects.create(owner=user, offer_type="E", game=game1,
                                          description="Offer 2", status=False)
    offer3 = ExchangeOffer.objects.create(owner=User.objects.create(username='user2'), offer_type="B", game=game1,
                                          price=5.0, description="Offer 3", status=True)

    response = client.get(reverse('user_page', args=[user.id]))

    assert response.status_code == 200
    assert offer1.description.encode() in response.content
    assert offer2.description.encode() in response.content
    assert offer3.description.encode() not in response.content