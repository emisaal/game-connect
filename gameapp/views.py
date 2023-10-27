from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

from gameapp.forms import LoginForm, RegistrationForm, AddOfferForm, MakeOfferForm, AcceptForm
from gameapp.models import Game, Article, ExchangeOffer, CustomerOffer
from gameconnect import local_settings

# Mailchimp Settings
api_key = local_settings.MAILCHIMP_API_KEY
server = local_settings.MAILCHIMP_DATA_CENTER
list_id = local_settings.MAILCHIMP_EMAIL_LIST_ID


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
    login_url = reverse_lazy('login')

    def get(self, request, user_id):
        active_offers = ExchangeOffer.objects.filter(owner=user_id, status=True)
        inactive_offers = ExchangeOffer.objects.filter(owner=user_id, status=False)
        return render(request, 'user_page.html', {"active_offers": active_offers,
                                                  "inactive_offers": inactive_offers})


class AddOfferView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    template_name = "add_offer.html"
    form_class = AddOfferForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def form_valid(self, form):
        user_id = self.request.user.id

        new_offer = form.save(commit=False)
        new_offer.owner_id = user_id
        new_offer.save()

        return redirect('market')


class MakeOfferView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    template_name = "make_offer.html"
    form_class = MakeOfferForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer_id = self.kwargs.get('offer_id')
        context['offer_id'] = offer_id
        context['offer'] = ExchangeOffer.objects.get(id=offer_id)
        return context

    def form_valid(self, form):
        offer_id = self.kwargs.get('offer_id')
        customer = self.request.user.id

        new_offer = form.save(commit=False)
        new_offer.exchange_offer_id = offer_id
        new_offer.customer_id = customer
        new_offer.save()

        return redirect('market')


class OfferDetailsView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, offer_id):
        offer = ExchangeOffer.objects.get(id=offer_id)
        customers = CustomerOffer.objects.filter(exchange_offer_id=offer_id)
        return render(request, 'offer_details.html', {"offer": offer, "customers": customers})

    def post(self, request, offer_id):
        form = AcceptForm(request.POST)
        if form.is_valid():
            offer = ExchangeOffer.objects.get(id=offer_id)
            customer_offer_id = form.cleaned_data.get('customer_offer_id')
            customers = CustomerOffer.objects.filter(exchange_offer_id=offer_id)

            if offer.status:
                for customer in customers:
                    if customer.id == customer_offer_id:
                        customer.status = "A"
                    else:
                        customer.status = "R"
                    customer.save()

                offer.status = False
                offer.save()
            return redirect('offer_details', offer_id=offer_id)

class SubscribeView(View):
    template_name = 'subscribe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        self.subscribe(email)
        messages.success(request, "Email received. Thank You!")
        return render(request, self.template_name)

    def subscribe(self, email):
        """
         Contains code handling the communication to the mailchimp api
         to create a contact/member in an audience/list.
        """

        mailchimp = Client()
        mailchimp.set_config({
            "api_key": api_key,
            "server": server,
        })

        member_info = {
            "email_address": email,
            "status": "subscribed",
        }

        try:
            mailchimp.lists.add_list_member(list_id, member_info)
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))
