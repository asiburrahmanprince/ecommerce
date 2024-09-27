from django.contrib import admin
from .models import User, Shopkeeper, Customer, Shop, Product, Review, Order, OrderItem


admin.site.register(User)
admin.site.register(Shopkeeper)
admin.site.register(Customer)
admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)