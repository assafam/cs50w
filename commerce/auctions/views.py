from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Auction, Bid, Comment
from . import forms


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(active=True),
        "watched_items": request.user.auction_watchlist.count() if request.user.is_authenticated else None,
    })

def listing(request, listing_id):
    try:
        auction = Auction.objects.get(id=listing_id)
    except Auction.DoesNotExist:
        raise Http404("Listing not found")
    context = {
        "listing": auction,
    }
    if request.user.is_authenticated:
        context["watched_items"] = request.user.auction_watchlist.count()
        context["is_watched"] = auction.watchers.filter(pk=request.user.id).exists()
    return render(request, "auctions/listing.html", context)

def categories(request):
    return render(request, "auctions/categories.html")

def watchlist(request):
    return render(request, "auctions/watchlist.html")

@login_required
def watch(request, listing_id):
    try:
        auction = Auction.objects.get(pk=listing_id)
    except Auction.DoesNotExist:
        return HttpResponseBadRequest("Bad request: auction does not exist")
    if not auction.watchers.filter(pk=request.user.id):
        auction.watchers.add(request.user)
    else:
        return HttpResponseBadRequest("Bad request: user already in watchlist")
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def unwatch(request, listing_id):
    try:
        auction = Auction.objects.get(pk=listing_id)
    except Auction.DoesNotExist:
        return HttpResponseBadRequest("Bad request: auction does not exist")
    if auction.watchers.filter(pk=request.user.id):
        auction.watchers.remove(request.user)
    else:
        return HttpResponseBadRequest("Bad request: user is not in watchlist")
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required()
def create(request):
    if request.method == "POST":
        auction = Auction(created_by=request.user, active=True)
        form = forms.NewAuctionForm(request.POST, instance=auction)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = forms.NewAuctionForm()

    return render(request, "auctions/create.html", {
        "form": form,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
