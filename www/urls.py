# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.sitemaps import FlatPageSitemap
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

from shop.views import ProductSitemap

sitemaps = {
	'product':ProductSitemap,
}

urlpatterns = patterns('',
	url(r'^admin/filebrowser/', include('filebrowser.urls')),
	url(r'^tinymce/', include('tinymce.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	url(r'^captcha/', include('captcha.urls')),
	
	url(r'^', include('shop.urls')),
	url(r'^robokassa/', include('robokassa.urls')),

	url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
	url(r'^robots\.txt$', 'django.views.static.serve', {'path':"/robots.txt", 'document_root':settings.MEDIA_ROOT, 'show_indexes': False}),
)