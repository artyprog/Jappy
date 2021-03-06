#!/usr/bin/env python3
import sys
import threading
import gi
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
from gi.repository import Gtk
from gi.repository import Gio

try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse

from server import start_server, bye, app

if sys.platform=='linux2':
    reload(sys)
    sys.setdefaultencoding('utf-8')

base_uri = 'http://127.0.0.1:54991#Jappy'

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def start_webview():
    def _app_scheme_cb(request, user_data):
        uri = request.get_path()
        with app.test_client() as c:
            response = c.get(uri) # TODO: instead, use c.open stream
            if response.status_code==302: # Handle redirect
                new_uri = urlparse.urlparse(response.location)
                new_uri = base_uri + '/' + new_uri.path +\
                                    new_uri.params + new_uri.query
                request.get_web_view().load_uri(new_uri)
            data, mime = response.data, response.mimetype
        input_stream = Gio.MemoryInputStream.new_from_data(data, None)
        #request.finish(Gio.File.new_for_path(path).read(None),
        #               -1, Gio.content_type_guess(path, None)[0])
        request.finish( input_stream, len(data), mime )

    context = WebKit2.WebContext.get_default()
    context.clear_cache()
    context.register_uri_scheme("activity", _app_scheme_cb, None)

    window = Gtk.Window()
    window.set_default_size(800, 600)
    window.maximize()
    web_view = WebKit2.WebView()
    #web_view.connect("load-changed", _loading_changed_cb)
    #web_view.connect('run-file-chooser', __run_file_chooser)

    window.add(web_view)

    settings = web_view.get_settings()
    settings.set_property('enable-developer-extras', True)
    #settings.set_property('enable-xss-auditor', False)
    settings.set_enable_xss_auditor(False)

    web_view.load_uri(base_uri)
    window.set_title("Jappy")
    window.set_title("Jappy")
    window.set_icon_from_file("activity/app-icon.png")
    window.show_all()

    def shutdown(*args):
        bye()
        Gtk.main_quit()
    window.connect("delete-event", shutdown)

def start_backend():
    try:
        start_server()
    except Exception as e:
        print ("WARNING: Could not start HTTP service: " + str(e))

if __name__ == "__main__":
    t = threading.Thread(target=start_backend)
    t.daemon = True
    t.start()

    start_webview()
    Gtk.main()
    sys.exit()
