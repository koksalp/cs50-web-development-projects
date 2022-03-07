from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sold", views.sold, name="sold"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.category, name="category"),
    path("categories/<str:category>", views.display, name="display"),
    path("items/<int:item_id>", views.item, name="item"),
    path("create", views.create, name="create"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist")
]
