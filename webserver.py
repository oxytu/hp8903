import cherrypy
import os

import measure
import graph
import io
import base64
import yaml

from types import SimpleNamespace
from cherrypy.lib import file_generator


WEBROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"webroot/")


class Hp8903Server(object):
    def __init__(self, config):
        self.persist_measurement = config["webserver"]["persist_measurements"]
        if (self.persist_measurement):
            print("Configured to persist measurements")

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers["Location"] = "/index.html"
        cherrypy.response.status = 301

    @cherrypy.expose
    def measurements(self):
        path = os.path.join(WEBROOT_PATH, "measurements")
        response_listing = ""
        for dpath, ddirs, dfiles in os.walk( path ):
            for fil in sorted( dfiles ):
                response_listing += f"<li><a href='/measurements/{fil}'>{fil}</a></li>"
        
        return f"<html><body><h1>Measurements</h1><ul>{response_listing}</ul></body></html>"

    @cherrypy.expose
    def measure(self, type=None, steps=None, freq1=None, freq2=None, amp1=None, amp2=None, title=None):
        args = {
            'steps': int(steps),
            'start_frequency': int(freq1),
            'stop_frequency': int(freq2),
            'start_amplitude': float(amp1),
            'stop_amplitude': float(amp2),
            'measure': type
        }
        
        args = SimpleNamespace(**args)
        output = io.StringIO()

        measure.measure(args, output)
        csv = output.getvalue()

        if (self.persist_measurement):
            with open(self.get_measurement_filename(title, "csv")) as writer:
                writer.write(csv)

        return csv

    def get_measurement_filename(self, title, typ):
        return os.path.join(WEBROOT_PATH, "measurements", f"{title}.{typ}")

    @cherrypy.expose
    def measure_and_graph(self, type=None, steps=None, freq1=None, freq2=None, amp1=None, amp2=None, title=None):
        csv = self.measure(type, steps, freq1, freq2, amp1, amp2, title)

        image = self.graph(type, title, csv)
        return image

    @cherrypy.expose
    def graph(self, type=None, title=None, csv=None):
        output_buffer = io.BytesIO()
        graph.create_graph(type, csv, "png", output_buffer, None, 'style/theta.mplstyle', None, title)
        output_buffer.seek(0)

        if (self.persist_measurement):
            with open(self.get_measurement_filename(title, "png")) as writer:
                writer.write(file_generator(output_buffer))
                output_buffer.seek(0)

        if "x-content-encoding" in cherrypy.request.headers and cherrypy.request.headers["x-content-encoding"] == "base64":
            cherrypy.response.headers['Content-Type'] = "text/plain; charset=ISO-8859-1"
            return base64.b64encode(output_buffer.read())
        else:
            cherrypy.response.headers['Content-Type'] = "image/png"
            return file_generator(output_buffer)


config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

cherrypy.server.socket_host = config["webserver"]["bind_address"]
cherrypy.server.socket_port = config["webserver"]["bind_port"]

cherrypy.quickstart(Hp8903Server(config), '/', {
    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': WEBROOT_PATH + "css"
    },
    '/js': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': WEBROOT_PATH + "js"
    },
    '/measurements': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': WEBROOT_PATH + "measurements"
    },
    '/index.html': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': WEBROOT_PATH + "index.html"
    },
})