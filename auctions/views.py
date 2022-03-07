from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Comment, User, Listings, Watchlist, Bid
from datetime import datetime
from django.db.models import Max

def index(request):
    listings = Listings.objects.filter(sold=False)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "from": "index"
    })

def sold(request):
    listings = Listings.objects.filter(sold=True, open=False)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "from": "sold"
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
    # create a set 
    categories = set()
    
    # retrieve all data 
    all_categories = Listings.objects.all()    
    for category in all_categories:
        # add all categories to the set called categories 
        categories.add(category.category)
    return render(request, "auctions/categories.html", {
        "categories": sorted(categories)
    })
def display(request, category):
    all = Listings.objects.filter(category = category)
    return render(request, "auctions/category.html", {"all": all})

def item(request, item_id):
    # initialize everything first that is common for items.html 
    comments = Comment.objects.filter(item_id=item_id)
    empty = 0 if len(comments) else 1
    item = Listings.objects.get(pk=item_id)
    user = User.objects.get(pk=request.user.id)     
    username = user.username
    owner = 1 if item.created_by.id == request.user.id else 0 
    bids = Bid.objects.filter(item=item)
    length = len(bids.exclude(person=item.created_by))
    bid_message = None
    message = None
    max_price = bids.aggregate(Max("price"))["price__max"]

    if max_price == None:
        max_price = item.price
    winner = None
    
    if item.sold:
        winner = "Nobody" if bids.first().item.created_by.id == bids.get(price=max_price).person.id else bids.get(price=max_price).person.id
    
    if request.method == "POST":    

        # execute here if user wants to add the item with an id of item_id to the watchlist 
        if request.POST["option"] == "1":
            if not len(Watchlist.objects.filter(person=user, item=item)):
                new_watchlist = Watchlist(person=user, item=item)
                new_watchlist.save()
                message = "Added"
                return render(request , "auctions/items.html", {"item": item, "empty": empty, "max_price":max_price, "comments": comments, "winner":winner , "username": username, "owner": owner, "length": length, "message": message, "bids": bids})
            message = "Item is already in watchlist"
            return render(request , "auctions/items.html", {"item": item, "empty": empty, "max_price":max_price, "comments": comments, "winner":winner , "username": username, "owner": owner, "length": length, "message": message, "bids": bids})
        
        # execute here if user wants to bid 
        if request.POST["option"] == "2":
            if item.created_by.id == request.user.id:
                item.open = True                   
                item.save()
                bid = Bid(item=item, person=user, price=item.price)
                bid.save() 
                bid_message = "Auction is started"
                return render(request , "auctions/items.html", {"item": item, "empty": empty, "comments": comments, "winner":winner , "username": username, "owner": owner, "length": length, "bids": bids, "max_price":max_price, "bid_message": bid_message, "message": message})

            # get bid amount 
            bid_price = int(request.POST["bid"])
            
            # make sure user's bid is greater than max_price which represents max bid or opening bid if there is no bids yet  
            if bid_price <= max_price:
                bid_message = f"Your bid must be greater than ${max_price}"
            
            # create a new bid and save 
            else:
                bid = Bid(item=item, person=user, price=bid_price)
                bid.save()
                item.price = bid_price
                item.save()
                
                # length must be increased by one 
                length += 1
                bid_message = "Your bid is the current bid"
                max_price = bid_price
            return render(request , "auctions/items.html", {"item": item, "empty": empty, "winner":winner , "comments": comments, "username": username, "owner": owner, "length": length, "max_price":max_price, "bids": bids, "bid_message": bid_message, "message": message})
        
        # execute here if owner of the item wants to close auction 
        if request.POST["option"] == "close" and item.created_by.id == request.user.id:        
            item.open = False
            item.sold = True
            item.save()
            # redirect user to the same page 
            return HttpResponseRedirect(reverse("item", args=(item_id,))) 
        
        # execute here when user wants to post a comment 
        now = str(datetime.now())
        now=now[:now.find(".")] 
        new_comment = request.POST["comment"]
        comment = Comment(comment=new_comment, person=user, item_id=item_id, time=now) 
        comment.save()
        
        # redirect user to the same page after comment is posted 
        return HttpResponseRedirect(reverse("item", args=(item_id,))) 
    
    # render items.html with given parameters if user reaches the page by GET method 
    return render(request , "auctions/items.html", {"item": item, "empty": empty, "comments": comments, "username": username, "owner": owner, "bids": bids, "winner":winner , "length": length, "max_price":max_price, "message": message})

def create(request):

    # get all the info submitted via form 
    if request.method == "POST":
        name = request.POST["name"]        
        price = request.POST["price"]
        description = request.POST["description"]
        image = request.POST["image"]
        category = request.POST["category"].strip()


        # get time info 
        now = str(datetime.now()) 
        now=now[:now.find(".")]        
        message = ""
        
        if not name:
            message = "Name cannot be empty" 
        try:       
            if int(price) < 0:
                message = "Price must be greater than or equal to 0"
        except:
            message = "Price must be greater than or equal to 0"
        if not len(message): 
            new_listing = Listings(name=name, price=price, description=description, time=now, image=image, category=category, created_by=User.objects.get(pk=request.user.id))
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/create.html", {
            "message": message
        })
    # render html file if method is GET 
    return render(request, "auctions/create.html")

        
def watchlist(request, user_id):     
    user = User.objects.get(pk=user_id)
    if request.method == "POST":   
        item = Listings.objects.get(pk=request.POST["item_id"])
        delete = Watchlist.objects.filter(person=user, item=item)
        delete.delete()
        return HttpResponseRedirect(reverse("watchlist", args=(user_id,)))
    items = Watchlist.objects.filter(person=user)    
    return render(request, "auctions/watchlist.html", {
        "listings": items
    })
