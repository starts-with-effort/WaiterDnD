from django.urls import path
from .views import ItemListView, ItemDetailView

urlpatterns = [
    path('items/', ItemListView.as_view(), name='item-list'),
    path('items/<int:item_id>/', ItemDetailView.as_view(), name='item-detail'),
]