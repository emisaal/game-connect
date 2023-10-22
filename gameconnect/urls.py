from django.contrib import admin
from django.urls import path

from gameapp.views import (LoginView, LogoutView, RegisterView, UserPageView, MainView, GamesListView,
                           ArticlesListView, ArticleDetailsView, MarketListView, AddOfferView,
                           MakeOfferView, OfferDetailsView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/<int:user_id>/', UserPageView.as_view(), name='user_page'),
    path('games/', GamesListView.as_view(), name='games'),
    path('articles/', ArticlesListView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleDetailsView.as_view(), name='article_detail'),
    path('market/', MarketListView.as_view(), name='market'),
    path('market/add_offer/', AddOfferView.as_view(), name='add_offer'),
    path('market/make_offer/<int:offer_id>/', MakeOfferView.as_view(), name='make_offer'),
    path('market/offer_details/<int:offer_id>/', OfferDetailsView.as_view(), name='offer_details'),
]
