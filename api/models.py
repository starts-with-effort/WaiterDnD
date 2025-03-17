from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Category(BaseModel):
    """Categoría de platos (entradas, platos fuertes, postres, etc.)"""
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True)
    # image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Dish(BaseModel):
    """Platos disponibles en el menú"""
    name = models.CharField(max_length=100)
    # description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #preparation_time = models.IntegerField(help_text="Tiempo de preparación en minutos")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes')
    # ingredients = models.ManyToManyField(Ingredient, through='DishIngredient')
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    # calories = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Table(BaseModel):
    """Mesas del restaurante"""
    number = models.IntegerField(unique=True)
    # capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Mesa {self.number} (Cap: {self.capacity})"

class Customer(BaseModel):
    """Clientes registrados en el sistema"""
    document_number = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Order(BaseModel):
    """Pedidos realizados"""
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('preparing', 'En preparación'),
        ('ready', 'Listo'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    is_paid = models.BooleanField(default=False)
    waiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    def __str__(self):
        if self.customer:
            return f"Orden #{self.id} - {self.customer.name}"
        return f"Orden #{self.id}"
    
    def calculate_total(self):
        """Calcula el monto total de la orden"""
        return sum(item.subtotal for item in self.orderitem_set.all())
    
    def save(self, *args, **kwargs):
        """Actualiza el total de la orden antes de guardar"""
        if self.id:
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

class OrderItem(BaseModel):
    """Items dentro de una orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        """Establece el precio basado en el plato si es un nuevo item"""
        if not self.id and not self.price:
            self.price = self.dish.price
        super().save(*args, **kwargs)

class Payment(BaseModel):
    """Pagos realizados por los clientes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Pago #{self.id} - Orden #{self.order.id}"

