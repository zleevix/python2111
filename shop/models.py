from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
# Project cuối khóa
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    category_parent = models.ForeignKey('self', blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"

class Brand(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Brand"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    stock_quantity = models.IntegerField()
    image = models.CharField(max_length=100)
    detail = models.TextField()
    status = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Product"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_path = models.TextField()

    class Meta:
        db_table = "ProductImage"

    def __str__(self):
        return f"{self.product.name}:{self.image_path}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    score = models.FloatField()
    class Meta:
        db_table = "ProductReview"

class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    discount = models.IntegerField()
    class Meta:
        db_table = "Promotion"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateField(default=timezone.now)
    total_amount = models.IntegerField(null=True)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    status = models.IntegerField(default=0)
    class Meta:
        db_table = "Order"

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    amount = models.IntegerField()

    class Meta:
        db_table = "OrderDetail"