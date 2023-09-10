import json
from .models import *
from random import randint


def cookieCart(request):
    try:
        cart = eval(request.COOKIES['cart'])  # getting cokkies
    except:
        cart = {}
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items']
    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'max_quantity': product.max_quantity,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }
            items.append(item)
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except:
            customer = Customer.objects.create(user=request.user,
                                               name=request.user.first_name + " " + request.user.last_name,
                                               email=request.user.email)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        customer_phone_number = customer.phone_number
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        customer_phone_number = None

    return {'cartItems': cartItems, 'order': order, 'items': items, 'customer_phone_number': customer_phone_number}


def guestOrder(request, data):
    print('User is not logged in')

    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(email=email, name="guest" + str(randint(100000, 999999)))
    customer.name = name + "-guest"
    customer.phone_number = data['customer']
    customer.save()

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])

    return customer, order
