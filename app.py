import os
import redis
from urllib.parse import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
from views import Views
from settings import *
from database import DBClient


class Ads(object):

    def __init__(self, config):
        self.db_client = DBClient(host=config['db_host'], port=config['db_port'])
        self.db_client.register_table('ads')
        self.db_client.select_table('ads')

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)

        self.views = Views(app_renderer=self.render_template)

        self.url_map = Map([
            Rule('/', endpoint='ad_list_view'),
            Rule('/ad/<ad_id>/', endpoint='ad_detail_view'),
            Rule('/ad/create/', endpoint='ad_create_view'),
        ])

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self.views, 'on_' + endpoint)(request, **values)
        except HTTPException as e:
            return e


def create_app(with_static=True):
    app = Ads({
        'db_host': DB_HOST,
        'db_port': DB_PORT,
    })

    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple(APP_HOST, APP_PORT, app, use_debugger=True, use_reloader=True)
