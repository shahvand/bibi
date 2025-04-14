from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def call(obj):
    """템플릿에서 메소드 객체를 호출합니다."""
    if callable(obj):
        return obj()
    return obj

@register.filter
def format_price(value):
    """حذف اعشار و صفرهای اضافی از قیمت"""
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