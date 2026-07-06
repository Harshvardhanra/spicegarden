from django.contrib import admin
from .models import Category, MenuItem, Table, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'sort_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'food_type', 'is_bestseller', 'is_new', 'is_available']
    list_filter = ['category', 'food_type', 'is_available', 'is_bestseller']
    list_editable = ['price', 'is_available']
    search_fields = ['name']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'status']
    list_editable = ['status']
    actions = ['generate_qr_codes']

    def generate_qr_codes(self, request, queryset):
        for table in queryset:
            table.generate_qr()
            table.save()
        self.message_user(request, f'QR codes generated for {queryset.count()} tables.')
    generate_qr_codes.short_description = 'Generate QR Codes'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['item_name', 'item_price', 'quantity', 'line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'table', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'created_at', 'updated_at']
