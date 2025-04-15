from django import template
from decimal import Decimal, InvalidOperation
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
    2. Adding thousands separator (کاما)
    3. Appending "تومان" at the end
    
    If the value is None, return a dash.
    """
    if value is None:
        return "-"
    
    try:
        # Convert the value to Decimal for proper formatting
        decimal_value = Decimal(str(value))
        
        # تبدیل عدد به رشته با جداکننده هزارتایی
        formatted_parts = []
        int_part = int(decimal_value)
        
        # جداسازی بخش صحیح با کاما
        int_str = str(int_part)
        for i in range(len(int_str) - 3, 0, -3):
            int_str = int_str[:i] + "," + int_str[i:]
        formatted_parts.append(int_str)
        
        # اگر بخش اعشاری داریم، آن را اضافه می‌کنیم
        decimal_part = decimal_value - int(decimal_value)
        if decimal_part > 0:
            # حذف صفرهای انتهایی بخش اعشاری
            decimal_str = str(decimal_part).split('.')[1].rstrip('0')
            if decimal_str:
                # تبدیل نقطه اعشار به کاما
                formatted_parts.append(decimal_str)
        
        formatted_value = ','.join(formatted_parts)
        
        # Add تومان at the end
        return f"{formatted_value} تومان"
    except (ValueError, InvalidOperation):
        return str(value)

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