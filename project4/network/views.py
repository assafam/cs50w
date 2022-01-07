from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post
from . import forms

def index(request):
    posts = Post.objects.all()
    page_obj = annotate_and_paginate(request, posts)

    context = {
        "title": "All Posts",
        "page_obj": page_obj,
    }
    return render(request, "network/index.html", context)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def post(request):
    if request.method == "POST":
        post = Post(user=request.user)
        form = forms.PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.headers["Referer"])
        else:
            return HttpResponseBadRequest("Bad requst: invalid form data")
    else:
        return HttpResponseBadRequest("Bad request: only POST access is supported")


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    posts = Post.objects.filter(user=user)
    page_obj = annotate_and_paginate(request, posts)

    context = {
        "title": f"{user.username}'s Profile",
        "following": user.following.count(),
        "followers": user.followers.count(),
        "profile_user": user,
        "is_following": request.user.is_authenticated and request.user.following.filter(pk=user.id).exists(),
        "page_obj": page_obj,
    }
    return render(request, "network/profile.html", context)


@login_required
def follow(request, id):
    if request.method == "POST":
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return HttpResponseBadRequest("Bad request: user does not exist")
        if user == request.user:
            return HttpResponseBadRequest("Bad request: cannot follow oneself")
        if not request.user.following.filter(pk=user.id):
            request.user.following.add(user)
        else:
            return HttpResponseBadRequest("Bad request: already following user")
        return HttpResponseRedirect(reverse("profile", args=[user.username]))
    return HttpResponseBadRequest("Bad request: only POST access is supported")


@login_required
def unfollow(request, id):
    if request.method == "POST":
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return HttpResponseBadRequest("Bad request: user does not exist")
        if user == request.user:
            return HttpResponseBadRequest("Bad request: cannot unfollow oneself")
        if request.user.following.filter(pk=user.id):
            request.user.following.remove(user)
        else:
            return HttpResponseBadRequest("Bad request: not following user")
        return HttpResponseRedirect(reverse("profile", args=[user.username]))
    return HttpResponseBadRequest("Bad request: only POST access is supported")


@login_required
def following(request):
    posts = Post.objects.filter(user__in=request.user.following.all())
    page_obj = annotate_and_paginate(request, posts)

    context = {
        "title": "Posts of Followed Users",
        "page_obj": page_obj,
    }
    return render(request, "network/index.html", context)


@login_required
def edit(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(user=request.user, pk=id)
        except Post.DoesNotExist:
            return HttpResponseBadRequest("Bad request: post does not exist")
        form = forms.PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204)
        else:
            return HttpResponseBadRequest("Bad requst: invalid form data")
    else:
        return HttpResponseBadRequest("Bad request: only POST access is supported")


@login_required
def like(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            return HttpResponseBadRequest("Bad request: post does not exist")
        if not post.likes.filter(pk=request.user.id):
            post.likes.add(request.user)
        else:
            return HttpResponseBadRequest("Bad request: post already liked")
        return HttpResponse(status=204)
    return HttpResponseBadRequest("Bad request: only POST access is supported")


@login_required
def unlike(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            return HttpResponseBadRequest("Bad request: post does not exist")
        if post.likes.filter(pk=request.user.id):
            post.likes.remove(request.user)
        else:
            return HttpResponseBadRequest("Bad request: post not liked")
        return HttpResponse(status=204)
    return HttpResponseBadRequest("Bad request: only POST access is supported")


def annotate_and_paginate(request, posts):
    if request.user.is_authenticated:
        posts = posts.annotate(is_liked=Count("likes", filter=Q(likes=request.user)))
    posts = posts.order_by("-creation_time")
    paginator = Paginator(posts, 10)

    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return page_obj
