from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listings(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    description = models.CharField(max_length=64, blank=True)
    time = models.CharField(max_length=32)
    image = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=32, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="by", default="")
    open = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.price} {self.description}"

class Comment(models.Model):
    comment = models.CharField(max_length=255)    
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person", default="")
    time = models.CharField(max_length=32, default="2021-09-02 21:30:52")
    item_id = models.IntegerField()
    
    def __str__(self):
        return f"Person with an id of {self.person_id} made a comment. Item id: {self.item_id}" 

class Watchlist(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="w_person")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="w_item")
    
    def __str__(self):
        return f"Person: {self.person.username} item: {self.item.name}"

class Bid(models.Model):
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="item_bid")
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person_bid")
    price = models.IntegerField()

    def __str__(self):
        return f"{self.person.username} made a bid for {self.item.name} and the price is: {self.price}"