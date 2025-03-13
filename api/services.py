from .models import Item

class ItemService:
    """Service class for handling Item business logic"""
    
    @staticmethod
    def get_all_items():
        """Get all active items"""
        return Item.objects.filter(is_active=True)
    
    @staticmethod
    def get_item_by_id(item_id):
        """Get item by ID"""
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return None
    
    @staticmethod
    def create_item(data):
        """Create a new item"""
        return Item.objects.create(**data)
    
    @staticmethod
    def update_item(item, data):
        """Update an existing item"""
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        return item
    
    @staticmethod
    def delete_item(item):
        """Delete an item"""
        item.delete()