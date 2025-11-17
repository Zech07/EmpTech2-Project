from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names): #Check if user belongs to one or multiple groups. group_names: comma-separated string, e.g. "staff,admin"

    group_list = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()