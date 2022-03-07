from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Comment, User, Listings

def index(request):
    listings = Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
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

def category(request):
    categories = set()
    all_categories = Listings.objects.all()
    for category in all_categories:
        categories.add(category.category)
    return render(request, "auctions/categories.html", {
        "categories": sorted(categories)
    })

def display(request, category):
    all = Listings.objects.filter(category = category)
    return render(request, "auctions/category.html", {"all": all})

def item(request, item_id):
    if request.method == "POST":        
        new_comment = request.POST["comment"]
        comment = Comment(comment=new_comment, person_id=request.user.id, item_id=item_id)
        comment.save()
        return HttpResponse(new_comment)
    item = Listings.objects.get(pk=item_id)
    empty = 1
    try:
        comments = Comment.objects.all(item_id=item_id)
        empty = 0
    except TypeError:
        pass
    if empty:
        return render(request , "auctions/items.html", {"item": item, "empty": empty})

    return render(request , "auctions/items.html", {"item": item, "comments": comments})
