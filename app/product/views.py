"""
Views for product API.
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from product.serializers import (
    ProductSerializer,
)
from core.models import (
    Product,
)


class ProductViewSet(viewsets.ModelViewSet):
    """View for manage product APIs."""

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve product for authenticated users."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
