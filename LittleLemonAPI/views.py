from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order, OrderItem, Category
from rest_framework import serializers
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer, UserSerializer
#from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination

# Create your views here.
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({'message': 'Succesful'})

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def throttle_check_auth(request):
    return Response({'message': 'message for the logged in users only'})

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def manager(request):
    """
    Endpoint to return all managers or assign the user in the request payload to the manager group
    """
    is_admin = request.user.is_staff or request.user.is_superuser
    is_manager = request.user.groups.filter(name='Manager').exists()
    # If the user is a manager or an admin, allow them to get all managers or assign a user to the manager group
    if is_admin or is_manager:
        if request.method == 'GET':
            managers = User.objects.filter(groups__name='Manager')
            serialized_item = UserSerializer(managers, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            user = get_object_or_404(User, username=request.data['username'])
            group = Group.objects.get(name='Manager')
            group.user_set.add(user)
            return Response({'message': 'User assigned to manager group'}, status=status.HTTP_200_OK)
    else:
        return Response({'error' : 'You do not have permission to assign users to the manager group'}, status=status.HTTP_403_FORBIDDEN)
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_manager(request, pk):
    """
    Endpoint to remove a user from the manager group
    """
    is_admin = request.user.is_staff or request.user.is_superuser
    is_manager = request.user.groups.filter(name='Manager').exists()
    if is_admin or is_manager:
        # If the user is a manager or an admin, allow them to remove a user from the manager group
        user = get_object_or_404(User, pk=pk)
        group = Group.objects.get(name='Manager')
        # Check if the user is in the manager group
        if user not in group.user_set.all():
            return Response({'error' : 'User is not in the manager group'}, status=status.HTTP_400_BAD_REQUEST)
        group.user_set.remove(user)
        return Response({'message': 'User removed from manager group'}, status=status.HTTP_200_OK)
    else:
        return Response({'error' : 'You do not have permission to remove users from the manager group'}, status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    """
    Endpoint to return all delivery crew members or assign the user in the request payload to the delivery crew group
    """
    if request.user.groups.filter(name='Manager').exists():
        # If the user is a manager, return all users in the delivery crew group
        if request.method == 'GET':
            delivery_crew = User.objects.filter(groups__name='Delivery crew')
            serialized_item = UserSerializer(delivery_crew, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            # If the user is a manager, assign the user in the request to the delivery crew group
            user = get_object_or_404(User, username=request.data['username'])
            group = Group.objects.get(name='Delivery crew')
            group.user_set.add(user)
            return Response({'message': 'User assigned to delivery crew group'}, status=status.HTTP_200_OK)
    else:
        return Response({'error' : 'You do not have permission to assign users to the delivery crew group'}, status=status.HTTP_403_FORBIDDEN)
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_delivery_crew(request, pk):
    """
    Endpoint to remove a user from the delivery crew group
    """
    if request.user.groups.filter(name='Manager').exists():
        # If the user is a manager, remove the user from the delivery crew group
        user = get_object_or_404(User, pk=pk)
        group = Group.objects.get(name='Delivery crew')
        # Check if the user is in the delivery crew group
        if user not in group.user_set.all():
            return Response({'error' : 'User is not in the delivery crew group'}, status=status.HTTP_400_BAD_REQUEST)
        group.user_set.remove(user)
        return Response({'message': 'User removed from delivery crew group'}, status=status.HTTP_200_OK)
    else:
        return Response({'error' : 'You do not have permission to remove users from the delivery crew group'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    """
    Endpoint to get all menu items or create a new menu item
    """
    is_admin = request.user.is_staff or request.user.is_superuser
    is_manager = request.user.groups.filter(name='Manager').exists()
    # If the user is a manager or an admin, allow them to create new menu items or get all menu items
    if is_admin or is_manager:
        if request.method == 'POST':
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            items = MenuItem.objects.select_related('category').all()
            # Filter the menu items based on the query parameters
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            if category_name:
                items = items.filter(category__title=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            if search:
                items = items.filter(title__icontains=search)
            if ordering:
                items = items.order_by(ordering)
            # Use DRF pagination
            paginator = PageNumberPagination()
            paginated_items = paginator.paginate_queryset(items, request)
            serialized_item = MenuItemSerializer(paginated_items, many=True)
            return paginator.get_paginated_response(serialized_item.data)
    else:
        # If the user is not a manager, only allow them to get all menu items
        if request.method == 'GET':
            items = MenuItem.objects.select_related('category').all()
            # Filter the menu items based on the query parameters
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            if category_name:
                items = items.filter(category__title=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            if search:
                items = items.filter(title__icontains=search)
            if ordering:
                items = items.order_by(ordering)
            # Use DRF pagination
            paginator = PageNumberPagination()
            paginated_items = paginator.paginate_queryset(items, request)
            serialized_item = MenuItemSerializer(paginated_items, many=True)
            return paginator.get_paginated_response(serialized_item.data)
        else:
            return Response({'error' : 'You do not have permission to create menu items'}, status=status.HTTP_403_FORBIDDEN)
        
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item(request, pk):
    """
    Endpoint to get, update or delete a specific menu item
    """
    if request.user.groups.filter(name='Manager').exists():
        # If the user is a manager, allow them to get, update or delete a specific menu item
        item = get_object_or_404(MenuItem, pk=pk)
        if request.method == 'GET':
            serialized_item = MenuItemSerializer(item)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            # Allow updates
            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'PATCH':
            # Allow partial updates
            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        # If the user is not a manager, only allow them to get a specific menu item
        if request.method == 'GET':
            item = get_object_or_404(MenuItem, pk=pk)
            serialized_item = MenuItemSerializer(item)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            return Response({'error' : 'You do not have permission to update or delete this menu item'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def categories(request):
    """
    Endpoint to get all categories or create a new category
    """
    is_admin = request.user.is_staff or request.user.is_superuser
    if is_admin:
        # If the user is an admin, allow them to create new category or get all categories
        if request.method == 'GET':
            items = Category.objects.all()
            serialized_item = CategorySerializer(items, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # If the user is not an admin, only allow them to get all categories
        if request.method == 'GET':
            items = Category.objects.all()
            serialized_item = CategorySerializer(items, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        else:
            return Response({'error' : 'You do not have permission to create categories'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    """
    Endpoint to get/delete all menu items in the cart or add a new menu item to the cart
    """
    is_manager = request.user.groups.filter(name='Manager').exists()
    is_delivery_crew = request.user.groups.filter(name='Delivery Crew').exists()
    if is_manager or is_delivery_crew:
        # Managers and delivery crew members should not be able to access this endpoint
        return Response({'error' : 'You do not have permission to access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    else:
        # If the user is a customer, allow them to get all menu items in the cart or add a new menu item to the cart
        if request.method == 'GET':
            items = Cart.objects.filter(user=request.user)
            serialized_item = CartSerializer(items, many=True)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            # Copy request.data to a mutable dictionary
            data = request.data.copy()
            # Sets the authenticated user as the user in the cart
            data['user'] = request.user.id
            # Sets the unit price and price to the menu item price
            menu_item = get_object_or_404(MenuItem, pk=data['menu_item'])
            unit_price = menu_item.price
            price = float(menu_item.price) * int(data['quantity'])
            serializer = CartSerializer(data=data)
            if serializer.is_valid():
                # These fields are set manually in the serializer to avoid validation errors
                # because they are read-only fields in the Cart serializer
                serializer.save(user=request.user, unit_price=unit_price, price=price)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            items = Cart.objects.filter(user=request.user)
            items.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders(request):
    """
    Endpoint to get all orders or create a new order
    """
    is_manager = request.user.groups.filter(name='Manager').exists()
    is_delivery_crew = request.user.groups.filter(name='Delivery Crew').exists()
    if is_manager:
        # If the user is a manager, allow them to get all orders
        if request.method == 'GET':
            items = Order.objects.select_related('user', 'delivery_crew').all()
            # Filter the orders based on the query parameters
            order_status = request.query_params.get('status')
            user = request.query_params.get('user')
            delivery_crew = request.query_params.get('delivery_crew')
            # Sort the orders based on the query parameters
            ordering = request.query_params.get('ordering')
            if order_status:
                items = items.filter(status=order_status)
            if user:
                items = items.filter(user__username=user)
            if delivery_crew:
                items = items.filter(delivery_crew__username=delivery_crew)
            if ordering:
                items = items.order_by(ordering)
            # Use DRF pagination
            paginator = PageNumberPagination()
            paginated_items = paginator.paginate_queryset(items, request)
            serialized_item = OrderSerializer(paginated_items, many=True)
            return paginator.get_paginated_response(serialized_item.data)
        else:
            return Response({'error' : 'You do not have permission to create orders'}, status=status.HTTP_403_FORBIDDEN)
    if is_delivery_crew:
        # If the user is a delivery crew, allow them to get all orders assigned to this user
        if request.method == 'GET':
            items = Order.objects.filter(delivery_crew=request.user)
            # Filter the orders based on the query parameters
            order_status = request.query_params.get('status')
            user = request.query_params.get('user')
            # Sort the orders based on the query parameters
            ordering = request.query_params.get('ordering')
            # Add pagination
            if order_status:
                items = items.filter(status=order_status)
            if user:
                items = items.filter(user__username=user)
            if ordering:
                items = items.order_by(ordering)
            # Use DRF pagination
            paginator = PageNumberPagination()
            paginated_items = paginator.paginate_queryset(items, request)
            serialized_item = MenuItemSerializer(paginated_items, many=True)
            return paginator.get_paginated_response(serialized_item.data)
        else:
            return Response({'error' : 'You do not have permission to create orders'}, status=status.HTTP_403_FORBIDDEN)
    else:
        # If the user is a customer, allow them to get all orders created by this user or create a new order
        if request.method == 'GET':
            try:
                # Get all orders created by the authenticated user
                items = Order.objects.filter(user=request.user)
            except Order.DoesNotExist:
                # If no orders exist, return an empty list
                items = Order.objects.none()
            # Sort the orders based on the query parameters
            ordering = request.query_params.get('ordering')
            if ordering:
                items = items.order_by(ordering)
            # Use DRF pagination
            paginator = PageNumberPagination()
            paginated_items = paginator.paginate_queryset(items, request)
            serialized_item = OrderSerializer(paginated_items, many=True)
            return paginator.get_paginated_response(serialized_item.data)
        if request.method == 'POST':
            # Copy request.data to a mutable dictionary
            data = request.data.copy()
            # Sets the authenticated user as the user in the order
            data['user'] = request.user.id
            # Sets the total to the sum of all items in the cart
            items = Cart.objects.filter(user=request.user)
            total = 0
            for item in items:
                total += item.price
            data['total'] = total
            serializer = OrderSerializer(data=data)
            if serializer.is_valid():
                order_instance = serializer.save(user=request.user)
                # Add cart items to OrderItem table
                for cart_item in items:
                    OrderItem.objects.create(
                        order=order_instance,
                        menu_item=cart_item.menu_item,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        price=cart_item.price
                    )
                # Clear the cart after creating the order
                items.delete()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order(request, pk):
    """
    Endpoint to get all menuitems of a specific order, and update or delete the order
    1. If the user is a manager, allow them to partially update or delete a specific order
    """
    is_manager = request.user.groups.filter(name='Manager').exists()
    is_delivery_crew = request.user.groups.filter(name='Delivery Crew').exists()
    if is_manager:
        # If the user is a manager, allow them to partially update or delete a specific order
        order = get_object_or_404(Order, pk=pk)
        if request.method == 'DELETE':
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'PATCH':
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error' : 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
    if is_delivery_crew:
        # If the user is a delivery crew, allow them to update the status of a specific order to 0 or 1
        order = get_object_or_404(Order, pk=pk)
        if request.method == 'PATCH':
            if request.data['status'] in [0, 1]:
                serializer = OrderSerializer(order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error' : 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error' : 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
    else:
        # If the user is a customer, allow them to get all menuitems of a specific order, and update or delete the order
        # Only allow the user to access their own orders
        order = get_object_or_404(Order, pk=pk)
        if request.method == 'GET':
            if request.user == order.user:
                items = OrderItem.objects.filter(order=order)
                serialized_items = OrderItemSerializer(items, many=True)
                return Response(serialized_items.data, status=status.HTTP_200_OK)
            else:
                return Response({'error' : 'You do not have permission to access this order'}, status=status.HTTP_403_FORBIDDEN)
        if request.method == 'PUT':
            if request.user == order.user:
                serializer = OrderSerializer(order, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error' : 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
        if request.method == 'PATCH':
            if request.user == order.user:
                serializer = OrderSerializer(order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error' : 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
