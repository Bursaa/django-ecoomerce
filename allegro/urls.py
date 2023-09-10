from django.urls import path
from . import views

urlpatterns = [
    path('Auth', views.Auth, name="allegro-auth"),
    path('Auth_callback', views.Auth_callback, name="allegro-auth-callback"),

    path('callback/<str:product_id>/<str:action>', views.callback, name="allegro-callback"),
    path('get_form/', views.get_form, name="get_form"),
    path('create_offer/', views.create_offer, name="create_offer"),
    path('end_offer/', views.end_offer, name="end_offer"),
    path('change_offer/', views.change_offer, name="change_offer"),
]
