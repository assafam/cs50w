from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("<int:auction_id>", views.listing, name="listing"),
    path("<int:auction_id>/watch", views.watch, name="watch"),
    path("<int:auction_id>/unwatch", views.unwatch, name="unwatch"),
    path("<int:auction_id>/close", views.close, name="close"),
    path("<int:auction_id>/comment", views.comment, name="comment"),
    path("<int:category_id>/view", views.view_category, name="view_category"),
]
