from django.urls import path
from .import views

urlpatterns = [
    path('groups/manager/users', views.manager), # Endpoint to return all managers or assign the user in the request payload to the manager group
    path('groups/manager/users/<int:pk>', views.remove_manager), # Endpoint to remove a user from the manager group
    path('groups/delivery-crew/users', views.delivery_crew), # Endpoint to return all delivery crew members or assign the user in the request payload to the delivery crew group
    path('groups/delivery-crew/users/<int:pk>', views.remove_delivery_crew), # Endpoint to remove a user from the delivery crew group
    path('menu-items', views.menu_items), # Endpoint to get all menu items or create a new menu item
    path('menu-items/<int:pk>', views.menu_item), # Endpoint to get, update or delete a specific menu item
    path('categories', views.categories), # Endpoint to get all categories or create a new category
    path('cart/menu-items', views.cart_menu_items), # Endpoint to get/delete all menu items in the cart or add a new menu item to the cart
    path('orders', views.orders), # Endpoint to get all orders or create a new order
    path('orders/<int:pk>', views.order), # Endpoint to get, update or delete a specific order
    path('throttle-check', views.throttle_check), # Endpoint to check if the user is throttled
    path('throttle-check-auth', views.throttle_check_auth), # Endpoint to check if the authenticated user is throttled
]