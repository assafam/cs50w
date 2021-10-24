from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

class Auction(models.Model):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=1024)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="auctions")
    creation_time = models.DateTimeField
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions_created")
    watchers = models.ManyToManyField(User, on_delete=models.CASCADE, related_name="auction_watchlist")

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    text = models.CharField(max_length=1024)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
