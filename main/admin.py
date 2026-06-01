from django.contrib import admin  # type: ignore[reportMissingModuleSource]
from .models import Product, Profile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'author', 'volume', 'is_new', 'rating')
    list_filter = ('category', 'is_new')
    search_fields = ('name', 'author')
    list_editable = ('price', 'is_new', 'rating')

admin.site.register(Profile)