"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from pylons.controllers.util import log
from pylons.i18n import get_lang, set_lang
from webhelpers import *
from webhelpers.rails import tags
from webhelpers.rails.secure_form_tag import secure_form
from webhelpers.rails.urls import convert_boolean_attributes

from pprint import pformat as txt_pformat

def secure_button_to(name, url='', **html_options):
    """
    Generates a form containing a sole button that submits to the
    URL given by ``url``, securely.  Based on button_to from webhelpers.
    
    """
    if html_options:
        convert_boolean_attributes(html_options, ['disabled'])

    method_tag = ''
    method = html_options.pop('method', '')
    if method.upper() in ['PUT', 'DELETE']:
        method_tag = tags.tag('input', type_='hidden', id='_method', name_='_method',
                              value=method)

    form_method = (method.upper() == 'GET' and method) or 'POST'

    confirm = html_options.get('confirm')
    if confirm:
        del html_options['confirm']
        html_options['onclick'] = "return %s;" % confirm_javascript_function(confirm)

    if callable(url):
        ur = url()
        url, name = ur, name or tags.escape_once(ur)
    else:
        url, name = url, name or url

    submit_type = html_options.get('type')
    img_source = html_options.get('src')
    if submit_type == 'image' and img_source:
        html_options.update(dict(type=submit_type, value=name,
                                 alt=html_options.get('alt', name)))
        html_options['src'] = compute_public_path(img_source, 'images', 'png')
    else:
        html_options.update(dict(type='submit', value=name))

    return secure_form(url, method=form_method, _class="button-to") + """<div>"""  + method_tag + tags.tag("input", **html_options) + "</div></form>"

def pformat(obj):
    return '<pre>%s</pre>' % txt_pformat(obj)
