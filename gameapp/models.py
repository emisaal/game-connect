from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

OFFER_TYPE_CHOICES = [
    ("S", "Sell"),
    ("E", "Exchange"),
    ("B", "Buy"),
]
STATUS_CHOICES = [
    ("P", "Pending"),
    ("A", "Accepted"),
    ("R", "Rejected"),
]


class Game(models.Model):
    """
    Model for storing information about a video game.

    Fields:
    - name (CharField): The name of the game (limited to 100 characters).
    - description (TextField): A detailed description of the game.
    - added (DateTimeField): Timestamp when the game was added.

    Provides a human-readable string representation of the game.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """ Provides a human-readable string representation of the game. """
        return self.name


class Article(models.Model):
    """
    Model for storing articles related to a specific game.

    Fields:
    - slug (SlugField): A user-friendly URL for the article (auto-generated based on the title).
    - game (ForeignKey): A reference to the associated game.
    - title (CharField): The title of the article (limited to 100 characters).
    - content (TextField): Content of the article.
    - added (DateTimeField): Timestamp when the article was created.

    Overrides the save method to generate a unique slug based on the title.
    """
    slug = models.SlugField(unique=True, max_length=100, primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Override the save method to generate a slug from the title and ensure uniqueness. """
        if not self.slug:
            self.slug = slugify(self.title)
            if Article.objects.filter(slug=self.slug).exists():
                suffix = 1
                while Article.objects.filter(slug=self.slug).exists():
                    self.slug = f"{slugify(self.title)}-{suffix}"
                    suffix += 1
        super().save(*args, **kwargs)


class ExchangeOffer(models.Model):
    """
    Model for game exchange offers.

    Fields:
    - owner (ForeignKey): Reference to the offer owner (User).
    - offer_type (CharField): Type of the offer (limited to choices).
    - game (ForeignKey): Reference to the game.
    - price (DecimalField): Price of the offer.
    - description (TextField): Description of the offer.
    - status (BooleanField): Offer status (defaulted to True).
    - added(DateTimeField): Timestamp when the offer was made.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    description = models.TextField()
    status = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)


class CustomerOffer(models.Model):
    """
    Model for customer offers in response to ExchangeOffer listings.

    Fields:
    - exchange_offer (ForeignKey): Reference to the original GameExchange offer.
    - customer (ForeignKey): Reference to the customer making the offer (User).
    - game_name (ForeignKey): Reference to the game.
    - price (DecimalField): Price offered by the customer.
    - description (TextField): Description of the customer's offer.
    - status (CharField): Offer status (defaulted to Pending).
    - added (DateTimeField): Timestamp when the offer was made.
    """
    exchange_offer = models.ForeignKey(ExchangeOffer, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    game_name = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, default="P", choices=STATUS_CHOICES)
    added = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    """
    Model for customer made offers and owner's accepted offers notifications.

    Fields:
    - user (ForeignKey): notification owner
    - description (TextField): notification content
    - status(BooleanField): notification status, shows whether user has seen it (defaulted to False)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.BooleanField(default=False)
