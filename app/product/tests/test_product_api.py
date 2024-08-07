"""
Tests for product API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from product.serializers import ProductSerializer

from core.models import (
    Product,
)


PRODUCT_URL = reverse('product:product-list')


def detail_url(product_id):
    """Create URL for specific product."""
    return reverse('product:product-detail', args=[product_id])


def create_user(**params):
    """Create and return a new user."""
    defaults = {
        'email': 'test@example.com',
        'password': 'testpass123',
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


def create_product(user, **params):
    """Create and return a new product."""
    defaults = {
        'name': 'Amazon product 1',
        'link': 'www.amazon.com/product1',
        'description': 'This is a brand new product - source: Trust me bro.',
    }
    defaults.update(**params)
    product = Product.objects.create(user=user, **defaults)
    return product


class PublicProductApiTests(TestCase):
    """Tests for public product API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_products_unautheticated_unsuccess(self):
        """Test retrieving products unauthenticated return failure."""
        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTests(TestCase):
    """Tests for authenticated product api requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_products_success(self):
        """Test retrieve list of products authenticated."""

        create_product(user=self.user)
        prod2 = {
            'name': 'Product2',
            'link': 'https://amazon.in/product2',
            'description': 'Best product ever'
        }
        create_product(user=self.user, **prod2)
        res = self.client.get(PRODUCT_URL)
        products = Product.objects.filter(user=self.user).order_by('-id')
        product_serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product_serializer.data, res.data)

    def test_retrieve_product_limited_to_user(self):
        """Test list of product is limited to authenticated user."""
        create_product(user=self.user)
        create_product(user=self.user)

        user2 = create_user(email='test2@example.com')
        create_product(user=user2)
        create_product(user=user2)
        res = self.client.get(PRODUCT_URL)

        products = Product.objects.filter(user=self.user).order_by('-id')
        product_serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, product_serializer.data)

    def test_retrieve_detail_product(self):
        """Test retrieve product detail by ID."""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        res = self.client.get(url)
        product_serializer = ProductSerializer(product)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, product_serializer.data)

    def test_create_product(self):
        """Test creating a product."""
        payload = {
            'name': 'Amazon product 1',
            'link': 'www.amazon.com/product1',
            'description': 'This is a brand new product',
        }
        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(self.user, product.user)

    def test_partial_update(self):
        """Update one attribute of product."""
        payload = {
            'name': 'Updated Name',
            'description': 'This is updated description.',
        }
        product = create_product(user=self.user)
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.description, payload['description'])
        self.assertEqual(product.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing user results in error."""
        new_user = create_user(email='abc@example.com', password='testpass123')
        new_product = create_product(user=self.user)
        payload = {
            'user': new_user.id,
        }
        url = detail_url(new_product.id)
        self.client.patch(url, payload)

        new_product.refresh_from_db()
        self.assertEqual(new_product.user, self.user)
