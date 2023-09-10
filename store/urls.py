from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('contact', views.contact, name="contact"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updadeItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('check_quantity/', views.check_quantity, name="check_quantity"),
    path('product/<int:product_id>/', views.view_product, name='view_product'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_products, name='search'),
    path('Auth_site', views.Auth_site, name='Auth_site'),

    path('<str:category_name>/', views.categories, name='categories'),
    path('<str:category_name>/<str:subcategory_name>/', views.subcategories, name='subcategories'),
]
