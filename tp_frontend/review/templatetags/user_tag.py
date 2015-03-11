from django import template
from django.contrib.auth.models import User


register = template.Library()
@register.filter(name='getusername')
def get_username(value):
    """
    Get user name via template tags
    """
    user = User.objects.get(id=int(value)).username.capitalize()
    if user:
        return user
    return 'Unknown'

@register.filter(name='get_colourcode')
def get_colourcode(id):
    """
    Get coulour code from user id
    :param id:
    :return:
    """
    dict = {
        1: '#337ab7', 2: '#22D08E', 3: '#f0ad4e', 4:'#5bc0de', 5:'#5cb85c',
        6: '#d9534f', 7: 'Coral', 8: 'darkcyan', 9: 'MediumSeaGreen', 10: 'LightCoral',
        11: 'Crimson', 12: 'DarkOrchid', 13: 'DarkGoldenRod', 14: 'OrangeRed', 15: 'RebeccaPurple'
    }
    return dict[id]



@register.filter(name='convert')
def convert(value):
    """
    Get user name via template tags
    """
    return float(value)


@register.filter(name='removeprefix')
def removeprefix(value):
    """
    Remove prefix: DBPedia>Soft_drink will become Soft drink
    """
    if ">" in value:
        surface_text = (value.split('>')[1]).replace("_", " ").replace("-", " ")
        return surface_text.capitalize()
    return value.capitalize()

