from django.urls import path

from .views import logout, me, my_factory, register

urlpatterns = [
    path("register/", register, name="register"),
    path("logout/", logout, name="logout"),
    path("me/", me, name="me"),
    path("my-factory/", my_factory, name="my_factory"),
]
