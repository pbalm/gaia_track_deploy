# -*- coding: utf-8 -*-
"""
    top_airports
    ~~~~~~~~~~~~

    A simple web-service that can build a list of the most visited airports,
    according to a pre-installed file with bookings data.
"""
import os
import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader, Markup

# My imports
import json
import re

# This class is adapted from the Shortly example in the WerkZeug docs.
# For explanations on the plumbing, please see:
# http://werkzeug.pocoo.org/docs/tutorial/#introducing-shortly

def get_hostname(url):
    return urlparse.urlparse(url).netloc

class TrackDeploySvc(object):
    
    def __init__(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.jinja_env.filters['hostname'] = get_hostname
        
        # Define the routing of incoming URLs to methods in this class that handle the
        # requests
        self.url_map = Map([
            Rule('/track_deploy', endpoint='product_table'),
            Rule('/track_deploy/', endpoint='product_table'),
            Rule('/track_deploy/deploy', endpoint='deploy'),
        ])
        
    def on_product_table(self, request):
		f = open("deploy.json", 'r')
		data = json.load(f)
		deploy = data["products"]
		table = '<table><tr>\n'
		for k,v in deploy.iteritems():
			table = table + '\t<td>' + k + '</td><td>' + v + '</td></tr>\n'
		table = table + '</tr></table>\n'
		return self.render_template('product_table.html', site=data['site'], product_table=Markup(table))
        
    # A new artifact is deployed
    def on_deploy(self, request):
        
        product = request.args.get('product', None)
        version = request.args.get('version', None)
        data = None
        return Response(data.to_json(), mimetype='application/json')
	
    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    # This is where we define how to use the Rules from the constructor,
    # to match endpoints to functions (by prefixing 'on_').
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e
	
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app(with_static=True):
    app = TrackDeploySvc()
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/track_deploy/static':  os.path.join(os.path.dirname(__file__), 'track_deploy/static')
        })
        #app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        #    '/track_deploy/static':  '/track_deploy/static'
        #})
    return app

if __name__ == '__main__':
	
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
