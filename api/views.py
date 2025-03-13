from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item
from .serializers import ItemSerializer
from .services import ItemService

class ItemListView(APIView):
    """API view for listing and creating items"""
    
    def get(self, request):
        """Get all items"""
        items = ItemService.get_all_items()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new item"""
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            item = ItemService.create_item(serializer.validated_data)
            return Response(
                ItemSerializer(item).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemDetailView(APIView):
    """API view for retrieving, updating and deleting an item"""
    
    def get_object(self, item_id):
        """Helper method to get item by ID"""
        return ItemService.get_item_by_id(item_id)
    
    def get(self, request, item_id):
        """Get an item by ID"""
        item = self.get_object(item_id)
        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    
    def put(self, request, item_id):
        """Update an item"""
        item = self.get_object(item_id)
        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            updated_item = ItemService.update_item(item, serializer.validated_data)
            return Response(ItemSerializer(updated_item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, item_id):
        """Delete an item"""
        item = self.get_object(item_id)
        if not item:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        ItemService.delete_item(item)
        return Response(status=status.HTTP_204_NO_CONTENT)
