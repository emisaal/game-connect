from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, UpdateView

from gameapp.forms import LoginForm, RegistrationForm, AddOfferForm, MakeOfferForm, SubscribeForm
from gameapp.models import Game, Article, ExchangeOffer, Subscribe


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'register.html', {'form': form})


class MainView(View):
    def get(self, request):
        game = Game.objects.latest('added')
        article = Article.objects.latest('added')
        offer = ExchangeOffer.objects.latest('added')
        return render(request, 'main.html', {"article": article, "game": game, "offer": offer})


class GamesListView(ListView):
    template_name = "games.html"
    model = Game


class ArticlesListView(ListView):
    template_name = "articles.html"
    model = Article


class ArticleDetailsView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, slug):
        article = Article.objects.get(slug=slug)
        user = request.user
        return render(request, 'article.html', {"article": article, "user": user})


class MarketListView(ListView):
    template_name = "market.html"
    model = ExchangeOffer
    ordering = ['added']

    def get_queryset(self):
        offers = super().get_queryset()
        active_offers = offers.filter(status=True)

        return active_offers


class UserPageView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        active_offers = ExchangeOffer.objects.filter(owner=user_id, status=True)
        return render(request, 'user_page.html', {"active_offers": active_offers})


class AddOfferView(LoginRequiredMixin, View):
    template = "add_offer.html"
    form = AddOfferForm

    def get(self, request, *args, **kwargs):
        form = self.form
        return render(request, self.template,  {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('market')


class MakeOfferView(LoginRequiredMixin, View):
    template = "make_offer.html"
    form = MakeOfferForm

    def get(self, request, *args, **kwargs):
        form = self.form
        return render(request, self.template,  {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('market')


class OfferDetailsView(LoginRequiredMixin, View):
    def get(self, request, offer_id):
        offer = ExchangeOffer.objects.get(pk=offer_id)
        customers = ExchangeOffer.objects.get(pk=offer_id)
        return render(request, 'offer_details.html', {"offer": offer,
                                                      "customers": customers})


class SubscribeView(FormView):
    template_name = 'subscribe.html'
    form_class = SubscribeForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        status = form.cleaned_data['status']
        if status:
            form.save()
            return super().form_valid(form)

# def subscribe_to_mailchimp_list(email, list_id):
#     client = Client()
#     client.set_config({
#         "api_key": settings.MAILCHIMP_API_KEY,
#         "server": settings.MAILCHIMP_SERVER_PREFIX,
#     })
#     member = {
#         "email_address": email,
#         "status": "subscribed"
#     }
#     try:
#         response = client.lists.add_list_member(list_id, member)
#         return response
#     except Exception as e:
#         return None


