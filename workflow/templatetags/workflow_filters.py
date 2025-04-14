from django import template

register = template.Library()

@register.filter
def call(obj):
    """템플릿에서 메소드 객체를 호출합니다."""
    if callable(obj):
        return obj()
    return obj 