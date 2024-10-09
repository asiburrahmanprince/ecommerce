from re import search
from django.db import connection
from django.db.models import Q

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (User, Shop, Shopkeeper, Customer,
                     Product, Review, Order, OrderItem, ShopAssignment)

from .serializers import (UserSerializer, ShopSerializer, ShopkeeperSerializer, CustomerSerializer,
                          ProductSerializer, ReviewSerializer, OrderSerializer, OrderItemSerializer,
                          ProductSearchSerializer)

class RegisterView(APIView):

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserListCreateView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"error": "User not found"},status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ShopListCreateView(APIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shops = Shop.objects.all()
        serializer = ShopSerializer(shops, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ShopSerializer)
    def post(self, request):
        shop_serializer = ShopSerializer(data=request.data)
        if shop_serializer.is_valid():
            shop = shop_serializer.save()

            # Handle shopkeeper assignment
            shopkeeper_id = request.data.get('shopkeeper_id')
            if shopkeeper_id:
                try:
                    shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
                except Shopkeeper.DoesNotExist:
                    return Response({"error": "Shopkeeper not found"},status=status.HTTP_404_NOT_FOUND)


                # Check if the shopkeeper is already assigned to a shop
                if ShopAssignment.objects.filter(shopkeeper=shopkeeper).exists():
                    return Response({"error": "This shopkeeper is already assigned to another shop."},status=status.HTTP_400_BAD_REQUEST)

                # Assign the shopkeeper to a new shop
                ShopAssignment.objects.create(shop=shop, shopkeeper=shopkeeper)
            return Response(shop_serializer.data, status=status.HTTP_201_CREATED)
        return Response(shop_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShopDetailView(APIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            return None

    def get(self, request, pk):
        shop = self.get_object(pk)
        if shop is None:
            return Response({"error": "Shop not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ShopSerializer)
    def put(self, request, pk):
        shop = self.get_object(pk)
        shop_serializer = ShopSerializer(shop, data=request.data, partial=True)
        if shop_serializer.is_valid():
            shop = shop_serializer.save()

            # Handle shopkeeper assignment updates
            shopkeeper_ids = request.data.get('shopkeeper_ids', [])
            ShopAssignment.objects.filter(shop=shop).delete()  # Clear existing shopkeepers

            for shopkeeper_id in shopkeeper_ids:
                try:
                    shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
                    ShopAssignment.objects.create(shop=shop, shopkeeper=shopkeeper)
                except Shopkeeper.DoesNotExist:
                    return Response({"error": f"Shopkeeper with ID {shopkeeper_id} does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response(shop_serializer.data, status=status.HTTP_200_OK)
        return Response(shop_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        shop = self.get_object(pk)
        if shop is None:
            return Response({"error": "Shop not found"},status=status.HTTP_404_NOT_FOUND)
        shop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ShopkeeperListCreateView(APIView):
    serializer_class = ShopkeeperSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shopkeepers = Shopkeeper.objects.all()
        serializer = ShopkeeperSerializer(shopkeepers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ShopkeeperSerializer)
    def post(self, request):
        serializer = ShopkeeperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShopkeeperDetailView(APIView):
    serializer_class = ShopkeeperSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Shopkeeper.objects.get(pk=pk)
        except Shopkeeper.DoesNotExist:
            return None

    def get(self, request, pk):
        shopkeeper = self.get_object(pk)
        if shopkeeper is None:
            return Response({"error": "Shopkeeper not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ShopkeeperSerializer(shopkeeper)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ShopkeeperSerializer)
    def put(self, request, pk):
        shopkeeper = self.get_object(pk)
        if shopkeeper is None:
            return Response({"error": "Shopkeeper not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ShopkeeperSerializer(shopkeeper, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shopkeeper = self.get_object(pk)
        if shopkeeper is None:
            return Response({"error": "Shopkeeper not found"},status=status.HTTP_404_NOT_FOUND)
        shopkeeper.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerListCreateView(APIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CustomerSerializer)
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetailView(APIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return None

    def get(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({"error": "Customer not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CustomerSerializer)
    def put(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({"error": "Customer not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({"error": "Customer not found"},status=status.HTTP_404_NOT_FOUND)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductSearchView(APIView):
    def get(selfself, request):
        search_serializer = ProductSearchSerializer(data=request.query_params)
        if search_serializer.is_valid():
            name = search_serializer.validated_data.get('name')
            description = search_serializer.validated_data.get('description')
            min_price = search_serializer.validated_data.get('min_price')
            max_price = search_serializer.validated_data.get('max_price')
            shop_name = search_serializer.validated_data.get('shop_name')

            query = Q()
            if name:
                query &= Q(name__icontains=name)
            if description:
                query &= Q(description__icontains=description)
            if min_price:
                query &= Q(price__gte=min_price)
            if max_price:
                query &= Q(price__lte=max_price)
            if shop_name:
                query &= Q(shop__name__icontains=shop_name)

            products = Product.objects.filter(query)
            products_serializer = ProductSerializer(products, many=True)

            # Log number of queries made during this view execution
            num_queries = len(connection.queries)
            print(f"Number of queries executed: {num_queries}")

            return Response(products_serializer.data, status=status.HTTP_200_OK)

        return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListCreateView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProductSerializer)
    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BulkProductCreateDeleteView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Bulk Product Creation
    @swagger_auto_schema(request_body=ProductSerializer(many=True))
    def post(self, request):
        # Get the shopkeeper linked to the user
        try:
            shopkeeper = Shopkeeper.objects.get(user=request.user)
        except Shopkeeper.DoesNotExist:
            return Response({'error': 'Shopkeeper not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare products data
        products_data = request.data

        # Pass the request context to the serializer to access the current user
        serializer = ProductSerializer(data=products_data, many=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Define the expected request body for bulk delete
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
            },
            required=['ids']
        )
    )
    # Bulk Product Deletion
    def delete(self, request):
        product_ids = request.data.get('ids', [])
        if not product_ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete products by their IDs
        Product.objects.filter(id__in=product_ids).delete()
        return Response({"message": "Products deleted successfully"},status=status.HTTP_204_NO_CONTENT)

class ProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProductSerializer)
    def put(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response({"error": "Product not found"},status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ReviewSerializer)
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_object(pk)
        if review is None:
            return Response({"error": "Review not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ReviewSerializer)
    def put(self, request, pk):
        review = self.get_object(pk)
        if review is None:
            return Response({"error": "Review not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if review is None:
            return Response({"error": "Review not found"},status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderSerializer)
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderSerializer)
    def put(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderItemListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        order_items = OrderItem.objects.all()
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderItemSerializer)
    def post(self, request, pk):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return None

    def get(self, request, pk):
        order_item = self.get_object(pk)
        if order_item is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderItemSerializer)
    def put(self, request, pk):
        order_item = self.get_object(pk)
        if order_item is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order_item = self.get_object(pk)
        if order_item is None:
            return Response({"error": "Order not found"},status=status.HTTP_404_NOT_FOUND)
        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
