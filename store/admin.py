from django.contrib import admin
from .models import *
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils import timezone
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('allegro_offer_id', 'olx_offer_id')

    def response_add(self, request, obj, post_url_continue=None):
        if obj.allegro_action == 'no_action':
            obj.save()
            return super().response_add(request, obj, post_url_continue)
        else:
            action = obj.allegro_action
            obj.allegro_action = 'no_action'
            obj.save()
            allegro_token, created = Token.objects.get_or_create(name="allegro")
            if created or not allegro_token.authorized:
                return HttpResponseRedirect(reverse('Auth_site'))
            else:
                return HttpResponseRedirect(reverse('allegro-callback', args=(obj.id, str(action))))

    def response_change(self, request, obj):
        if obj.allegro_action == 'no_action':
            obj.save()
            return super().response_change(request, obj)
        else:
            action = obj.allegro_action
            obj.allegro_action = 'no_action'
            obj.save()
            allegro_token, created = Token.objects.get_or_create(name="allegro")
            if created or not allegro_token.authorized:
                return HttpResponseRedirect(reverse('Auth_site'))
            else:
                return HttpResponseRedirect(reverse('allegro-callback', args=(obj.id, str(action))))


admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(Subcategory)
