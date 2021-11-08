from django import template
register = template.Library()

@register.filter
def addclass(field, arg):
    return field.as_widget(attrs={"class": arg})
