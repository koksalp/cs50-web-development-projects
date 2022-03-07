from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person", default="") 
    content = models.CharField(max_length=255)
    date = models.CharField(max_length = 32)
    number_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f"content: {self.content} person who made the post is {self.person.username}" 

    def serialize(self):
        return {
            "id": self.id,
            "person": self.person.username,
            "content": self.content,
            "date": self.date,
            "number_of_likes": self.number_of_likes
        }
         
class Comment(models.Model):
    comment = models.CharField(max_length=255)    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post", default="")

    def __str__(self):
        return f"{self.comment} is made for the post content {self.post.content}" 

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", default="") 
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", default="") 

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}" 

class Like(models.Model):
    like_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_from", default="") 
    liked_post =  models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_post", default="") 
    
    def __str__(self):
        return f"{self.like_from.username} likes {self.liked_post.person.username}'s post. Post id: {self.liked_post.id}"   