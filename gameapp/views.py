from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, CreateView, TemplateView
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from gameapp.forms import AddOfferForm, MakeOfferForm, AcceptForm, NotificationForm, NewGameForm, NewArticleForm, \
    CustomUserCreationForm
from gameapp.models import Game, Article, ExchangeOffer, CustomerOffer, Notification
from gameconnect import local_settings

# Mailchimp Settings
api_key = local_settings.MAILCHIMP_API_KEY
server = local_settings.MAILCHIMP_DATA_CENTER
list_id = local_settings.MAILCHIMP_EMAIL_LIST_ID


class CustomLoginView(LoginView):
    """ A class-based view for handling user login. """
    template_name = "login.html"


class RegisterView(CreateView):
    """ A class-based view for user registration. """
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')


class MainView(View):
    """ A class-based view for the main page. """

    def get(self, request):
        game = Game.objects.latest('added')
        article = Article.objects.latest('added')
        offer = ExchangeOffer.objects.latest('added')
        return render(request, 'main.html', {"article": article, "game": game, "offer": offer})


class GamesListView(ListView):
    """ A class-based view for listing games. """
    template_name = "games.html"
    model = Game
    ordering = 'name'


class ArticlesListView(ListView):
    """ A class-based view for listing articles. """
    template_name = "articles.html"
    model = Article
    ordering = '-added'


class ArticleDetailsView(LoginRequiredMixin, View):
    """ A class-based view for displaying article details, with login requirement. """
    login_url = reverse_lazy('login')

    def get(self, request, slug):
        article = Article.objects.get(slug=slug)
        user = request.user
        return render(request, 'article.html', {"article": article, "user": user})


class MarketListView(ListView):
    """ A class-based view for listing all active exchange offers ordered by the added date,
    optionally filtered by game name. """
    template_name = "market.html"
    model = ExchangeOffer

    def get_context_data(self, **kwargs):
        """ Adds game list without duplicates to context. """
        context = super().get_context_data(**kwargs)
        context['games'] = ExchangeOffer.objects.filter(status=True).values_list('game__name', flat=True).distinct()

        return context

    def get_queryset(self):
        """ Retrieves the queryset of active exchange offers, optionally filtered by the selected game. """
        game_filter = self.request.GET.get('game')
        if game_filter:
            active_offers = ExchangeOffer.objects.filter(status=True, game__name=game_filter).order_by('-added')
        else:
            active_offers = ExchangeOffer.objects.filter(status=True).order_by('-added')
        return active_offers


class UserPageView(LoginRequiredMixin, View):
    """ A class-based view for displaying a user's page, with login requirement. """
    login_url = reverse_lazy('login')

    def get(self, request, user_id):
        if user_id != request.user.id:
            raise Http404

        notifications = Notification.objects.filter(user=user_id).order_by('-id')
        active_offers = ExchangeOffer.objects.filter(owner=user_id, status=True)
        inactive_offers = ExchangeOffer.objects.filter(owner=user_id, status=False)
        return render(request, 'user_page.html', {
            "active_offers": active_offers, "inactive_offers": inactive_offers, "notifications": notifications})

    def post(self, request, user_id):
        """ Handles POST requests to mark notifications as read by user. """
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification_id = form.cleaned_data['notification_id']
            notification = Notification.objects.get(id=notification_id)
            notification.status = True
            notification.save()

        return redirect('user_page', user_id=request.user.id)


class ChangePasswordView(View):
    """ A class-based view for allowing a user to change their password. """
    template_name = 'change_password.html'

    def get(self, request, user_id):
        if user_id != request.user.id:
            raise Http404

        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, user_id):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('user_page', user_id)
        return render(request, self.template_name, {'form': form})


class AddOfferView(LoginRequiredMixin, FormView):
    """  A class-based view for adding exchange offer, with login requirement. """
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
    """ A class-based view for making an offer on an existing exchange offer, with login requirement. """
    login_url = reverse_lazy('login')
    template_name = "make_offer.html"
    form_class = MakeOfferForm

    def get_form(self, form_class=None):
        """ Customizes the form by setting the initial game name. """
        form = super().get_form(form_class)
        offer_id = self.kwargs.get('offer_id')
        selected_game = ExchangeOffer.objects.get(id=offer_id)
        form.fields['game_name'].initial = selected_game.game
        return form

    def get_context_data(self, **kwargs):
        """ Adds offer-related context data to the view. """
        context = super().get_context_data(**kwargs)
        offer_id = self.kwargs.get('offer_id')
        context['offer_id'] = offer_id
        context['offer'] = ExchangeOffer.objects.get(id=offer_id)
        return context

    def form_valid(self, form):
        offer_id = self.kwargs.get('offer_id')
        customer = self.request.user.id

        # save new offer to CustomerOffer
        new_offer = form.save(commit=False)
        new_offer.exchange_offer_id = offer_id
        new_offer.customer_id = customer
        new_offer.save()

        # send email notification to offer owner
        owner = ExchangeOffer.objects.get(id=offer_id)
        text_content = (f"New offer was made to Your listing {owner.get_offer_type_display()} - {owner.game}, please "
                        f"go to Your User Page - My active offers - Details to review it.")
        self.send_notification_email(owner.owner.email, text_content)

        # create notification for offer's owner
        notification = f"New offer was made to Your listing {owner.get_offer_type_display()} - {owner.game}"
        Notification.objects.create(user=owner.owner, description=notification)
        return redirect('market')

    def send_notification_email(self, email, text_content):
        """ Send an email when offer is made by customer. """
        subject, from_email, to = "New offer made by customer", "emistrij@gmail.com", email
        html_content = f"<p>{text_content}</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class OfferDetailsView(LoginRequiredMixin, View):
    """ A class-based view for displaying the details of an exchange offer, with login requirement. """
    login_url = reverse_lazy('login')

    def get(self, request, offer_id):
        try:
            offer = ExchangeOffer.objects.get(id=offer_id)
        except ExchangeOffer.DoesNotExist:
            raise Http404

        if offer.owner != request.user:
            raise Http404
        # get all customer's offers
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
                        offer_details = offer.get_offer_type_display() + "-" + str(offer.game)
                        notification = (
                            f"User {offer.owner.username} has accepted your offer for {offer_details}. Please "
                            f"reach out ot them via email {offer.owner.email}")
                        Notification.objects.create(user=customer.customer, description=notification)
                        self.send_notification_email(customer.customer.email, notification)

                    else:
                        customer.status = "R"
                    customer.save()

                offer.status = False
                offer.save()
            return redirect('offer_details', offer_id=offer_id)

    def send_notification_email(self, email, text_content):
        """ Send an email when offer is accepted by owner. """
        subject, from_email, to = "You offer was accepted", "emistrij@gmail.com", email
        html_content = f"<p>{text_content}</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class SubscribeView(View):
    """ A class-based view for handling email subscriptions to a mailing list. """
    template_name = 'subscribe.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        self.subscribe(email)
        self.send_welcome_email(email)
        messages.success(request, "Email received. Thank You!")
        return render(request, self.template_name)

    def subscribe(self, email):
        """ A method for subscribing an email to a mailing list using the Mailchimp API. """

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

    def send_welcome_email(self, email):
        """ Send a welcome email to the new subscribed user. """
        subject, from_email, to = "Welcome to Our Mailing List", "emistrij@gmail.com", email
        text_content = "Thank you for subscribing to our mailing list. We are excited to have you on board!"
        html_content = "<p>Thank you for subscribing to our mailing list. We are excited to have you on board!</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class GameCreateView(PermissionRequiredMixin, CreateView):
    """ A class-based view for creating a new game, with permission requirements. """
    permission_required = 'gameapp.add_game'
    model = Game
    form_class = NewGameForm
    template_name = 'add_game.html'
    success_url = reverse_lazy('games')

    def form_valid(self, form):
        return super().form_valid(form)


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    """ A class-based view for creating a new article, with permission requirements. """
    permission_required = 'gameapp.add_article'
    model = Article
    form_class = NewArticleForm
    template_name = 'add_article.html'
    success_url = reverse_lazy('articles')

    def form_valid(self, form):
        return super().form_valid(form)


class NotificationView(LoginRequiredMixin, View):
    """ A class-based view for displaying all user notifications, with login requirement. """
    login_url = reverse_lazy('login')

    def get(self, request, user_id):
        if user_id != request.user.id:
            raise Http404

        notifications = Notification.objects.filter(user=user_id).order_by('-id')
        return render(request, 'notifications.html', {"notifications": notifications})

    def post(self, request, user_id):
        """ Handles POST requests to delete notifications. """
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification_id = form.cleaned_data['notification_id']
            notification = Notification.objects.get(id=notification_id)
            notification.delete()

        return redirect('notifications', user_id=request.user.id)

