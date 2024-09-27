from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Custom User Manager
class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)


# Abstract User Model
class User(AbstractBaseUser):
    ADMIN = 'admin'
    SHOPKEEPER = 'shopkeeper'
    CUSTOMER = 'customer'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (SHOPKEEPER, 'Shopkeeper'),
        (CUSTOMER, 'Customer'),
    ]

    username = None
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


# Shop Model
class Shop(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    owner = models.ForeignKey('Shopkeeper', on_delete=models.SET_NULL, null=True, related_name='owned_shops')
    shopkeepers = models.ManyToManyField('Shopkeeper', related_name='assigned_shop', through='ShopAssignment')
    status = models.CharField(max_length=50,
                              choices=[('active', 'Active'), ('pending', 'Pending'), ('deleted', 'Deleted')])

    def __str__(self):
        return self.name


# Shopkeeper Model
class Shopkeeper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    TIN = models.CharField(max_length=100)
    NID = models.CharField(max_length=100)
    approval_status = models.CharField(max_length=50,
                                       choices=[('pending', 'Pending'), ('approved', 'Approved') ,('rejected', 'Rejected')])
    def __str__(self):
        return self.user.name


# New Model to ensure each shopkeeper can be assigned to one shop only
class ShopAssignment(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    shopkeeper = models.OneToOneField(Shopkeeper, on_delete=models.CASCADE)  # Enforces one shopkeeper per shop
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shopkeeper} -> {self.shop}"


# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=50,
                                       choices=[('pending', 'Pending'), ('approved', 'Approved') ,('rejected', 'Rejected')])

    def __str__(self):
        return self.user.name


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    added_by = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Review Model
class Review(models.Model):
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rating} by {self.customer.user.name}"


# Order Model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50,
                              choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'),
                                       ('shipped', 'Shipped'), ('delivered', 'Delivered')])
    def __str__(self):
        return f"Order {self.id} by {self.customer.user.name}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"