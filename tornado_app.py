import os
from tornado.web import Application, FallbackHandler, RequestHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from darksky_api import app


APP_PORT = 80
if 'APP_PORT' in os.environ:
    APP_PORT = os.environ['APP_PORT']


class MainHandler(RequestHandler):
    def get(self):
        self.write("This message comes from Tornado ^_^")

tr = WSGIContainer(app)

application = Application([
    (r"/tornado", MainHandler),
    (r".*", FallbackHandler, dict(fallback=tr)),
])

if __name__ == "__main__":
    application.listen(int(APP_PORT), address='0.0.0.0')
    IOLoop.instance().start()