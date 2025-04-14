from django import template
from django.utils import timezone
import jdatetime

register = template.Library()

@register.filter(name='to_jalali')
def to_jalali(value, format_string="%Y/%m/%d"):
    """تبدیل تاریخ میلادی به تاریخ شمسی"""
    if value is None:
        return ""
    try:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime(format_string)
    except:
        return ""

@register.filter(name='to_jalali_month_year')
def to_jalali_month_year(value):
    """تبدیل فرمت Y-m میلادی به سال و ماه شمسی"""
    if not value or len(value) != 7:
        return value
    try:
        year, month = value.split('-')
        gregorian_date = timezone.datetime(int(year), int(month), 1)
        jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
        months = {
            1: 'فروردین',
            2: 'اردیبهشت',
            3: 'خرداد',
            4: 'تیر',
            5: 'مرداد',
            6: 'شهریور',
            7: 'مهر',
            8: 'آبان',
            9: 'آذر',
            10: 'دی',
            11: 'بهمن',
            12: 'اسفند'
        }
        return f"{months[jalali_date.month]} {jalali_date.year}"
    except:
        return value 