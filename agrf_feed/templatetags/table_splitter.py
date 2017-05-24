from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = Library()


@register.filter(needs_autoescape=True)
@stringfilter
def null_split_and_style(text, autoescape=True):
    """
    Expects the text argument to have three unicode nulls in it: \N{NULL}
    The text is split on these nulls and marked up inline.
    
    :param text: The text to be split and marked up
    :param autoescape: Should the conditional escape function be used or not?
    :return: The marked up text input
    """
    widths = [20, 9, 3, 10]
    align = ['left', 'right', 'right', 'left']
    titles =['Name', 'Size', 'Days until deletion', 'Status']
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = ''
    for index, section in enumerate(text.split('\N{NULL}')):
        result += f'<span title="{titles[index]}" style="' \
                  f'display: inline-block; ' \
                  f'width: {widths[index]}em; ' \
                  f'text-align: {align[index]}">{esc(section)}</span>&nbsp;'
    return mark_safe(result)
