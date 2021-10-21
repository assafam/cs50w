from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entry, name="wiki"),
    path("search", views.search, name="search"),
    path("random", views.random_entry, name="random"),
    path("new", views.new, name="new"),
    path("edit/<str:entry>", views.edit, name="edit"),
]
