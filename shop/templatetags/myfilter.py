
from math import prod
from django import template
from django.conf import settings
from django.utils.timezone import now
from shop.models import Category, Brand, Product, Promotion, Order

register = template.Library()

# Viết hàm kiểm tra category nó có category con hay không ?
@register.filter
def has_children(category_parent_id):
    children = Category.objects.filter(category_parent_id=category_parent_id)
    return len(children) > 0 # >0 thì có chilren

@register.filter
def get_first_image(product_images):
    return product_images[0].image_path

# Tạo được slide, mỗi lần hiển thị là 3 ảnh.
# Số ảnh của mỗi sản phẩm là số chia hết cho 3.
@register.filter
def make_product_slider(product_images):
    lst = []
    for i in range(0, len(product_images), 3):
        lst.append([product_images[i].image_path,product_images[i+1].image_path,product_images[i+2].image_path,])

@register.filter
def is_product_sale(product_id):
    product = Promotion.objects.filter(product_id=product_id, start_date__lte=now(), end_date__gt=now())
    return len(product) > 0

@register.filter
def get_discount_product(product_id):
    try:
        product_promotion = Promotion.objects.get(product_id=product_id, start_date__lte=now(), end_date__gt=now())
        return int(product_promotion.product.price * (100 - product_promotion.discount)/100)
    except Promotion.DoesNotExist:
        return Product.objects.get(id=product_id).price

@register.filter
def count_product_in_cart(logged_user):
    try:
        # Đếm số lượng sản phẩm trong order status=0
        user_ordered = Order.objects.get(user=logged_user, status=0)
        return sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    except:
        return 0