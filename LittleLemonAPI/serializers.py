from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem, Category
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'groups']
        extra_kwargs = {
            'password': {'write_only': True},
            'groups': {'required': False}
        }
        read_only_fields = ['id']

class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the MenuItem model
    """
    category = serializers.StringRelatedField()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        read_only_fields = ['id']

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model
    """
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menu_item', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'user', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model
    """
    delivery_crew = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        read_only_fields = ['id', 'user', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model
    """
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'order', 'unit_price', 'price']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model
    """
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
        read_only_fields = ['id']