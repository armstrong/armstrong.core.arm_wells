from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _


class SimpleWellView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        if not 'params' in context:
            raise ImproperlyConfigured(
                    _(u"Expects `params` to be provided in the context"))
        if not self.template_name:
            if not 'template_name' in context['params']:
                raise ImproperlyConfigured(
                        _(u"Expects `template_name` to be provided"))
            else:
                self.template_name = context['params']['template_name']

        if not 'well' in context['params']:
            raise ImproperlyConfigured(_(u"Expects a `well` to be provided"))

        return super(SimpleWellView, self).render_to_response(context,
                **response_kwargs)
