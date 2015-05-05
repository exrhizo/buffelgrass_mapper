#!/usr/bin/env python

import operator, os, pickle, sys
import subprocess

import cherrypy
from cherrypy.lib.static import serve_file
from genshi.template import TemplateLoader

from BuffelMapper.Settings import settings

from Model import Photograph, Flight, Flights

loader = TemplateLoader(
    os.path.join(settings["buffel_root"], "BuffelWeb" ,"templates"),
    auto_reload=True
)

class Root(object):
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.F = Flights()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/map_camera')

    @cherrypy.expose
    def flights(self):
        tmpl = loader.load('flights.html')
        stream = tmpl.generate(title='Flights', flights=self.F.flights, vehicle=self.vehicle)
        return stream.render('html', doctype='html')

    @cherrypy.expose
    def map_camera(self):
        tmpl = loader.load('map_camera.html')
        stream = tmpl.generate(title='Map Camera', picture=None, vehicle=self.vehicle)
        return stream.render('html', doctype='html')

    @cherrypy.expose
    def download_flight(self, idx=None):
        if not idx:
            return 'Error, flight not specified'
        idx = int(idx)
        if idx >= 0 and idx<len(self.F.flights):
            flight = self.F.flights[idx]
            path = flight.path
            out_file = os.path.join(settings["buffel_root"], "BuffelWeb" , "static", "%s.tgz" % flight.name)
            err = self.compress(path, out_file)
            if err:
                return "Error compressing: %s" % err 
            return serve_file(out_file, "application/x-download", "attachment")
        else:
            return "Error, invalid flight"
        return ''.join(random.sample(string.hexdigits, int(length)))
    
    def compress(self, in_file, out_file):
        sep = os.path.split(in_file)
        command = ["tar", "-czf", out_file, "-C" , sep[0], sep[1]]

        compress_proc = subprocess.Popen(command, 
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
        out, err = compress_proc.communicate()
        return err

class BuffelWebServer(object):
    def __init__(self, vehicle=None, buffel_mapper=None):
        self.vehicle = vehicle
        self.buffel_mapper = buffel_mapper

        self.config()

        conf = {
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': './static'
            }
        }
        cherrypy.tree.mount(Root(vehicle), '/', conf)
        cherrypy.engine.start()


    def config(self):
        cherrypy.config.update({
            'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
            'tools.decode.on': True,
            'tools.trailing_slash.on': True,
            'tools.staticdir.root': os.path.abspath(os.path.join(settings["buffel_root"], "BuffelWeb")),
        })

    def close(self):
        cherrypy.engine.stop()

if __name__ == '__main__':
    BuffelWebServer()
    cherrypy.engine.block()