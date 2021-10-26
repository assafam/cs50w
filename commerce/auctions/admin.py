from django.contrib import admin
from .models import Category, Auction, Bid, Comment, User

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "starting_bid", "category", "created_by", "creation_time")
    filter_horizontal = ("watchers", )


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
