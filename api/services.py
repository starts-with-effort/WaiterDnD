from django.db.models import Sum, Count
from django.db import transaction
from datetime import datetime, timedelta
from .models import Category, Dish, Table, Customer, Order, OrderItem, Payment

class CategoryService:
    @staticmethod
    def get_all_categories(active_only=True):
        queryset = Category.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @staticmethod
    def get_category_by_id(category_id):
        return Category.objects.get(id=category_id)

class DishService:
    @staticmethod
    def get_all_dishes(available_only=True, category_id=None):
        queryset = Dish.objects.all()
        
        if available_only:
            queryset = queryset.filter(is_available=True)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
    
    @staticmethod
    def get_featured_dishes():
        return Dish.objects.filter(is_featured=True, is_available=True)
    
    @staticmethod
    def get_dish_by_id(dish_id):
        return Dish.objects.get(id=dish_id)

class TableService:
    @staticmethod
    def get_all_tables(active_only=True):
        queryset = Table.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @staticmethod
    def get_available_tables():
        # Mesas que no tienen órdenes pendientes o en preparación
        active_tables = Table.objects.filter(is_active=True)
        busy_tables = Order.objects.filter(
            status__in=['pending', 'preparing'],
            table__isnull=False
        ).values_list('table_id', flat=True)
        
        return active_tables.exclude(id__in=busy_tables)
    
    @staticmethod
    def get_table_by_id(table_id):
        return Table.objects.get(id=table_id)

class CustomerService:
    @staticmethod
    def get_all_customers():
        return Customer.objects.all()
    
    @staticmethod
    def get_customer_by_id(customer_id):
        return Customer.objects.get(id=customer_id)
    
    @staticmethod
    def get_customer_by_document(document_number):
        return Customer.objects.filter(document_number=document_number).first()
    
    @staticmethod
    def update_loyalty_points(customer_id, points_to_add):
        customer = Customer.objects.get(id=customer_id)
        customer.loyalty_points += points_to_add
        customer.save()
        return customer

class OrderService:
    @staticmethod
    def get_all_orders(status=None):
        queryset = Order.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_orders_by_table(table_id):
        return Order.objects.filter(table_id=table_id).order_by('-created_at')
    
    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer_id=customer_id).order_by('-created_at')
    
    @staticmethod
    def get_order_by_id(order_id):
        return Order.objects.get(id=order_id)
    
    @staticmethod
    @transaction.atomic
    def create_order(data):
        items_data = data.pop('items', [])
        order = Order.objects.create(**data)
        
        for item_data in items_data:
            dish_id = item_data.get('dish')
            quantity = item_data.get('quantity', 1)
            notes = item_data.get('notes', '')
            
            dish = Dish.objects.get(id=dish_id)
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=quantity,
                price=dish.price,
                notes=notes
            )
        
        order.save()  # Esto invoca el método save() que calcula el total
        return order
    
    @staticmethod
    @transaction.atomic
    def update_order_status(order_id, new_status):
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        return order
    
    @staticmethod
    @transaction.atomic
    def update_order_item_status(item_id, new_status):
        item = OrderItem.objects.get(id=item_id)
        item.status = new_status
        item.save()
        return item
    
    @staticmethod
    def get_daily_sales(date=None):
        if not date:
            date = datetime.now().date()
        
        end_date = date + timedelta(days=1)
        return Order.objects.filter(
            created_at__gte=date,
            created_at__lt=end_date,
            is_paid=True
        ).aggregate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        )

class PaymentService:
    @staticmethod
    def get_payments_by_order(order_id):
        return Payment.objects.filter(order_id=order_id)
    
    @staticmethod
    @transaction.atomic
    def create_payment(order_id, amount, payment_method, payment_reference=''):
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_method=payment_method,
            payment_reference=payment_reference
        )
        
        # Calcular el total pagado
        total_paid = Payment.objects.filter(order=order).aggregate(
            total=Sum('amount'))['total'] or 0
        
        # Actualizar el estado de pago de la orden
        if total_paid >= order.total_amount:
            order.is_paid = True
            order.payment_method = payment_method
            order.save()
        
        return payment