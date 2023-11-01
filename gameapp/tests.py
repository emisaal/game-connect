import pytest
from captcha.models import CaptchaStore
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from pytest_django.asserts import assertRedirects
from gameapp.models import Game, Article, ExchangeOffer, CustomerOffer
from conftest import user, exchange_offer

User = get_user_model()


@pytest.mark.django_db
def test_login_view_valid_login(client):
    """CustomLoginView: Test a valid login attempt, expecting a successful redirect (HTTP 302)."""
    user_data = {'username': 'testuser', 'password': 'validpassword123!@#'}
    User.objects.create_user(**user_data)
    response = client.post(reverse('login'), data=user_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_view_invalid_login(client):
    """CustomLoginView: Test an invalid login attempt, expecting a form submission failure (HTTP 200)."""
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

    game = Game.objects.create(name="Test Game", description="text")
    article = Article.objects.create(slug="test-article", game=game, title="Test Article", content="text")
    offer = ExchangeOffer.objects.create(owner=User.objects.create(username="testuser"),
                                         offer_type="S", game=game, price=9.99, description="text")

    response = client.get(reverse('main'))
    assert response.status_code == 200
    assert game.name.encode() in response.content
    assert article.title.encode() in response.content
    assert offer.description.encode() in response.content


@pytest.mark.django_db
def test_games_list_view(client):
    """Test that the GamesListView displays a list of games correctly."""

    game1 = Game.objects.create(name="Game 1", description="text")
    game2 = Game.objects.create(name="Game 2", description="text")

    response = client.get(reverse('games'))
    assert response.status_code == 200
    assert game1.name.encode() in response.content
    assert game2.name.encode() in response.content


@pytest.mark.django_db
def test_articles_list_view(client):
    """Test that the ArticlesListView displays a list of articles correctly."""

    Game.objects.create(id=1, name="Game 1", description="text")
    article1 = Article.objects.create(slug="article-1", game_id="1", title="Article 1", content="text")
    article2 = Article.objects.create(slug="article-2", game_id="1", title="Article 2", content="text")

    response = client.get(reverse('articles'))
    assert response.status_code == 200
    assert article1.title.encode() in response.content
    assert article2.title.encode() in response.content


@pytest.mark.django_db
def test_article_details_view(client, user):
    """Test the ArticleDetailsView with a logged-in user."""

    game = Game.objects.create(name="Game 1", description="text")
    article = Article.objects.create(slug="article-1", game=game, title="Article 1", content="text")

    response = client.get(reverse('article_detail', args=['article-1']))
    assert response.status_code == 200
    assert article.title.encode() in response.content


@pytest.mark.django_db
def test_article_details_view_requires_login(client):
    """Test that the ArticleDetailsView redirects to the login page when not logged in."""

    Game.objects.create(id=1, name="Game 1", description="text")
    Article.objects.create(slug="article-1", game_id="1", title="Article 1", content="text")

    response = client.get(reverse('article_detail', args=['article-1']))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_market_list_view(client, user):
    """Test that the MarketListView displays a list of active exchange offers correctly."""

    game1 = Game.objects.create(name="Game 1", description="text")
    offer1 = ExchangeOffer.objects.create(owner=user, offer_type="S", game=game1, price=10.0, description="Offer 1",
                                          status=True)
    offer2 = ExchangeOffer.objects.create(owner=user, offer_type="E", game=game1, description="Offer 2", status=True)
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

    game1 = Game.objects.create(name="Game 1", description="text")
    offer1 = ExchangeOffer.objects.create(owner=user, offer_type="S", game=game1, price=10.0, description="Offer 1",
                                          status=True)
    offer2 = ExchangeOffer.objects.create(owner=user, offer_type="E", game=game1, description="Offer 2", status=False)
    offer3 = ExchangeOffer.objects.create(owner=User.objects.create(username='user2'), offer_type="B", game=game1,
                                          price=5.0, description="Offer 3", status=True)

    response = client.get(reverse('user_page', args=[user.id]))
    assert response.status_code == 200
    assert offer1.description.encode() in response.content
    assert offer2.description.encode() in response.content
    assert offer3.description.encode() not in response.content


@pytest.mark.django_db
def test_change_password_view_post_valid_form(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    data = {
        'old_password': 'testpassword',
        'new_password1': 'newpassword123!',
        'new_password2': 'newpassword123!',
    }
    client.force_login(user)
    response = client.post(reverse('password_change', args=[user.id]), data=data, follow=True)
    assert response.status_code == 200
    assertRedirects(response, reverse('user_page', args=[user.id]))


@pytest.mark.django_db
def test_change_password_view_post_invalid_form(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    data = {
        'old_password': 'wrongpassword',
        'new_password1': 'new123!',
        'new_password2': 'newpassword123!',
    }
    client.force_login(user)
    response = client.post(reverse('password_change', args=[user.id]), data=data)
    assert response.status_code == 200
    assert 'The two password fields didn' in str(response.content)


@pytest.mark.django_db
def test_add_offer_view_get(client, user):
    """Test the GET request to the AddOfferView."""
    response = client.get(reverse('add_offer'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_offer_view_post(client, user):
    """Test the POST request to the AddOfferView with valid form data."""
    data = {
        'offer_type': 'S',
        'game': Game.objects.create(name="Game 1", description="text").pk,
        'price': 10.0,
        'description': 'Offer Description',
    }
    captcha = CaptchaStore.objects.create(challenge="test-challenge", response="test-response")
    data['captcha_0'] = captcha.hashkey
    data['captcha_1'] = "test-response"

    response = client.post(reverse('add_offer'), data=data)
    assert response.status_code == 302
    assert ExchangeOffer.objects.filter(description='Offer Description').exists()


@pytest.mark.django_db
def test_make_offer_view_get(client, user, exchange_offer):
    """Test the GET request to the MakeOfferView."""
    offer_id = exchange_offer.id
    response = client.get(reverse('make_offer', args=[offer_id]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_make_offer_view_post(client, user, exchange_offer):
    """ Test the POST request to the MakeOfferView with valid form data. """
    form_data = {
        'game_name': exchange_offer.game.id,
        'price': 10.0,
        'description': 'Test Description',
    }
    captcha = CaptchaStore.objects.create(challenge="test-challenge", response="test-response")
    form_data['captcha_0'] = captcha.hashkey
    form_data['captcha_1'] = "test-response"

    url = reverse('make_offer', kwargs={'offer_id': exchange_offer.id})
    response = client.post(url, data=form_data)

    assert response.status_code == 302
    assert CustomerOffer.objects.filter(game_name=exchange_offer.game.id, price=10.0, description='Test Description').exists()
    assert response.url == reverse('market')


@pytest.mark.django_db
def test_subscribe_view_get(client):
    """Test the GET request to the SubscribeView."""
    response = client.get(reverse('subscribe'))

    assert response.status_code == 200
