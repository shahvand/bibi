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
    """حذف اعشار و صفرهای اضافی از قیمت و اضافه کردن تومان در انتها"""
    if value is None:
        return ""
    
    try:
        # تبدیل به Decimal برای اطمینان
        decimal_value = Decimal(str(value))
        
        # اگر عدد صحیح است، فقط بخش صحیح را برگردان با فرمت هزارگان
        if decimal_value == decimal_value.to_integral_value():
            formatted_value = "{:,}".format(int(decimal_value))
            return f"{formatted_value} تومان"
        
        # در غیر این صورت، عدد اعشاری را برگردان، با حذف صفرهای انتهایی و فرمت هزارگان
        cleaned_value = str(decimal_value).rstrip('0').rstrip('.') if '.' in str(decimal_value) else str(decimal_value)
        
        if '.' in cleaned_value:
            integer_part, decimal_part = cleaned_value.split('.')
            formatted_value = "{:,}.{}".format(int(integer_part), decimal_part)
        else:
            formatted_value = "{:,}".format(int(cleaned_value))
            
        return f"{formatted_value} تومان"
    except:
        return value

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