from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('view_category', kwargs={"category_id": self.pk})

class Auction(models.Model):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=1024)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField()
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="auctions")
    creation_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    watchers = models.ManyToManyField(User, blank=True, related_name="auction_watchlist")

    def __str__(self):
        return f"{self.title} (category: {self.category}, created by: {self.created_by} at: {self.creation_time})"

    def get_absolute_url(self):
        return reverse('listing', kwargs={"auction_id": self.pk})

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.bid} for {self.auction} by {self.user}"

class Comment(models.Model):
    text = models.CharField(max_length=1024)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment for {self.auction} by {self.user}"
