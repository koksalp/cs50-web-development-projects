from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt 
import json 
from datetime import datetime 
from .models import * 
import math 

def index(request): 
    
    # if POST request is received 
    if request.method == "POST": 

        # execute here if user submits a new post 
        if request.POST.get("post") == "Post": 
            now = get_now()
            content = request.POST["new_post"]  
            new_post = Post(person=request.user, content=content, date=now) 
            new_post.save()

            # redirect user to main page after submitting the post 
            return HttpResponseRedirect(reverse("index")) 
        
        # if user is logged in, get the id of the posts the current user has liked, otherwise return empty list 
        if request.user.id is not None: 
            posts_liked = [like.liked_post.id for like in Like.objects.filter(like_from=request.user)]  
        else: 
            posts_liked = [] 

        # get all necessary information sent with POST request  
        posts = Post.objects.all()[::-1] 
        pages = list(range(1, math.ceil(len(posts) / 10) + 1)) 
        page = int(request.POST.get("select"))
        is_previous = request.POST.get("previous") 
        is_next = request.POST.get("next") 

        # if previous button is clicked 
        if is_previous == "previous": 
            page -= 1 

        # if next button is clicked 
        if is_next == "next":  
            page += 1 

        # index of the first post in posts 
        starting_post = (page - 1) * 10 

        # render index.html with given parameters 
        return render(request, "network/index.html", { 
        "posts": posts[starting_post: starting_post + 10], 
        "posts_liked": posts_liked,       
        "pages": pages,  
        "next": True if len(pages) > 1 and page != pages[-1] else False,  
        "previous": True if page > 1 else False, 
        "current_page": page 
        })  

    # if GET request is received 
    # get all the posts and calculate the number of pages 
    posts = Post.objects.all()[::-1] 
    pages = list(range(1, math.ceil(len(posts) / 10) + 1)) 

    # if user is authenticated 
    if request.user.is_authenticated:  
        posts_liked = [like.liked_post.id for like in Like.objects.filter(like_from=request.user)]  

        return render(request, "network/index.html", {
        "posts": posts[:10], 
        "posts_liked": posts_liked,       
        "pages": pages,  
        "next": True if len(pages) > 1 else False,     
        "current_page": 1 
    })

    # if user is not authenticated 
    return render(request, "network/index.html", {
        "posts": posts[:10], 
        "pages": pages,  
        "next": True if len(pages) > 1 else False,     
        "current_page": 1 
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

@csrf_exempt 
@login_required
def post(request, post_id):

    # Query for requested post  
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404) 

    # Return post contents
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update corresponding data if PUT request is received   
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("number_of_likes") is not None:
            post.number_of_likes = data["number_of_likes"]
        if data.get("content") is not None:
            post.content = data["content"] 
        if data.get("date") is not None:
            post.date = data["date"] 
        post.save()
        return HttpResponse(status=204)  

    # POST request is sreceived   
    elif request.method == "POST": 

        # get content 
        data = json.loads(request.body) 

        # if user liked a post, create a Like object and save 
        if data.get("like"):  
            like = Like(like_from = request.user, liked_post = post)    
            like.save()  

        # else delete like object     
        else: 
            try:
                like = Like.objects.get(like_from = request.user, liked_post = post) 
                like.delete() 
            except Like.DoesNotExist:
                return JsonResponse({"error": "An error occured."}, status=404)   

        return JsonResponse({"message": "Success"}, status=201)  

    else:
        return JsonResponse({
            "error": "GET,POST or PUT request required." 
        }, status=400)
 
# function that returns the current time 
def get_now():
    now = str(datetime.now())
    now = now[:now.find(".")]
    return now  

@csrf_exempt 
@login_required 
def following(request):
    
    # get all the posts of following people 
    posts = []
    followings = Follow.objects.filter(follower=request.user)
    for i in followings: 
        posts.extend([post for post in Post.objects.filter(person=i.following)])
    posts=posts[::-1] 

    # get all the post ids of liked posts 
    posts_liked = [like.liked_post.id for like in Like.objects.filter(like_from=request.user)]  

    # calculate the number of the pages 
    pages = list(range(1, math.ceil(len(posts) / 10) + 1)) 

    # get all the necessary information and render follow.html with given parameters 
    if request.method == "POST": 
        page = int(request.POST.get("select"))
        is_previous = request.POST.get("previous") 
        is_next = request.POST.get("next") 
        if is_previous == "previous": 
            page -= 1
        if is_next == "next":  
            page += 1 
        starting_post = (page - 1) * 10 

        return render(request, "network/follow.html", { 
        "posts": posts[starting_post: starting_post + 10], 
        "posts_liked": posts_liked,   
        "pages": pages,  
        "next": True if len(pages) > 1 and page != pages[-1] else False,  
        "previous": True if page > 1 else False, 
        "current_page": page 
        })

    # render follow.html if GET request is received 
    return render(request, "network/follow.html", {
        "posts": posts[:10], 
        "number_of_buttons": list(range(1, math.ceil(len(posts) / 10) + 1)),
        "posts_liked": posts_liked,   
        "pages": pages,  
        "next": True if len(pages) > 1 else False,     
        "current_page": 1 
    }) 
    
@csrf_exempt 
@login_required 
def profile(request, user_id): 

    # get user 
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404) 
        
    # owner indicates if the profile page belongs to the user 
    owner = True if user_id == request.user.id else False 

    # follow infos 
    is_following = True if len(Follow.objects.filter(follower=request.user, following=user)) != 0 else False 
    followings = Follow.objects.filter(follower=user) 
    followers = Follow.objects.filter(following=user) 

    # get all posts of the user that owns the profile page 
    posts = Post.objects.filter(person=user) 

    # all the posts that current user has liked    
    posts_liked = [like.liked_post.id for like in Like.objects.filter(like_from=request.user)] 

    # number of pages in a list  
    pages = list(range(1, math.ceil(len(posts) / 10) + 1)) 

    # POST request is received   
    if request.method == "POST": 

        # get all the necessary information  
        page = int(request.POST.get("select"))
        is_previous = request.POST.get("previous") 
        is_next = request.POST.get("next") 
        if is_previous == "previous": 
            page -= 1
        if is_next == "next":  
            page += 1 
        starting_post = (page - 1) * 10 

        # render profile.html with given parameters  
        return render(request, "network/profile.html", {
            "followings": followings,
            "number_of_followings": len(followings),
            "followers": followers, 
            "number_of_followers": len(followers),
            "posts": posts[starting_post: starting_post + 10],
            "is_following": is_following, 
            "user_p": user, 
            "owner": owner,    
            "posts_liked": posts_liked,   
            "pages": pages,  
            "next": True if len(pages) > 1 and page != pages[-1] else False,  
            "previous": True if page > 1 else False, 
            "current_page": page 
        })    
    
    # render profile.html with given parameters if GET request is received  
    return render(request, "network/profile.html", {
        "followings": followings,
        "number_of_followings": len(followings),
        "followers": followers, 
        "number_of_followers": len(followers),
        "posts": posts[:10],
        "is_following": is_following, 
        "user_p": user, 
        "owner": owner,    
        "posts_liked": posts_liked,   
        "pages": pages,  
        "next": True if len(pages) > 1 else False,     
        "current_page": 1 
    })   
 
# API route for follow operation   
@csrf_exempt 
@login_required 
def handle_follow(request):

    # POST request only 
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get content   
    data = json.loads(request.body) 

    # get id of the user to be followed or unfollowed  
    user_id = data.get("user_id") 

    # follow or unfollow  
    follow = data.get("follow") 

    # error checking 
    try:
        user = User.objects.get(id=user_id) 
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"User with id {user_id} does not exist."
        }, status=400) 
    
    # error checking 
    check = Follow.objects.filter(follower=request.user, following=user) 

    # execute here if current user wants to follow a user 
    if follow: 

        if len(check) == 0:
            follow_object = Follow(follower=request.user, following=user) 
            follow_object.save() 
        else:  
            
            # error message 
            return JsonResponse({
                "error": "An error occured." 
            }, status=400) 
        number_of_followers = len(Follow.objects.filter(following=user)) 

        # return a success message that contains number of followers of the user that current user followed 
        return JsonResponse({"message": "Success", "number_of_followers": number_of_followers}, status=201) 

    # execute here if current user wants to unfollow a user 
    else:
        if len(check) == 1:
            check.delete() 
            number_of_followers = len(Follow.objects.filter(following=user)) 

            # return a success message that contains number of followers of the user that current user unfollowed    
            return JsonResponse({"message": "Success", "number_of_followers": number_of_followers}, status=201) 

        # error message 
        return JsonResponse({
            "error": "An error occured." 
        }, status=400)     