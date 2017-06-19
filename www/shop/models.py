# -*- coding: utf-8 -*-

from django.db import connection, models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from pytils.translit import slugify
import settings
import datetime
import re
import os

from tinymce import models as TinymceField

from sorl.thumbnail import ImageField as SorlImageField
from sorl.thumbnail.shortcuts import get_thumbnail, delete

from shop.helper import threading_send_mail

################################################################################################################
################################################################################################################

#Товар	
class Product(models.Model):
	title = models.CharField(max_length=500, verbose_name=u'продукт')
	slug = models.CharField(max_length=500, verbose_name=u'псевдоним', blank=True)
	introduction = TinymceField.HTMLField(max_length=1000, verbose_name=u'краткое описание', blank=True)
	description = TinymceField.HTMLField(max_length=10000, verbose_name=u'описание', blank=True)
	cost = models.IntegerField(verbose_name=u'цена', default=0)
	
	icon = models.CharField(max_length=50, verbose_name=u'текст-иконка')
	color = models.CharField(max_length=50, verbose_name=u'цвет')
	width = models.CharField(max_length=50, verbose_name=u'ширина')
	height = models.CharField(max_length=50, verbose_name=u'высота')
		
	date = models.DateField(verbose_name=u'дата', auto_now = True, auto_now_add = True)

	is_active = models.BooleanField(verbose_name=u'активно', default=True)
	sort = models.IntegerField(verbose_name=u'порядок', default=0)
	
	class Meta: 
		verbose_name = u'продукт' 
		verbose_name_plural = u'продукты'
		ordering = ['sort',]
	
	def __unicode__(self):
		return self.title
		
	@models.permalink
	def get_absolute_url(self):
		return ('product_url', (), {'id':self.id, 'slug': self.slug},)
		
	def get_image(self):
		imgs = self.product_images.filter(is_main=True, is_active=True)
		if imgs.count(): return imgs[0]
		else:
			imgs = self.product_images.filter(is_active=True)
			if imgs.count(): return imgs.order_by('?')[0]
		return None
		
	def get_all_images(self):
		return self.product_images.all()
		
	def get_active_images(self):
		return self.get_all_images().filter(is_active=True)
	
	def get_cost(self):
		return self.cost
		
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Product, self).save(*args, **kwargs)
	
################################################################################################################
################################################################################################################
	
#Изображение товара		
class ProductGallery(models.Model):
	product = models.ForeignKey(Product, verbose_name=u'продукт', related_name='product_images')
	title = models.CharField(max_length=500, verbose_name=u'заголовок')
	text = TinymceField.HTMLField(max_length=1000, verbose_name=u'описание', blank=True)
	image = SorlImageField(max_length=500, upload_to='upload/shop/product/', verbose_name=u'изображение')
	is_main = models.BooleanField(verbose_name=u'главное изображение', default=False)
	is_active = models.BooleanField(verbose_name=u'активно', default=True)
	sort = models.IntegerField(verbose_name=u'порядок', default=0)
	
	class Meta: 
		verbose_name = u'изображение'
		verbose_name_plural = u'изображения'
		ordering = ['-is_main', 'sort', 'id']
		
	def __unicode__(self):
		return self.title
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.(jpg|jpeg|png|bmp|gif)$', re.IGNORECASE)
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(u'Некорректное имя файла.')
		
	def save(self, *args, **kwargs):
		if self.is_main:
			ProductGallery.objects.filter(product=self.product, is_main=True).update(is_main=False)
		super(ProductGallery, self).save(*args, **kwargs)

################################################################################################################
################################################################################################################

#Заказы
class Order(models.Model):
	session = models.CharField(max_length=200, verbose_name=u'сессия')
	name = models.CharField(max_length=100, verbose_name=u'ФИО', blank=True)
	phone = models.CharField(max_length=100, verbose_name=u'телефон', blank=True)
	email = models.EmailField(max_length=100, verbose_name=u'e-mail', blank=True)
	text = TinymceField.HTMLField(max_length=10000, verbose_name=u'комментарий', blank=True)
	status = models.ForeignKey('OrderStatus', verbose_name=u'статус', blank=True, null=True)
	is_send_email = models.BooleanField(verbose_name=u'уведомлять на e-mail', default=True)
	is_send_sms = models.BooleanField(verbose_name=u'уведомлять по СМС', default=True)
	products = models.ManyToManyField(Product, verbose_name=u'продукты', related_name='rel_products', through='OrderProduct')
	date = models.DateTimeField(verbose_name=u'дата', auto_now = True, auto_now_add = True)
	is_new = models.BooleanField(verbose_name=u'новый заказ', default=True)
	is_history = models.BooleanField(verbose_name=u'из истории', default=False)
	is_notified = models.BooleanField(verbose_name=u'пользователь уведомил об оплате', default=False)
	is_paid = models.BooleanField(verbose_name=u'пользователь оплатил заказ', default=False)
	
	class Meta: 
		verbose_name = u'заказ'
		verbose_name_plural = u'заказы'
		ordering = ['-is_new', 'id']
		
	def __unicode__(self):
		return u'%s (%s)' % (self.name, self.date.strftime("%d.%m.%Y %H:%M"))
	
	def get_op(self):
		return OrderProduct.objects.filter(order=self)
		
	def get_total_count(self):
		o = self.get_op()
		count = 0
		for i in o:
			try:
				c = int(i.count)
				if c > 0 and c < 1000000:
					count += c
			except: return 0
		return count
		
	def get_total_cost(self):
		o = self.get_op()
		total = 0
		for i in o:
			total += i.get_total_cost()
		return total
	
	def get_absolute_url(self):
		return '/admin/shop/order/%d/' % self.id
		
	def save(self, *args, **kwargs):
		if not self.status:
			try: self.status = OrderStatus.objects.get(is_active=True, is_new=True)
			except: pass
		
		domain = Site.objects.get_current().domain
		
		if self.id and self.is_notified and not Order.objects.get(id=self.id).is_notified:
			users = User.objects.filter(is_staff=True, is_active=True)
			users_emails = [u.email for u in users]
						
			threading_send_mail(
				'shop/mail/thanks_admin.html',
				u'Уведомление об оплате заказа №%d.' % self.id,
				users_emails,
				{'obj':self, 'domain':domain}
			)
		
		if self.id and self.status != Order.objects.get(id=self.id).status:
			if self.is_send_email and self.email:
				domain = Site.objects.get_current().domain
				
				threading_send_mail(
					'shop/mail/change_status.html',
					u'Статус Вашего заказа на сайте %s изменился на %s. Номер заказа %d.' % (domain, self.status, self.id),
					[self.email],
					{'obj':self, 'domain':domain}
				)
				
			if self.is_send_sms and self.phone:
				pass
				
		super(Order, self).save(*args, **kwargs)
	
################################################################################################################
################################################################################################################

#Корзина пользователя	
class OrderProduct(models.Model):
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	count = models.IntegerField(verbose_name=u'количество', default=0)
	date = models.DateTimeField(verbose_name=u'дата', auto_now = True, auto_now_add = True)
	
	class Meta:
		verbose_name = u'товар в заказе'
		verbose_name_plural = u'товары в заказе'
		ordering = ['product__sort']
	
	def __unicode__(self):
		return u'%s / %s' % (self.order, self.product)
		
	def clean(self):
		if self.count > 1000000 or self.count <= 0:
			raise ValidationError(u'Некорректное количество товара.')
			
	def get_total_cost(self):
		try:
			c = self.count
			if c > 0 and c < 1000000:
				return c * self.product.get_cost()
		except: pass
		return 0

################################################################################################################
################################################################################################################

#Статус заказа
class OrderStatus(models.Model):
	title = models.CharField(max_length=500, verbose_name=u'заголовок')
	is_new = models.BooleanField(verbose_name=u'статус нового заказа', default=False)
	is_last = models.BooleanField(verbose_name=u'статус выполненного заказа', default=False)
	is_active = models.BooleanField(verbose_name=u'активно', default=True)
	sort = models.IntegerField(verbose_name=u'порядок', default=0)
	
	class Meta: 
		verbose_name = u'статус заказа' 
		verbose_name_plural = u'статусы заказа'
		ordering = ['sort', 'title', 'id']
		
	def __unicode__(self):
		return self.title
		
	def save(self, *args, **kwargs):
		if self.is_new:
			OrderStatus.objects.filter(is_new=True).update(is_new=False)
		if self.is_last:
			OrderStatus.objects.filter(is_last=True).update(is_last=False)
		super(OrderStatus, self).save(*args, **kwargs)
		
################################################################################################################
################################################################################################################