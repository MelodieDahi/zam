from pyramid.config import Configurator
from pyramid.router import Router


def make_app(global_settings: dict, **settings: dict) -> Router:
    with Configurator(settings=settings) as config:
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")
        config.add_route("home", "/")
        config.scan()
        app = config.make_wsgi_app()
    return app
