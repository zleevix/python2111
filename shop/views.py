from itertools import product
from django.db.models import Min, Max, Sum
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http.response import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.template import Context
from django.conf import settings
from .models import Category, Brand, Product, Order, OrderDetail, Promotion
from .forms import RegisterForm

def register_user(request):
    register_form = RegisterForm() 
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save_user()
            return redirect('index')
    return render(
        request=request,
        template_name='user/register.html',
        context={
            'form': register_form
        }
    )

def login_user(request):
    message = ""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(
            username=username,
            password=password
        )
        if user: # Khác None
            # print("Xác thực thành công !")
            login(request=request, user=user)
            # print("Đăng nhập thành công")
            next_page = request.GET.get('next')
            if next_page:
                return HttpResponseRedirect(next_page)
            return redirect('index')
        else:
            print("Username/password không đúng")
            message="Thông tin bạn cung cấp không khớp. Vui lòng kiểm tra lại"
    return render(
        request=request,
        template_name='user/login.html',
        context={
            'message': message
        }
    )
    
# Create your views here.
def index(request):
    # Hiển thị category của trang chủ là các Category parent = parent_id là Null
    categories = Category.objects.filter(category_parent__isnull=True)
    brands = Brand.objects.all()
    minimun_price = Product.objects.all().aggregate(Min('price'))
    maximun_price = Product.objects.all().aggregate(Max('price'))
    products = Product.objects.all()
    category_filter = request.GET.get('category')
    category_display = ''
    if category_filter:
        products = Product.objects.filter(category__name=category_filter)
        category_display = Category.objects.get(name=category_filter)
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = Product.objects.filter(brand__name=brand_filter)
    price_filter = request.GET.get('price')
    if price_filter:
        price_range = list(map(int,price_filter.split(',')))
        products = Product.objects.filter(price__range=price_range)
    name_filter = request.GET.get('name')
    if name_filter:
        products = Product.objects.filter(name__icontains=name_filter)
    return render(
        request=request,
        template_name='index.html',
        context={
            'categories': categories,
            'brands': brands,
            'minimun_price':minimun_price,
            'maximun_price':maximun_price,
            'products': products,
            'category_display': category_display
        }
    )


def view_product_detail(request, product_id):
    categories = Category.objects.filter(category_parent__isnull=True)
    brands = Brand.objects.all()
    minimun_price = Product.objects.all().aggregate(Min('price'))
    maximun_price = Product.objects.all().aggregate(Max('price'))
    product = Product.objects.get(id=product_id)
    return render(
        request=request,
        template_name='product-details.html',
        context={
            'product': product,
            'categories': categories,
            'brands': brands,
            'minimun_price':minimun_price,
            'maximun_price':maximun_price,
        }
    )

@login_required(login_url='/login')
def add_product_to_cart(request, product_id):
    # Cần phải biết được user nào đang logged
    logged_user = request.user # Lấy user đang logged
    # Kiểm tra `logged_user` có Order với status đang = 0 hay chưa ?
    product_data = Product.objects.get(id=product_id)
    try:
        product_promotion = Promotion.objects.get(product=product_data, start_date__lte=now(), end_date__gt=now())
        product_price_discount = int(product_promotion.product.price * (100 - product_promotion.discount)/100)
    except Promotion.DoesNotExist:
        product_price_discount = product_data.price
    try:
        # Trong try là đã có Order với status 0
        user_ordered = Order.objects.get(user=logged_user, status=0)
        # Kiểm tra sản phẩm product_id có tồn tại trong OrderDetail của order user
        try:
            # Trong order của người dùng hiện tại, kiểm tra orderDetail xem đã tồn tại sản phẩm đó chưa
            data_orderdetail = OrderDetail.objects.get(order=user_ordered, product=product_data)
            # print("Người dùng mua trùng sản phẩm")
            # Tăng quantity lên
            data_orderdetail.quantity += 1
            data_orderdetail.amount = data_orderdetail.quantity * product_price_discount
            data_orderdetail.save()
        except OrderDetail.DoesNotExist:
            # print("Người dùng mua sản phẩm khác")
            # Thêm vào OrderDetail
            OrderDetail.objects.create(
                order=user_ordered,
                product=product_data,
                quantity=1,
                amount=product_price_discount*1
            )
    except Order.DoesNotExist:
        # Logged_user chưa có sản phẩm nào trong giỏ hàng
        # Hoặc là logged_user có sản phẩm nhưng Order status = 1
        # Thêm vào Order vơi status = 0và OrderDetail
        order_created = Order.objects.create(
            user=logged_user, 
            create_date=now(), 
            total_amount=0,
            status=0
        )
        OrderDetail.objects.create(
            order=order_created,
            product=product_data,
            quantity=1,
            amount=product_price_discount*1
        )
    
    user_ordered = Order.objects.get(user=logged_user, status=0)
    count_quantity = sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    return JsonResponse({"data": count_quantity})

    # return redirect('index')

@login_required(login_url='/login')
def change_product_quantity(request,  product_id, action):
    # localhost:8000/<id>/increase
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    user_ordered = Order.objects.get(user=logged_user, status=0)
    orderdetail_change = user_ordered.orderdetail_set.get(product=product_data)
    if action == "increase":
        orderdetail_change.quantity += 1
        orderdetail_change.amount = int(orderdetail_change.quantity) * int(product_data.price)
        orderdetail_change.save()
    else:
        if orderdetail_change.quantity == 1:
            orderdetail_change.delete()
        else:
            orderdetail_change.quantity -= 1
            orderdetail_change.amount = int(orderdetail_change.quantity) * int(product_data.price)
            orderdetail_change.save()
    return redirect('show_cart')

@login_required(login_url='/login')
def remove_product_in_cart(request, product_id):
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    user_ordered = Order.objects.get(user=logged_user, status=0)
    orderdetail_change = user_ordered.orderdetail_set.get(product=product_data)
    orderdetail_change.delete()
    return redirect('show_cart')


@login_required(login_url='/login')
def show_cart(request):
    logged_user = request.user
    total_amount = {
        'amount__sum': 0
    }
    try:
        user_ordered = Order.objects.get(user=logged_user, status=0)
        total_amount = user_ordered.orderdetail_set.all().aggregate(Sum('amount'))
        print(total_amount['amount__sum'])
    except Order.DoesNotExist:
        user_ordered = None
    return render(
        request=request,
        template_name='cart.html',
        context={
            'user_ordered': user_ordered,
            'total_amount': total_amount['amount__sum']
        }
    )
    
@login_required(login_url='/login')
def confirm_checkout(request):
    logged_user = request.user
    total_amount = {
        'amount__sum': 0
    }
    try:
        user_ordered = Order.objects.get(user=logged_user, status=0)
        total_amount = user_ordered.orderdetail_set.all().aggregate(Sum('amount'))
        print(total_amount['amount__sum'])
    except Order.DoesNotExist:
        user_ordered = None
    return render(
        request=request,
        template_name='confirm_checkout.html',
        context={
            'user_ordered': user_ordered,
            'total_amount': total_amount['amount__sum']
        }
    )

@login_required(login_url='/login')
def checkout(request):
    if request.method == "POST":
        logged_user = request.user
        phone = request.POST['phone']
        address = request.POST['address']
        try:
            user_ordered = Order.objects.get(user=logged_user, status=0)
            total_amount = user_ordered.orderdetail_set.all().aggregate(Sum('amount'))
            # Giảm tồn kho stock_quantity của từng sản phẩm.
            for orderdetail in user_ordered.orderdetail_set.all():
                orderdetail.product.stock_quantity -= orderdetail.quantity
                orderdetail.product.save()
            user_ordered.total_amount = total_amount['amount__sum']
            user_ordered.phone = phone
            user_ordered.address = address
            user_ordered.status = 1
            user_ordered.save()
            subject = 'Thanks for you checkout'
            html_message = render_to_string('common/email_checkout.html', {'user_ordered': user_ordered})
            plain_message = strip_tags(html_message)
            message = f'''Hi {logged_user.username}, thank you for checkout at onlineshop.
    Here is detail your order: 
{plain_message}


    Total: {total_amount['amount__sum']}
    Thanks,
    onlineshop admin'''
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [logged_user.email, ]
            send_mail( subject, message, email_from, recipient_list )
        except Order.DoesNotExist:
            user_ordered = None
        except BaseException as e:
            print(e)
    return redirect('index')
# Logic thêm sản phẩm vào giỏ hàng
# Giỏ hàng thì có liên quan đến 2 bảng: Order và OrderDetail
# Người dùng bắt buộc phải đăng nhập.

# Trường hợp 1: Người dùng đã login, trong giỏ hàng hiện tại là không sản phẩm nào.
# Giả sử: người dùng mua cái iPhone 13 Pro Max, mã sp 1
# bấm `Add to cart` của sản phẩm có id=1
# Order 
# id    user_id             ngày mua    tổng tiền       status # 0: chưa hoàn thành, 1: hoàn thành
# 1     1 (logged user)     29/4 19:50  0               0 # chưa hoàn thành.

# OrderDetail
# id    order_id        product_id      quantity        amount
# 1     1               1               1               quantity* product_price

# Trường hợp 2: người dùng đã login, giỏ hàng hiện tại đang có sản phẩm trong 1 đơn hàng chưa thành công
    # Trường hợp 2.1: Sản phẩm mới thêm vào, giả sử Samsung S22 Ultra (không trùng với sản phẩm có trước đó trong giỏ hàng)
    # Samsung S22 Ultra, mã sp là 2
# Kiẽm tra id = 1 có trùng với product_id trong order hay không ?
# Order 
# id    user_id             ngày mua    tổng tiền       status # 0: chưa hoàn thành, 1: hoàn thành
# 1     1 (logged user)     29/4 19:50  0               0 # chưa hoàn thành.
# OrderDetail
# id    order_id        product_id      quantity        amount
# 1     1               1               1               quantity* product_price
# 2     1               2               1               quantity* product_price


    # Trường hợp 2.2: Sản phẩm mới thêm vào, giả sử iPhone 13 Pro Max (trùng với sản phẩm có trước đó trong giỏ hàng)
    # iPhone 13 Pro Max, mã sp 1
# Order 
# id    user_id             ngày mua    tổng tiền       status # 0: chưa hoàn thành, 1: hoàn thành
# 1     1 (logged user)     29/4 19:50  0               0 # chưa hoàn thành.

# Kiẽm tra id = 1 có trùng với product_id trong order hay không ?
# OrderDetail
# id    order_id        product_id      quantity        amount
# 1     1               1               2               quantity* product_price
# 2     1               2               1               quantity* product_price