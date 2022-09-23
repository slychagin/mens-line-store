from django.contrib import admin
from orders.models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'is_ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email')
    list_per_page = 20
    list_max_show_all = 100
    inlines = [OrderProductInline]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'amount_paid', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('payment_id', 'amount_paid')
    list_per_page = 20
    list_max_show_all = 100


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
