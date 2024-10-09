from django.urls import path
from .views import (UserListCreateView, UserDetailView, ShopListCreateView, ShopDetailView, ShopkeeperListCreateView,
                    ShopkeeperDetailView, CustomerListCreateView, CustomerDetailView, ProductListCreateView,
                    ProductDetailView, ReviewListCreateView, ReviewDetailView, OrderListCreateView, OrderDetailView,
                    OrderItemListCreateView, OrderItemDetailView, RegisterView, BulkProductCreateDeleteView,
                    ProductSearchView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [

    # path('users/sign-up/', UserSignUpView.as_view(), name='user-signup'),
    # path('users/login/', UserLoginView.as_view(), name='user-login'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name="sign_up"),
    # User URLs
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Shop URLs
    path('shops/', ShopListCreateView.as_view(), name='shop-list-create'),
    path('shops/<int:pk>/', ShopDetailView.as_view(), name='shop-detail'),

    # Shopkeeper URLs
    path('shopkeepers/', ShopkeeperListCreateView.as_view(), name='shopkeeper-list-create'),
    path('shopkeepers/<int:pk>/', ShopkeeperDetailView.as_view(), name='shopkeeper-detail'),

    # Customer URLs
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),

    # Product URLs
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('bulk-products/', BulkProductCreateDeleteView.as_view(), name='bulk-product-create-delete'),

    # Review URLs
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),

    # Order URLs
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # OrderItem URLs
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
]