from django.conf import settings
from drf_yasg.generators import OpenAPISchemaGenerator, EndpointEnumerator


class SwaggerEndpointEnumerator(EndpointEnumerator):
    """
    Add custom setting to exclude views
    """

    def should_include_endpoint(self, path, callback, app_name='',
                                namespace='', url_name=None):
        view = '{}.{}'.format(callback.__module__, callback.__qualname__)
        if url_name in settings.SWAGGER_SETTINGS['EXCLUDE_URL_NAMES']:
            return False

        return super().should_include_endpoint(
            path, callback, app_name, namespace, url_name
        )


class SwaggerAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    We want change default endpoint enumerator class
    """
    endpoint_enumerator_class = SwaggerEndpointEnumerator
