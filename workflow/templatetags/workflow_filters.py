from django import template
from decimal import Decimal
import locale
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def call(obj):
    """템플릿에서 메소드 객체를 호출합니다."""
    if callable(obj):
        return obj()
    return obj

@register.filter
def clean_number(value):
    """حذف اعشار 0.00 از اعداد"""
    if value is None:
        return ""
    
    try:
        # تبدیل به Decimal برای اطمینان
        decimal_value = Decimal(str(value))
        
        # اگر عدد صحیح است، فقط بخش صحیح را برگردان
        if decimal_value == decimal_value.to_integral_value():
            return int(decimal_value)
        
        # در غیر این صورت، عدد اعشاری را برگردان، با حذف صفرهای انتهایی
        return str(decimal_value).rstrip('0').rstrip('.') if '.' in str(decimal_value) else decimal_value
    except:
        return value

@register.filter
def format_price(value):
    """
    Format a price value by:
    1. Removing decimal places if they're all zeros
    2. Adding thousands separator
    3. Adding ' تومان' suffix to the end
    
    If the value is None, return a dash.
    """
    if value is None:
        return "-"
    
    try:
        value = Decimal(str(value))
    except (ValueError, TypeError):
        return f"{value} تومان"

    # Format with thousands separator
    locale.setlocale(locale.LC_ALL, '')
    formatted_value = locale.format_string("%d", int(value), grouping=True)
    
    # Check if there are non-zero decimal places
    decimal_part = value % 1
    if decimal_part > 0:
        decimal_str = str(decimal_part).split('.')[1]
        formatted_value = f"{formatted_value}.{decimal_str}"
    
    # Add تومان suffix
    return f"{formatted_value} تومان"

def format_price_input(value):
    """تابع کمکی برای فرمت کردن قیمت‌ها در فرم‌ها"""
    if value is None:
        return ""
    
    try:
        decimal_value = Decimal(str(value))
        if decimal_value == decimal_value.to_integral_value():
            return int(decimal_value)
        return str(decimal_value).rstrip('0').rstrip('.') if '.' in str(decimal_value) else decimal_value
    except:
        return value 