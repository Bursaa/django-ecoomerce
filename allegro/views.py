from .platform_senders import *
from .forms import MyForm
from django.shortcuts import render, redirect
from store.models import Product, Token
from django.http import HttpResponse


def Auth(request):
    return get_auth_code()


def Auth_callback(request):
    allegro_token, created = Token.objects.get_or_create(name="allegro")
    if not allegro_token.authorized:
        code = request.GET.get('code')
        result = get_access_token(code)

        if isinstance(result, HttpResponse):
            res = HttpResponse(result)
            res['Refresh'] = '5;url=/Auth_site/'
            return res
        else:
            return redirect('Auth_site')
    else:
        return redirect('Auth_site')


def callback(request, product_id, action):

    product = Product.objects.get(id=product_id)
    try:
        id_cat = product.subcategory.allegro_id
    except:
        id_cat = product.category.allegro_id

    is_leaf = is_category_leaf(id_cat)

    if isinstance(is_leaf, HttpResponse):
        res = HttpResponse(is_leaf)
        res['Refresh'] = '5;url=/admin/store/product'
        return res
    elif not is_leaf:
        res = HttpResponse("Nie można dodać produktu w tej kategorii - kategoria nie jest lisciem")
        res['Refresh'] = '5;url=/admin/store/product'
        return res
    elif is_leaf:
        request.session['product_id'] = product_id

        if action == 'add':
            result = get_required_parameters(id_cat)

            if isinstance(result, HttpResponse):
                res = HttpResponse(result)
                res['Refresh'] = '5;url=/admin/store/product'
                return res
            else:
                product_params, offer_params = result

            request.session['product_params'] = product_params
            request.session['offer_params'] = offer_params

            return redirect("/allegro/get_form")
        elif action == 'delete':
            return redirect("/allegro/end_offer")
        elif action == 'change':
            return redirect("/allegro/change_offer")


def get_form(request):
    product_params = request.session.get('product_params')
    offer_params = request.session.get('offer_params')
    if request.method == 'POST':
        product_form = MyForm(request.POST, form_data=product_params)
        offer_form = MyForm(request.POST, form_data=offer_params)
        if product_form.is_valid() and offer_form.is_valid():
            allegro_params_product = []
            allegro_params_offer = []
            for name, value in product_form.fields.items():
                allegro_params_product.append({'name': name, 'values': [str(product_form.cleaned_data[name])]})
            for name, value in offer_form.fields.items():
                allegro_params_offer.append({'name': name, 'values': [str(offer_form.cleaned_data[name])]})
            request.session['product_params'] = allegro_params_product
            request.session['offer_params'] = allegro_params_offer
            return redirect("/allegro/create_offer/")
        else:
            return render(request, 'allegro/allegro_form.html', {'product_form': product_form, 'offer_form': offer_form})
    else:
        product_form = MyForm(form_data=product_params)
        offer_form = MyForm(form_data=offer_params)
        return render(request, 'allegro/allegro_form.html', {'product_form': product_form, 'offer_form': offer_form})


def create_offer(request):
    product_params = request.session.get('product_params')
    offer_params = request.session.get('offer_params')
    prod_id = request.session.get('product_id')
    product = Product.objects.get(id=prod_id)

    try:
        id_cat = product.subcategory.allegro_id
    except:
        id_cat = product.category.allegro_id

    try:
        allegro_token = Token.objects.get(name="allegro")
        token = allegro_token.access_token
        url = ENV_URL + "sale/product-offers"
        headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json",
                   'Content-Type': 'application/vnd.allegro.public.v1+json'}

        product_data = {
            "productSet": [{
                "product": {
                    "name": str(product.name),
                    "description": str(product.description),
                    "category": {
                        "id": str(id_cat)
                    },
                    "parameters": product_params,
                    "images": [
                        "https://picsum.photos/200/300"
                    ]
                }
            }],
            "parameters": offer_params,
            "sellingMode": {
                "price": {
                    "amount": str(product.price),
                    "currency": "PLN"
                }
            },
            "stock": {
                "available": product.max_quantity,
            }
        }
        result = requests.post(url, headers=headers, json=product_data, verify=True, allow_redirects=True)
        if result.status_code == 201 or result.status_code == 202:
            product_data = result.json()
            product.allegro_offer_id = str(product_data['id'])
            product.save()
            return redirect("/admin/store/product")
        else:
            response = HttpResponse(result)
            response['Refresh'] = '5;url=/admin/store/product'
            return response

    except requests.exceptions.HTTPError as err:
        res = HttpResponse(err)
        res['Refresh'] = '5;url=/admin/store/product'
        return res


def end_offer(request):
    allegro_token = Token.objects.get(name="allegro")
    token = allegro_token.access_token
    prod_id = request.session.get('product_id')
    product = Product.objects.get(id=prod_id)
    offers_url = ENV_URL + "sale/offers"
    headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json",
               'Content-Type': 'application/vnd.allegro.public.v1+json'}
    response = requests.get(offers_url, headers=headers)

    if response.status_code == 200:
        offers_data = response.json()
        desired_offer = None

        for offer in offers_data['offers']:
            if str(product.allegro_offer_id) in offer['id']:
                desired_offer = offer

        if desired_offer:
            product_id = desired_offer['id']
            end_product_url = ENV_URL + "sale/product-offers/" + str(product_id)
            data = {
                "publication": {"status": "ENDED"},
            }
            response = requests.patch(end_product_url, headers=headers, json=data, verify=False)
            if response.status_code == 202 or response.status_code == 200:
                product.allegro_offer_id = 'not added'
                product.save()
                return redirect("/admin/store/product")
            else:
                res = HttpResponse(str(response.status_code) + str(response.text))
                res['Refresh'] = '5;url=/admin/store/product'
                return res
        else:
            res = HttpResponse("Product not found")
            res['Refresh'] = '5;url=/admin/store/product'
            return res
    else:
        res = HttpResponse(str(response.status_code) + str(response.text))
        res['Refresh'] = '5;url=/admin/store/product'
        return res


def change_offer(request):
    allegro_token = Token.objects.get(name="allegro")
    token = allegro_token.access_token
    prod_id = request.session.get('product_id')
    product = Product.objects.get(id=prod_id)
    offers_url = ENV_URL + "sale/offers"
    headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json",
               'Content-Type': 'application/vnd.allegro.public.v1+json'}
    response = requests.get(offers_url, headers=headers)

    if response.status_code == 200:
        offers_data = response.json()
        desired_offer = None

        for offer in offers_data['offers']:
            if str(product.allegro_offer_id) in offer['id']:
                desired_offer = offer

        if desired_offer:
            try:
                id_cat = product.subcategory.allegro_id
            except:
                id_cat = product.category.allegro_id

            product_id = desired_offer['id']
            change_product_url = ENV_URL + "sale/product-offers/" + str(product_id)
            product_data = {
                "productSet": [{
                    "product": {
                        "name": str(product.name),
                        "description": str(product.description),
                        "category": {
                            "id": str(id_cat)
                        },
                        "images": [
                            "https://picsum.photos/200/300"
                        ]
                    }
                }],
                "sellingMode": {
                    "price": {
                        "amount": str(product.price),
                        "currency": "PLN"
                    }
                },
                "stock": {
                    "available": product.max_quantity,
                }
            }
            response = requests.patch(change_product_url, headers=headers, json=product_data, verify=False)
            if response.status_code == 202 or response.status_code == 200:
                return redirect("/admin/store/product")
            else:
                res = HttpResponse(str(response.status_code) + str(response.text))
                res['Refresh'] = '5;url=/admin/store/product'
                return res
        else:
            res = HttpResponse("Product not found")
            res['Refresh'] = '5;url=/admin/store/product'
            return res
    else:
        res = HttpResponse(str(response.status_code) + str(response.text))
        res['Refresh'] = '5;url=/admin/store/product'
        return res
