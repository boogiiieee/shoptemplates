# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
import re

from shop.models import Product, Order, OrderProduct

##################################################################################################	
##################################################################################################

class BasketForm(forms.ModelForm):
	class Meta:
		model = OrderProduct
		fields = ('product', 'count')
		widgets = {
			'product':forms.HiddenInput(),
		}
		
	def clean_count(self):
		count = self.cleaned_data['count']
		if count < 1: raise forms.ValidationError(u'Некорректное количество')
		return count
		
##################################################################################################	
##################################################################################################

class OrderForm(forms.ModelForm):
	agreement = forms.BooleanField(label=u'Принимаю пользовательское соглашение')
	
	def __init__(self, *args, **kwargs):
		super(OrderForm, self).__init__(*args, **kwargs)
		
		self.fields['name'].required = True
		self.fields['phone'].required = True
		self.fields['email'].required = True
	
	class Meta:
		model = Order
		fields = ('name', 'phone', 'email', 'text')
		widgets = {'text':forms.Textarea()}
		
	def clean_phone(self): 
		phone = self.cleaned_data['phone']
		if phone:
			r = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
			if not r.findall(phone):
				raise forms.ValidationError(u'Некорректный номер телефона. Формат номера +7XXXXXXXXXX.')
		return phone
	
	def clean_name(self):
		name = self.cleaned_data['name']
		if name:
			r = re.search(u'^[а-яА-Я\ ]+$', name)
			if not r: raise forms.ValidationError(u'Некорректное ФИО')
		return name
		
	def clean_email(self):
		email = self.cleaned_data['email']
		if email:
			r = re.search(r'^[0-9a-zA-Z]([\.-]?\w+)*@[0-9a-zA-Z]([\.-]?[0-9a-zA-Z])*(\.[0-9a-zA-Z]{2,4})+$', email)
			if not r: raise forms.ValidationError(u'Некорректный e-mail')
		return email
		
##################################################################################################	
##################################################################################################