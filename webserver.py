import cherrypy
import os

import measure
import graph
import io
import base64

from types import SimpleNamespace
from cherrypy.lib import file_generator


class Hp8903Server(object):
    @cherrypy.expose
    def index(self):
        cherrypy.response.headers["Location"] = "/index.html"
        cherrypy.response.status = 301

    @cherrypy.expose
    def measure(self, type=None, steps=None, freq1=None, freq2=None, amp1=None, amp2=None):
        args = {
            'start_frequency': int(freq1),
            'stop_frequency': int(freq2),
            'start_amplitude': float(amp1),
            'stop_amplitude': float(amp2),
            'measure': type
        }
        args = SimpleNamespace(**args)
        output = io.StringIO()
        measure.measure(args, output)

        image = self.graph(type, output.getvalue())
        return image

        #return f"Type={type}, steps={steps}, freq1={freq1}, freq2={freq2}, amp1={amp1}, amp2={amp2}\n{output.getvalue()}"

    @cherrypy.expose
    def graph(self, type=None, csv=None):
        output_buffer = io.BytesIO()
        graph.create_graph(type, csv, "png", output_buffer, None, 'style/theta.mplstyle', None)
        output_buffer.seek(0)


        if cherrypy.request.headers.has_key("x-content-encoding") and cherrypy.request.headers["x-content-encoding"]:
            cherrypy.response.headers['Content-Type'] = "text/plain; charset=ISO-8859-1"
            return base64.b64encode(output_buffer)
        else:
            cherrypy.response.headers['Content-Type'] = "image/png"
            return file_generator(output_buffer)



WEBROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"webroot/")

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.quickstart(Hp8903Server(), '/', {
    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': WEBROOT_PATH + "css"
    },
    '/js': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': WEBROOT_PATH + "js"
    },
    '/index.html': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': WEBROOT_PATH + "index.html"
    },
})