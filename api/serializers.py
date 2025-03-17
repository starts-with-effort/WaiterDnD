from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Dish, Table, Customer, Order, OrderItem, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'category', 'category_name', 'image', 
                  'is_available', 'is_featured', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'document_number', 'user', 'user_details', 'name', 'email', 
                  'phone', 'address', 'loyalty_points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'loyalty_points', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'dish', 'dish_name', 'quantity', 'price', 'notes', 
                  'status', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'subtotal', 'created_at', 'updated_at']

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'notes']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    table_number = serializers.ReadOnlyField(source='table.number')
    waiter_name = serializers.ReadOnlyField(source='waiter.username')
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'table', 'table_number', 
                  'status', 'notes', 'total_amount', 'payment_method', 
                  'is_paid', 'waiter', 'waiter_name', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['customer', 'table', 'notes', 'waiter', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        order.save()  # Esto invoca el método save() que calcula el total
        return order

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.ReadOnlyField(source='order.id')
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_id', 'amount', 'payment_method', 
                  'payment_reference', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']