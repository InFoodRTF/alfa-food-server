from django.contrib import admin

from django.contrib.admin import ModelAdmin

from orders.models import Product, Order, OrderItem


@admin.register(Product)
class ProfileAdmin(ModelAdmin):
    pass


@admin.register(Order)
class ProfileAdmin(ModelAdmin):
    pass


@admin.register(OrderItem)
class ProfileAdmin(ModelAdmin):
    pass

