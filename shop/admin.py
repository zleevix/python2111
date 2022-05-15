from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Promotion, ProductReview

# Register your models here.
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_category_parent')
    
    @admin.display(description='Category Parent')
    def get_category_parent(self, obj):
        try:
            category_parent = obj.category_parent
            return category_parent.name
        except:
            return ''

class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'get_category', 'get_brand')
    inlines = [
        ProductImageInline,
    ]

    @admin.display(description='Category')
    def get_category(self, obj):
        try:
            return obj.category.name
        except:
            return ''

    @admin.display(description='Brand')
    def get_brand(self, obj):
        try:
            return obj.brand.name
        except:
            return ''

admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Promotion)
admin.site.register(ProductReview)
