from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from .models import User, Category, Auction, Bid, Comment
from . import forms
from . import util

def index(request):
    auctions = Auction.objects.filter(active=True)
    context = {
        "auctions": util.annotate_with_current_price(auctions),
    }
    if request.user.is_authenticated:
        context["watched_items"] = request.user.auction_watchlist.count()
    return render(request, "auctions/index.html", context)

def listing(request, auction_id):
    try:
        auction_qs = Auction.objects.filter(pk=auction_id)
        auction = util.annotate_with_current_price(auction_qs).get()
    except Auction.DoesNotExist:
        raise Http404("Listing not found")

    context = {
        "auction": auction,
        "num_bids": auction.bids.count(),
        "comments": auction.comments.all(),
    }
    if request.user.is_authenticated:
        context["watched_items"] = request.user.auction_watchlist.count()
        context["is_watched"] = auction.watchers.filter(pk=request.user.id).exists()
        context["current_bid"] = auction.bids.exists() and util.get_winning_bid(auction).user == request.user

    if request.method == "POST" and request.user.is_authenticated:
        bid = Bid(auction=auction, user=request.user)
        form = forms.BidForm(request.POST, instance=bid)
        if form.is_valid():
            if not auction.active:
                form.add_error(None, ValidationError(_("Auction is not active."), code="inactive"))
            elif form.cleaned_data["bid"] <= auction.cur_price:
                form.add_error("bid", ValidationError(_("Bid must be greater than current price."), code="low_bid"))
            else:
                form.save()
                return HttpResponseRedirect(reverse("listing", args=[auction_id]))
    else:
        form = forms.BidForm()

    context["form"] = form
    return render(request, "auctions/listing.html", context)

def categories(request):
    return render(request, "auctions/categories.html")

def watchlist(request):
    return render(request, "auctions/watchlist.html")

@login_required
def watch(request, auction_id):
    if request.method == "POST":
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return HttpResponseBadRequest("Bad request: auction does not exist")
        if not auction.watchers.filter(pk=request.user.id):
            auction.watchers.add(request.user)
        else:
            return HttpResponseBadRequest("Bad request: user already in watchlist")
        return HttpResponseRedirect(reverse("listing", args=[auction_id]))

@login_required
def unwatch(request, auction_id):
    if request.method == "POST":
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return HttpResponseBadRequest("Bad request: auction does not exist")
        if auction.watchers.filter(pk=request.user.id):
            auction.watchers.remove(request.user)
        else:
            return HttpResponseBadRequest("Bad request: user is not in watchlist")
        return HttpResponseRedirect(reverse("listing", args=[auction_id]))

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
