import logging
from logging.handlers import RotatingFileHandler
from app import create_app, db
from tornado.web import FallbackHandler, Application, StaticFileHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.options import options

from app.ws import handler
from app.ws.handler import IndexHandler, WsockHandler, NotFoundHandler
from app.ws.settings import (
    get_app_settings,  get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings, check_encoding_setting
)
from tornado.httpserver import HTTPServer


flask_app = WSGIContainer(create_app())

def make_handlers(loop, options):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = [
        (r'/ws/connection', IndexHandler, dict(loop=loop, policy=policy,
                                                host_keys_settings=host_keys_settings)),
        (r'/ws', WsockHandler, dict(loop=loop)),
        (r'/(.*)', FallbackHandler, dict(fallback=flask_app))
    ]
    return handlers

def make_app(handlers, settings):
    settings.update(default_handler_class=NotFoundHandler)
    return Application(handlers, **settings)

def app_listen(app, port, address, server_settings):
    app.listen(port, address, **server_settings)
    if not server_settings.get('ssl_options'):
        server_type = 'http'
    else:
        server_type = 'https'
        handler.redirecting = True if options.redirect else False
    logging.info(
        'Listening on {}:{} ({})'.format(address, port, server_type)
    )

def write_log(msg):
    file_handler = RotatingFileHandler('logs/opsdev.log', maxBytes=102400,
                                        backupCount=10)
    file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)
    logger.info(msg)

def main():
    options.parse_command_line()
    check_encoding_setting(options.encoding)
    loop = IOLoop.current()
    app = make_app(make_handlers(loop, options), get_app_settings(options))
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    app_listen(app, options.port, options.address, server_settings)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app_listen(app, options.sslport, options.ssladdress, server_settings)
    loop.start()

if __name__ == "__main__":
    main()
