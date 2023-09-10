from .models import *
from django.http import JsonResponse
import datetime
from .utils import cartData, guestOrder
from .models import Product, Token
from django.shortcuts import render, redirect
from django.utils import timezone
import json


def profile(request):
    Data = cartData(request)
    cartItems = Data['cartItems']

    user = request.user
    if user.is_superuser:
            return redirect('Auth_site')

    try:
        customer = Customer.objects.get(user=user)
        orders = Order.objects.filter(customer=customer)
    except:
        customer = Customer.objects.get(user=user)
        orders = []

    if request.POST.get('first_name') != None or request.POST.get('last_name') != None or request.POST.get('email')!= None:
        customer = Customer.objects.get(user=user)
        customer.name = request.POST.get('first_name') + " " + request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.phone_number = request.POST.get('phone_number')
        customer.save()
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

    context = {'orders': orders, 'user': user, 'cartItems': cartItems, 'customer': customer}

    respond = render(request, 'store/profile.html', context)

    return respond


def store(request):
    Data = cartData(request)
    cartItems = Data['cartItems']
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {"products": products, 'cartItems': cartItems, 'categories': categories}

    respond = render(request, 'store/store.html', context)

    return respond


def search_products(request):
    Data = cartData(request)
    search_query = request.GET.get('search')  # Pobierz wpisane w polu Search dane

    products = Product.objects.filter(name__startswith=search_query)
    categories = Category.objects.all()
    cartItems = Data['cartItems']

    context = {'products': products, 'cartItems': cartItems, 'categories': categories}

    respond = render(request, 'store/store.html', context)

    return respond


def categories(request, category_name):
    Data = cartData(request)
    products = Product.objects.filter(category__name__startswith=category_name)
    categories = Category.objects.all()
    cartItems = Data['cartItems']

    context = {'products': products, 'cartItems': cartItems, 'categories': categories}

    respond = render(request, 'store/store.html', context)

    return respond


def subcategories(request, category_name, subcategory_name):
    Data = cartData(request)

    products = Product.objects.filter(subcategory__name__startswith=subcategory_name)
    categories = Category.objects.all()

    cartItems = Data['cartItems']

    context = {'products': products, 'cartItems': cartItems, 'categories': categories}

    respond = render(request, 'store/store.html', context)

    return respond


def view_product(request, product_id):
    Data = cartData(request)

    cartItems = Data['cartItems']
    product = Product.objects.get(id=product_id)

    context = {'product': product, 'cartItems': cartItems}

    respond = render(request, 'store/view.html', context)

    return respond


def contact(request):
    Data = cartData(request)
    cartItems = Data['cartItems']

    context = {'cartItems': cartItems}

    respond = render(request, 'store/contact.html', context)

    return respond


def cart(request):
    Data = cartData(request)

    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']

    context = {"items": items, "order": order, 'cartItems': cartItems}

    respond = render(request, 'store/cart.html', context)

    return respond


def updadeItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add' and orderItem.quantity < product.max_quantity:
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def checkout(request):
    Data = cartData(request)

    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']

    context = {"items": items, "order": order, 'cartItems': cartItems, 'customer_phone_number': Data['customer_phone_number']}

    respond = render(request, 'store/checkout.html', context)

    return respond


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        customer.phone_number = data['customer']
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        country=data['shipping']['country'],
        zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Payment completed', safe=False)


def check_quantity(request):
    result = True
    trouble_items = []
    if request.method == 'POST':
        data = json.loads(request.body)

        if request.user.is_authenticated:
            customer = request.user.customer
            customer.phone_number = data['customer']
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        for item in order.orderitem_set.all():
            product = Product.objects.get(id=item.product.id)
            if item.quantity > product.max_quantity:
                result = False  # Zakładając, że change_quantity jest
                trouble_items.append(item.product.name)
        if result:
            for item in order.orderitem_set.all():
                product = Product.objects.get(id=item.product.id)
                product.max_quantity -= item.quantity
                product.save()

    return JsonResponse({'result': result, 'trouble_items': trouble_items})


def Auth_site(request):
    allegro_token, created = Token.objects.get_or_create(name="allegro")
    olx_token, created = Token.objects.get_or_create(name="olx")
    print(allegro_token.authorized)
    return render(request, 'store/authorization.html', {'allegro_authorized': allegro_token.authorized,
                                                        'olx_authorized': olx_token.authorized})
