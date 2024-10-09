from decimal import Decimal, InvalidOperation

from django.db import IntegrityError
from rest_framework import serializers
from .models import User, Shopkeeper, Customer, Shop, Product, Review, Order, OrderItem, ShopAssignment


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "password"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the User
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        # Automatically create Shopkeeper or Customer based on role
        role = validated_data['role']
        if role == User.SHOPKEEPER:
            Shopkeeper.objects.create(user=user)
        elif role == User.CUSTOMER:
            Customer.objects.create(user=user)

        return user


class ShopkeeperSerializer(serializers.ModelSerializer):
    # Accept email directly instead of the entire user object
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Shopkeeper
        fields = ['id', 'email', 'TIN', 'NID', 'approval_status']

    def create(self, validated_data):
        # Extract the email from the validate data
        email = validated_data.pop('email')

        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "A user with this email does not exist."})

        # Now try to create the Shopkeeper using the found user
        try:
            shopkeeper = Shopkeeper.objects.create(user=user, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"user": "This user is already associated with a shopkeeper."})

        # Now create the Shopkeeper using the found user
        #shopkeeper = Shopkeeper.objects.create(user=user, **validated_data)

        return shopkeeper

    def update(self, instance, validated_data):
        # Handle the email field separately
        email = validated_data.pop('email', None)

        # If email is provided, ensure the associated user exists
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "A user with this email does not exist."})
            instance.user = user

        # Update the remaining fields
        instance.TIN = validated_data.get('TIN', instance.TIN)
        instance.NID = validated_data.get('NID', instance.NID)
        instance.approval_status = validated_data.get('approval_status', instance.approval_status)

        # Save the updated instance
        instance.save()

        return instance

    # def create(self, validated_data):
    #     user_data = validated_data.pop('user')
    #     user = User.objects.create_user(**user_data)
    #     shopkeeper = Shopkeeper(**validated_data)
    #     shopkeeper.user = user
    #     shopkeeper.save()
    #     return shopkeeper


class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'email', 'approval_status']

    def create(self, validated_data):
        email = validated_data.pop('email')

        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "A user with this email does not exist."})

        # Now try to create the Customer using the found user
        try:
            customer = Customer.objects.create(user=user, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"user": "This user is already associated with a Customer."})

        # Now create the Shopkeeper using the found user
        # shopkeeper = Shopkeeper.objects.create(user=user, **validated_data)

        return customer

    def update(self, instance, validated_data):
        # Handle the email field separately
        email = validated_data.pop('email', None)

        # If email is provided, ensure the associated user exists
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "A user with this email does not exist."})
            instance.user = user

        # Update the remaining fields
        instance.approval_status = validated_data.get('approval_status', instance.approval_status)

        # Save the updated instance
        instance.save()

        return instance


class ShopAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAssignment
        fields =['shop', 'shopkeeper', 'assigned_at']


class ShopSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Shopkeeper.objects.all())
    shopkeepers = ShopAssignmentSerializer(source='shopassignment_set', many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'address', 'owner', 'status', 'shopkeepers']


class ProductSerializer(serializers.ModelSerializer):
    added_by = ShopkeeperSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'shop', 'shop_name', 'added_by']

    def validate_price(self, value):
        # If the price is sent as a string, try converting it to a Decimal
        if isinstance(value, str):
            try:
                value = Decimal(value)
            except InvalidOperation:
                raise serializers.ValidationError("Invalid price format. Please provide a valid decimal.")
        # Ensure the price is a positive number
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def create(self, validated_data):
        # Assign the shopkeeper to the product
        request = self.context.get('request')
        shopkeeper = Shopkeeper.objects.get(user=request.user)
        product = Product.objects.create(added_by=shopkeeper, **validated_data)
        return product


class ProductSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    shop_name = serializers.CharField(required=False)

    def validate(self, data):
        min_price = data.get('min_price')
        max_price = data.get('max_price')

        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError("min_price cannot be greater than max_price.")
        return data


class ReviewSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'product', 'customer']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'shop', 'total_price', 'status']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    order = OrderSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']
