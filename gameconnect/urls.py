from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from captcha import urls as captcha_urls
from gameapp.views import (CustomLoginView, RegisterView, UserPageView, MainView, GamesListView,
                           ArticlesListView, ArticleDetailsView, MarketListView, AddOfferView,
                           MakeOfferView, OfferDetailsView, SubscribeView, ChangePasswordView, GameCreateView,
                           ArticleCreateView, NotificationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='main'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('user/<int:user_id>/', UserPageView.as_view(), name='user_page'),
    path('user/<int:user_id>/notifications/', NotificationView.as_view(), name='notifications'),
    path('user/<int:user_id>/password/', ChangePasswordView.as_view(), name='password_change'),
    path('games/', GamesListView.as_view(), name='games'),
    path('articles/', ArticlesListView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleDetailsView.as_view(), name='article_detail'),
    path('market/', MarketListView.as_view(), name='market'),
    path('market/add_offer/', AddOfferView.as_view(), name='add_offer'),
    path('market/make_offer/<int:offer_id>/', MakeOfferView.as_view(), name='make_offer'),
    path('market/offer_details/<int:offer_id>/', OfferDetailsView.as_view(), name='offer_details'),
    path('captcha/', include(captcha_urls)),
    path('add/game/', GameCreateView.as_view(), name='add_game'),
    path('add/article/', ArticleCreateView.as_view(), name='add_article'),
]
