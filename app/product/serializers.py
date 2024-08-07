"""
Serializers for product API.
"""

from rest_framework import serializers

from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'link', 'description']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Method to add product to DB."""
        auth_user = self.context['request'].user
        return Product.objects.create(user=auth_user, **validated_data)

    def update(self, instance, validated_data):
        """Method to update product details."""
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
