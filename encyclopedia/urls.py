from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.createNewPage, name="create_new_page"),
    path("wiki/<str:title>", views.display, name="display"),
    path("random", views.random, name="random"),
    path("edit", views.edit, name="edit") 
]
