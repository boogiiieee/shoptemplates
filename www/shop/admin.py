# -*- coding: utf-8 -*-

from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
from django.utils.translation import ugettext_lazy as _

from shop.models import Product, ProductGallery, Order, OrderProduct, OrderStatus

################################################################################################################
################################################################################################################

#Изображение товара
class ProductGalleryInline(AdminImageMixin, admin.StackedInline):
	model = ProductGallery
	extra = 0
	ordering = ('-is_main', 'sort', 'id')
	
#Товар
class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
	inlines = [ProductGalleryInline]
	list_display = ('id', 'title', 'cost', 'is_active', 'sort')
	list_display_links = ('id', 'title')
	search_fields = ('title',)
	list_filter = ('is_active',)
	list_editable = ('is_active', 'sort')
	ordering = ('sort', '-id',)
		
admin.site.register(Product, ProductAdmin)

################################################################################################################
################################################################################################################
		
#Корзина пользователя
class OrderProductInline(admin.TabularInline):
	model = OrderProduct
	fields = ('ids', 'product', 'count', 'cost', 'total')
	readonly_fields = ['ids', 'cost', 'total']
	raw_id_fields = ('product',) 
	extra = 0

	def ids(self, obj):
		return u'<strong>#%d</strong>' % obj.product.id
	ids.short_description = u'ID'
	ids.allow_tags = True
	
	def cost(self, obj):
		return u'%d руб.' % obj.product.get_cost()
	cost.short_description = u'Цена'
	
	def total(self, obj):
		return u'<strong>%d руб.</strong>' % obj.get_total_cost()
	total.short_description = u'Стоимость'
	total.allow_tags = True

#Заказы
class OrderAdmin(AdminImageMixin, admin.ModelAdmin):
	inlines = [OrderProductInline]
	list_display = ('id', 'name', 'is_new', 'is_notified', 'is_paid', 'phone', 'email', 'status', 'date')
	list_display_links = ('id', 'name')
	search_fields = ('name', 'phone', 'email')
	list_filter = ('date', 'is_new', 'is_notified', 'is_paid', 'status')
	readonly_fields = ('total',)
	fieldsets = ((None, {'fields': ('name', 'phone', 'email', 'status', 'is_send_email', 'text', 'is_new', 'is_notified', 'is_paid', 'total')}),)
	ordering = ('-date',)
	
	def total(self, obj):
		return u'<strong>%d руб.</strong>' % obj.get_total_cost()
	total.short_description = u'Стоимость'
	total.allow_tags = True
	
	def queryset(self, request):
		return super(OrderAdmin, self).queryset(request).filter(is_history=True)

admin.site.register(Order, OrderAdmin)

################################################################################################################
################################################################################################################

#Статус заказа
class OrderStatusAdmin(admin.ModelAdmin):
	list_display = ('title', 'is_new', 'is_last', 'is_active', 'sort')
	search_fields = ('title',)
	list_filter = ('is_active',)
	list_editable = ('is_active', 'sort')

admin.site.register(OrderStatus, OrderStatusAdmin)

################################################################################################################
################################################################################################################