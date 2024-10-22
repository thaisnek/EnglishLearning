from django import template
import math
register = template.Library()

# 100 -> 10% --> mpr -  (mpr*discount*0.01) = selprice

@register.simple_tag
def cal_sellprice(price,discount):
    if discount is None or discount is 0:
        return price
    sellprice = price
    sellprice = price - (price*discount*0.01)
    return math.floor(sellprice)

@register.filter
def usd(price):
    return f"${price}"
