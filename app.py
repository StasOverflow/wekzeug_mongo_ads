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


def is_valid_url(url):
    parts = urlparse(url)
    return parts.scheme in ('http', 'https')


def base36_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))


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

    def on_new_url(self, request):
        return
        error = None
        url = ''
        if request.method == 'POST':
            url = request.form['url']
            if not is_valid_url(url):
                error = 'Please enter a valid URL'
            else:
                short_id = self.insert_url(url)
                return redirect('/%s+' % short_id)
        return self.render_template('new_url.html', error=error, url=url)

    def insert_url(self, url):
        return
        short_id = self.db_client.get('reverse-url:' + url)
        if short_id is not None:
            return short_id
        url_num = self.db_client.incr('last-url-id')
        short_id = base36_encode(url_num)
        self.db_client.set('url-target:' + short_id, url)
        self.db_client.set('reverse-url:' + url, short_id)
        return short_id

    def on_follow_short_link(self, request, short_id):
        return
        link_target = self.db_client.get('url-target:' + short_id)
        if link_target is None:
            raise NotFound()
        self.db_client.incr('click-count:' + short_id)
        return redirect(link_target)

    def on_short_link_details(self, request, short_id):
        return
        link_target = self.db_client.get('url-target:' + short_id)
        if link_target is None:
            raise NotFound()
        click_count = int(self.db_client.get('click-count:' + short_id) or 0)
        return self.render_template('short_link_details.html',
                                    link_target=link_target,
                                    short_id=short_id,
                                    click_count=click_count
                                    )


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
