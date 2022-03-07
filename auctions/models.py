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
    def __str__(self):
        return f"{self.name} {self.price} {self.description}"

class Comment(models.Model):
    comment = models.CharField(max_length=255)    
    person_id = models.IntegerField()
    item_id = models.IntegerField()
    def __str__(self):
        return f"Person with an id of {self.person_id} made a comment. Item id: {self.item_id}" 