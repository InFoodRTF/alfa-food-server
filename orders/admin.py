from datetime import datetime

from django.contrib import admin

from django.contrib.admin import ModelAdmin, DateFieldListFilter
from django.forms import CheckboxInput
from rangefilter.filters import DateRangeFilterBuilder, DateTimeRangeFilterBuilder, NumericRangeFilterBuilder

# from orders.models import Product, Order, OrderItem, Menu, MenuItem, Cart, CartItem
from django.db import models

from classes.models.student import Student
from orders.models.cart import CartItem, Cart
from orders.models.menu import MenuItem, Menu
from orders.models.order import OrderItem, Order
from orders.models.product import Product


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass


# @admin.register(OrderItem)
class OrderItemAdmin(admin.StackedInline):
    # pass
    model = OrderItem


admin.site.register(OrderItem)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderItemAdmin]


# @admin.register(MenuItem)
class MenuItemAdmin(admin.StackedInline):
    # pass
    model = MenuItem


admin.site.register(MenuItem)


@admin.register(Menu)
class MenuAdmin(ModelAdmin):
    inlines = [MenuItemAdmin]
    formfield_overrides = {
        models.BooleanField: {'widget': CheckboxInput(attrs={'style': 'width:20px;height:20px;'})}
    }
    list_display = ('name', 'date_implementation', 'created', 'active')
    # list_filter = ('active', )
    # list_filter = (
    #         ('date_implementation', DateFieldListFilter),
    #         'active'
    # )
    list_filter = (
        ("created", DateRangeFilterBuilder()),
        ("date_implementation", DateRangeFilterBuilder(title="Дата реализации")),

        # (
        #     "updated",
        #     DateTimeRangeFilterBuilder(
        #         title="Custom title",
        #         default_start=datetime(2020, 1, 1),
        #         default_end=datetime(2030, 1, 1),
        #     ),
        # ),
        # ("num_value", NumericRangeFilterBuilder()),
    )



class CartItemAdmin(admin.StackedInline):
    # pass
    model = CartItem


admin.site.register(CartItem)


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    inlines = [CartItemAdmin]

    list_display = ('customer', 'student')
    # list_editable = ('quantity',)
    # list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('customer', 'student')

    # def queryset(self, request):
    #     qs = super(CartAdmin, self).queryset(request)
    #     qs.student.queryset =

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):

        try:
            context['adminform'].form.fields['student'].queryset = Student.objects.filter(parent_id=obj.customer.pk)
        except:
            pass
        # context['adminform'].form.fields['product'].queryset = MenuItem.objects.filter(parent_id=obj.customer.pk)

        return super(CartAdmin, self).render_change_form(request, context)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "student":
    #         kwargs["queryset"] = Student.objects.filter(parent_id=4)
    #     return super(CartAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     # remove null choice
    #     form.base_fields["student"].queryset = Student.objects.filter(parent_id=obj.customer.pk)
    #     return form
