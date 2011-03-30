from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView


class SimpleWellView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        if not 'params' in context:
            raise ImproperlyConfigured(
                    "Expects `params` to be provided in the context")
        if not self.template_name:
            if not 'template_name' in context['params']:
                raise ImproperlyConfigured(
                        "Expects `template_name` to be provided")
            else:
                self.template_name = context['params']['template_name']

        if not 'well' in context['params']:
            raise ImproperlyConfigured("Expects a `well` to be provided")

        return super(SimpleWellView, self).render_to_response(context,
                **response_kwargs)
