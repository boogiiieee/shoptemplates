# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic import simple
import settings

urlpatterns = patterns('shop.views',
	url(r'^$', 'catalog'),
	url(r'^catalog/(?P<id>[0-9]+)/(?P<slug>.+)/$', 'product', name='product_url'),
	
	url(r'^basket/$', 'order'),
	
	url(r'^basket/add/(?P<id>[0-9]+)/$', 'basket_add'),
	url(r'^basket/clean/$', 'basket_clean'),
	
	url(r'^basket/pay/$', 'order_pay'),
	url(r'^pay/$', 'order_pay'),
	
	url(r'^basket/thanks/$', 'order_thanks'),
	
	url(r'^contacts/$', 'contacts'),
	
	# url(r'^demo/shop/$', simple.direct_to_template, {'template':'shop/demo/shop.html'}),
	# url(r'^demo/corp/$', simple.direct_to_template, {'template':'shop/demo/corp.html'}),
	# url(r'^demo/site/$', simple.direct_to_template, {'template':'shop/demo/site.html'}),
)