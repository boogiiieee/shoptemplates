# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext, loader, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.views.generic import list_detail
from django.views.decorators.cache import never_cache 
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.utils import simplejson
from django.core.cache import cache
from django.db.models import Q
from django.db.models import Avg, Max, Min, Count, Sum
from django.contrib.sitemaps import Sitemap
import datetime
import uuid
import re
import os

from robokassa.forms import RobokassaForm

from shop.models import Product, ProductGallery, Order, OrderProduct
from shop.forms import BasketForm, OrderForm
from shop.helper import threading_send_mail

################################################################################################################
################################################################################################################

#Для карты сайта
class ProductSitemap(Sitemap):
	changefreq = "monthly"
	priority = 0.7
	
	def items(self):
		return Product.objects.filter(is_active=True)
		
	def location(self, obj):
		return obj.get_absolute_url()
		
################################################################################################################
################################################################################################################

from admin_tools.dashboard.modules import DashboardModule

class OrdersModule(DashboardModule):
	def is_empty(self):
		return self.objects == None

	def __init__(self, **kwargs):
		super(OrdersModule, self).__init__(**kwargs)
		self.title = u'Новые заказы'
		self.template = 'shop/blocks/orders.html'
		self.objects = Order.objects.filter(is_new=True, is_history=True)[:10]
		
################################################################################################################
################################################################################################################

#Создать корзину
def set_basket(request, response):
	if 'shop_session' in request.COOKIES:
		shop_session = request.COOKIES['shop_session']
	else:
		shop_session = str(uuid.uuid4())
		response.set_cookie("shop_session", shop_session, expires=datetime.date(3000,1,1).strftime("%a, %d-%b-%Y %H:%M:%S GMT"), path='/')

	b, create = Order.objects.get_or_create(session=shop_session, is_history=False)
	return response, b

#Получить корзину / Список товаров
def shop_proc(request):
	ps = Product.objects.filter(is_active=True)

	result = {'basket':None, 'items':ps}
	
	if 'shop_session' in request.COOKIES:
		shop_session = request.COOKIES['shop_session']
		try: b = Order.objects.get(session=shop_session, is_history=False)
		except: pass
		else: result['basket'] = b
	return result

################################################################################################################
################################################################################################################

#Возвращает список товаров
def catalog(request):
	return render_to_response('shop/catalog.html', {'active':1}, RequestContext(request, processors=[shop_proc]))

################################################################################################################
################################################################################################################

#Возвращает информацию о товаре
def product(request, id, slug):
	try: p = Product.objects.get(id=int(id), is_active=True)
	except: raise Http404()
	
	return render_to_response('shop/product.html', {'item':p, 'active':1}, RequestContext(request, processors=[shop_proc]))

################################################################################################################
################################################################################################################

#Добавить товар в корзину
@never_cache
def basket_add(request, id):
	response = HttpResponseRedirect('/basket/')
	response, b = set_basket(request, response)

	try: p = Product.objects.get(is_active=True, id=int(id))
	except: raise Http404()
	else:
		op, create = OrderProduct.objects.get_or_create(order=b, product=p)
		op.count += 1
		op.save()

	return response
	
#Очистить корзину
@never_cache
def basket_clean(request):
	response = HttpResponseRedirect('/basket/')
	response, b = set_basket(request, response)
	
	b.delete()
	messages.add_message(request, messages.INFO, u'Корзина очищена.')
		
	return response

################################################################################################################
################################################################################################################

#Сделать заказ
@never_cache
def order(request):
	basket = None
	form = None
	formset = None
	
	if 'shop_session' in request.COOKIES:
		shop_session = request.COOKIES['shop_session']
		try: basket = Order.objects.get(session=shop_session, is_history=False)
		except: pass
		else:
			op = basket.get_op()
			
			BasketFormSet = modelformset_factory(OrderProduct, form=BasketForm, fields=('id', 'product', 'count'), extra=0, can_delete=True)
			
			if request.method == 'POST' and basket:
				if 'o' in request.GET:
					form = OrderForm(request.POST, instance=basket)
					if form.is_valid():
						form.save()
						basket.is_history = True
						basket.save()
						
						#Заказ создан
						domain = Site.objects.get_current().domain
						
						if basket.is_send_email:
							threading_send_mail(
								'shop/mail/create_order.html',
								u'Ваш заказ на сайте %s принят. Номер заказа %d.' % (domain, basket.id),
								[basket.email],
								{'obj':basket, 'domain':domain}
							)
					
						if basket.is_send_sms and basket.phone:
							pass
							
						users = User.objects.filter(is_staff=True, is_active=True)
						users_emails = [u.email for u in users]
						
						threading_send_mail(
							'shop/mail/create_order_admin.html',
							u'Новый заказ на сайте %s. Номер заказа %d.' % (domain, basket.id),
							users_emails,
							{'obj':basket, 'domain':domain}
						)
						
						return HttpResponseRedirect('/basket/pay/')
				else:
					form = OrderForm()
					
				if 's' in request.GET:
					formset = BasketFormSet(request.POST, queryset=op)
					
					if formset.is_valid():
						formset.save()
						messages.add_message(request, messages.INFO, u'Корзина сохранена.')
						return HttpResponseRedirect('/basket/')
				else:
					formset = BasketFormSet(queryset=op)
			else:
				form = OrderForm()
				formset = BasketFormSet(queryset=op)
	
	return render_to_response('shop/order.html', {'form':form, 'formset':formset, 'active':2}, RequestContext(request, processors=[shop_proc]))
	
################################################################################################################
################################################################################################################

#Оплата регистрации
# def pay(request):
	# if 'shop_session' in request.COOKIES:
		# shop_session = request.COOKIES['shop_session']
		
		# id = None
		# if 'id' in request.GET:
			# id = int(request.GET.get('id'))
			
		# if id:
			# try: b = Order.objects.get(session=shop_session, is_history=True, id=id)
			# except: raise Http404()
		# else:
			# try: b = Order.objects.filter(session=shop_session, is_history=True).latest('id')
			# except: raise Http404()
	
		# if b and b.get_total_count():
			# ps = Product.objects.filter(is_active=True)
			
			# initial = {
				# 'OutSum': b.get_total_cost(),
				# 'InvId': 0,
				# 'Desc': u'Заказ № %d' % b.id,
				# 'Culture': 'ru',
				
				# 'order_id':b.id,
			# }
			
			# form = RobokassaForm(initial = initial)
			# return render_to_response('shop/pay.html', {'items':ps, 'form':form, 'b':b, 'active':2}, RequestContext(request))
	# raise Http404()

################################################################################################################
################################################################################################################

#Оплатить заказ
@never_cache
def order_pay(request):
	b = None
	
	if 'shop_session' in request.COOKIES:
		shop_session = request.COOKIES['shop_session']
		
		id = None
		if 'id' in request.GET:
			id = int(request.GET.get('id'))

		if id:
			try: b = Order.objects.get(session=shop_session, is_history=True, id=id)
			except: raise Http404()
		else:
			try: b = Order.objects.filter(session=shop_session, is_history=True).latest('id')
			except: raise Http404()
			
		domain = Site.objects.get_current().domain
		
		if not id:
			threading_send_mail(
				'shop/mail/pay.html',
				u'Ваш заказ №%d ожидает оплаты на сайте %s.' % (b.id, domain),
				[b.email],
				{'obj':b, 'domain':domain}
			)
	
	return render_to_response('shop/order_pay.html', {'b':b, 'active':2}, RequestContext(request, processors=[shop_proc]))
	
################################################################################################################
################################################################################################################

#Спасибо за заказ
@never_cache
def order_thanks(request):
	if 'shop_session' in request.COOKIES:
		shop_session = request.COOKIES['shop_session']
		
		if 'id' in request.GET:
			id = int(request.GET.get('id'))

			try: b = Order.objects.get(session=shop_session, is_history=True, id=id)
			except: raise Http404()
			else:
				b.is_notified = True
				b.save()
				
				domain = Site.objects.get_current().domain
				
				threading_send_mail(
					'shop/mail/thanks.html',
					u'Спасибо за заказ! Ваш заказ №%d отправлен нашему оператору.' % b.id,
					[b.email],
					{'obj':b, 'domain':domain}
				)
			
				return render_to_response('shop/order_thanks.html', {'b':b, 'active':2}, RequestContext(request, processors=[shop_proc]))
	raise Http404()
	
################################################################################################################
################################################################################################################

#Контакты
def contacts(request):
	return render_to_response('contacts.html', {'active':3}, RequestContext(request, processors=[shop_proc]))

################################################################################################################
################################################################################################################