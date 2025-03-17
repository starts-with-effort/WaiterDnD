from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .models import Category, Dish, Table, Customer, Order, OrderItem, Payment
from .serializers import (
    CategorySerializer, DishSerializer, TableSerializer, CustomerSerializer,
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer, PaymentSerializer
)
from .services import (
    CategoryService, DishService, TableService, CustomerService,
    OrderService, PaymentService
)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        return CategoryService.get_all_categories(active_only=active_only)

class DishViewSet(viewsets.ModelViewSet):
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        available_only = self.request.query_params.get('available_only', 'true').lower() == 'true'
        category_id = self.request.query_params.get('category_id')
        return DishService.get_all_dishes(available_only=available_only, category_id=category_id)
    
    @action(detail=False, methods=['GET'])
    def featured(self, request):
        dishes = DishService.get_featured_dishes()
        serializer = self.get_serializer(dishes, many=True)
        return Response(serializer.data)

class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        return TableService.get_all_tables(active_only=active_only)
    
    @action(detail=False, methods=['GET'])
    def available(self, request):
        tables = TableService.get_available_tables()
        serializer = self.get_serializer(tables, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def by_document(self, request):
        document_number = request.query_params.get('document_number')
        if not document_number:
            return Response({"error": "Document number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        customer = CustomerService.get_customer_by_document(document_number)
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def update_loyalty_points(self, request, pk=None):
        points_to_add = request.data.get('points', 0)
        try:
            customer = CustomerService.update_loyalty_points(pk, points_to_add)
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        return OrderService.get_all_orders(status=status_filter)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create_order(serializer.validated_data)
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['PATCH'])
    def update_status(self, request, pk=None):
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = OrderService.update_order_status(pk, new_status)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'])
    def by_table(self, request):
        table_id = request.query_params.get('table_id')
        if not table_id:
            return Response({"error": "Table ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        orders = OrderService.get_orders_by_table(table_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_customer(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        orders = OrderService.get_orders_by_customer(customer_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def daily_sales(self, request):
        date_str = request.query_params.get('date')
        date = None
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        sales_data = OrderService.get_daily_sales(date=date)
        return Response(sales_data)

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OrderItem.objects.all()
    
    @action(detail=True, methods=['PATCH'])
    def update_status(self, request, pk=None):
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item = OrderService.update_order_item_status(pk, new_status)
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.all()
    
    def create(self, request, *args, **kwargs):
        order_id = request.data.get('order')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        payment_reference = request.data.get('payment_reference', '')
        
        try:
            payment = PaymentService.create_payment(
                order_id, amount, payment_method, payment_reference
            )
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'])
    def by_order(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        payments = PaymentService.get_payments_by_order(order_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)