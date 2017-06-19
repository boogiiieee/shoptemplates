# -*- coding: utf-8 -*-

from django import template
from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError
from django.template import get_library, Library, InvalidTemplateLibrary
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.db.models import Avg, Max, Min, Count, Sum
from django.utils.encoding import force_unicode
import settings
import os
import re

from shop.models import Product, Order

register = template.Library()

#######################################################################################################################
#######################################################################################################################

#Возвращает товар по id	
class ShopPrductByIdNode(Node):
	def __init__(self, varname, id):
		self.varname = varname
		self.id = id
		
	def render(self, context):
		context[self.varname] = Product.objects.get(id=template.Variable(self.id).resolve(context), is_active=True)
		return ''

def ShopPrductById(parser, token):
	bits = token.split_contents()
	if len(bits) != 3: raise TemplateSyntaxError(_('Error token tag "ShopPrductById"'))
	return ShopPrductByIdNode(bits[1][1:-1], bits[2])

register.tag('ShopPrductById', ShopPrductById)

#######################################################################################################################
#######################################################################################################################

@register.filter(name='mult')
def mult(x, y):
	try:
		x = int(x)
		y = int(y)
	except: return u'-'
	if x*y < 1: return u'-'
	return x*y
		
#######################################################################################################################
#######################################################################################################################

def shop_intcomma(value, exploder=' '):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>%s\g<2>' % exploder, orig)
    if orig == new: return new
    else: return shop_intcomma(new)
	
shop_intcomma.is_safe = True
register.filter(shop_intcomma)

#######################################################################################################################
#######################################################################################################################