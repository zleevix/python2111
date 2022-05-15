from unicodedata import category
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineshop.settings')
django.setup()

from shop.models import Category, Product

products = Product.objects.filter(category__name='Điện Thoại')
category = Category.objects.get(name="Điện Thoại")
# Lấy đc category parent mà có chứa thằng đăng được filter
category.category_parent
print(products)