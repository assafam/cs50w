from django.contrib import admin
from .models import Category, Auction, Bid, Comment, User

class AuctionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "active",
        "starting_bid",
        "category_view",
        "created_by",
        "creation_time")
    filter_horizontal = ("watchers", )
    list_display_links = ("id", "title")

    @admin.display(empty_value="None", description="Category", ordering="category")
    def category_view(self, obj):
        return obj.category


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
