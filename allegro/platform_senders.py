import requests
import json
from django.utils import timezone
from django.shortcuts import redirect, HttpResponse
from store.models import Product, Token
import urllib3
import datetime
urllib3.disable_warnings()

# important settings for allegro configurations
CLIENT_ID = "4efb05ce175841a89b1aa2248dab4f51"  # wprowadź Client_ID aplikacji
CLIENT_SECRET = "pCQdmWikNutad9m5FFTAu6gVyTDcPj4N31OwUeWz9IhENqu8uVci8E4euKOYGoSA"  # wprowadź Client_Secret aplikacji
ENV_URL = "https://api.allegro.pl.allegrosandbox.pl/"
TOKEN_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"

REDIRECT_URI = "http://localhost:8000/allegro/Auth_callback"


def get_auth_code():
    allegro_auth_url = "https://allegro.pl.allegrosandbox.pl/auth/oauth/authorize?response_type=code&client_id=" \
                       + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI
    return redirect(allegro_auth_url)


def get_access_token(authorization_code):
    data = {'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': REDIRECT_URI}
    access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                          allow_redirects=False, auth=(CLIENT_ID, CLIENT_SECRET))
    try:
        tokens = json.loads(access_token_response.text)
        allegro_token, created = Token.objects.get_or_create(name="allegro")
        allegro_token.access_token = tokens['access_token']
        allegro_token.refresh_token = tokens['refresh_token']
        allegro_token.time_of_invalidation = timezone.now() + timezone.timedelta(seconds=int(tokens['expires_in']))
        allegro_token.authorized = True
        allegro_token.save()
        return tokens["access_token"]
    except requests.exceptions.HTTPError as err:
        response = HttpResponse(err)
        response['Refresh'] = '5;url=/Auth_site/'
        return response


def get_required_parameters(category_id):
    allegro_token = Token.objects.get(name="allegro")
    token = allegro_token.access_token
    to_form = {'product': [], 'offer': []}
    parameters_url = ENV_URL + "sale/categories/" + str(category_id) + "/parameters"
    headers = {'Authorization': 'Bearer ' + token,
               'Accept': "application/vnd.allegro.public.v1+json", 'Accept-Language': 'pl-PL'}

    response = requests.get(parameters_url, headers=headers, verify=False)
    try:
        parameters_dict = response.json()
        for parameter in parameters_dict['parameters']:
            if parameter['required']:
                param = {'name': parameter['name'], 'type': parameter['type'], 'values': [],
                         'restrictions': {'min': None, 'max': None}}
                if parameter['options']['describesProduct']:
                    if parameter['type'] == 'dictionary' and 'dictionary' in parameter.keys():
                        for element in parameter['dictionary']:
                            param['values'].append(element['value'])
                    elif 'restrictions' in parameter.keys():
                        restrictions = parameter['restrictions']
                        if parameter['type'] == 'string':
                            if 'minLength' in restrictions.keys():
                                param['restrictions']['min'] = int(restrictions['minLength'])
                            if 'maxLength' in restrictions.keys():
                                param['restrictions']['max'] = int(restrictions['maxLength'])
                        elif parameter['type'] == 'integer' or parameter['type'] == 'float':
                            if 'min' in restrictions.keys():
                                param['restrictions']['min'] = int(restrictions['min'])
                            if 'max' in restrictions.keys():
                                param['restrictions']['max'] = int(restrictions['max'])
                    to_form['product'].append(param)

                else:
                    if parameter['type'] == 'dictionary' and 'dictionary' in parameter.keys():
                        for element in parameter['dictionary']:
                            param['values'].append(element['value'])
                    elif 'restrictions' in parameter.keys():
                        restrictions = parameter['restrictions']
                        if parameter['type'] == 'string':
                            if 'minLength' in restrictions.keys():
                                param['restrictions']['min'] = int(restrictions['minLength'])
                            if 'maxLength' in restrictions.keys():
                                param['restrictions']['max'] = int(restrictions['maxLength'])
                        elif parameter['type'] == 'integer' or parameter['type'] == 'float':
                            if 'min' in restrictions.keys():
                                param['restrictions']['min'] = int(restrictions['min'])
                            if 'max' in restrictions.keys():
                                param['restrictions']['max'] = int(restrictions['max'])
                    to_form['offer'].append(param)

        return to_form['product'], to_form['offer']
    except requests.exceptions.HTTPError as err:
        response = HttpResponse(err)
        response['Refresh'] = '5;url=/admin/store/product'
        return response


def is_category_leaf(category_id):
    try:
        allegro_token = Token.objects.get(name="allegro")
        token = allegro_token.access_token
        url = ENV_URL + "sale/categories/" + str(category_id)
        headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json"}
        category = requests.get(url, headers=headers, verify=False)
        cat = category.json()
        is_leaf = cat['leaf']
        return is_leaf
    except requests.exceptions.HTTPError as err:
        response = HttpResponse(err)
        response['Refresh'] = '5;url=/admin/store/product'
        return response


def change_quantity(offer_id, quantity):
    try:
        allegro_token = Token.objects.get(name="allegro")
        token = allegro_token.access_token
        change_quant_url = ENV_URL + "sale/product-offers/" + str(offer_id)
        headers = {'Authorization': "Bearer " + token, 'Accept': "application/vnd.allegro.public.v1+json",
                   'Content-Type': 'application/vnd.allegro.public.v1+json'}
        data = {
            "stock": {"available": quantity},
        }
        response = requests.patch(change_quant_url, headers=headers, json=data, verify=False, allow_redirects=False)
    except requests.exceptions.HTTPError as err:
        print("Failed to change quantity of offers because of HTTP error: ", err)


# Tasks
def refresh_tokens_every_4_hours():
    try:
        allegro_token = Token.objects.get(name="allegro")
        refresh_token = allegro_token.refresh_token
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token, 'redirect_uri': REDIRECT_URI}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False, auth=(CLIENT_ID, CLIENT_SECRET))
        tokens = json.loads(access_token_response.text)
        allegro_token.access_token = tokens['access_token']
        allegro_token.refresh_token = tokens['refresh_token']
        allegro_token.time_of_invalidation = timezone.now() + datetime.timedelta(seconds=int(tokens['expires_in']))
        allegro_token.authorized = True
        allegro_token.save()
    except requests.exceptions.HTTPError as err:
        print("Failed to refresh token, because of HTTP error: ", err)


def check_quants_every_5_seconds():
    try:
        allegro_token = Token.objects.get(name="allegro")
        token = allegro_token.access_token
        authorized = allegro_token.authorized
        if authorized:
            url = ENV_URL + "sale/offers"
            headers = {'Authorization': "Bearer " + token, 'Accept': "application/vnd.allegro.public.v1+json"}
            offers_result = requests.get(url, headers=headers, verify=False, allow_redirects=False)
            offers = json.loads(offers_result.text)
            if offers_result.status_code == 200:
                products = Product.objects.exclude(allegro_offer_id="not added")
                for product in products:
                    for offer in offers['offers']:
                        if offer['id'] == str(product.allegro_offer_id) and offer['publication']['status'] == 'ACTIVE':
                            offer_id = offer['id']
                            offer_quantity = offer['stock']['available']
                            if int(product.max_quantity) > int(offer_quantity):
                                product.max_quantity = int(offer_quantity)
                                product.save()
                            elif int(product.max_quantity) < int(offer_quantity):
                                change_quantity(offer_id, int(product.max_quantity))
            else:
                print(offers_result.text)
        else:
            refresh_tokens_every_4_hours()
    except requests.exceptions.HTTPError as err:
        print("Failed to check quantity of offers because of HTTP error: ", err)


def check_time_of_invalidation():
    time_now = timezone.now()
    token = Token.objects.get(name="allegro")
    if token.time_of_invalidation is not None:
        if token.time_of_invalidation < time_now:
            token.authorized = False
            token.save()



