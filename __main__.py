from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import logging
import aw_config # personal configuration file (fill from aw_config-example.py)
import ssl
from aw_pubsub import AWPubSub

class AWebhookHTTPServer(BaseHTTPRequestHandler):
    awpubsub = AWPubSub()

    def do_GET(self):
        logging.info(self.path)
        path = self.path.split('/')

        if True:
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write("OK {0}".format(path))

    def do_POST(self):
        logging.info(self.path)
        authkey = self.headers.get('authkey')
        path = self.path.split('/')

        if authkey == aw_config.authkey:
            msg_id = self.awpubsub.publish_msg(path[1], path[2])
            if len(str(msg_id)) > 3:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                jsonstring = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
                logging.info(jsonstring)
            else:
                self.send_response(msg_id)
        else:
            self.send_response(400)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle request in a separate thread"""


def run():
    logging.info('Starting HTTPS server')

    server_address = (aw_config.external_ip, aw_config.external_port)
    httpd = ThreadedHTTPServer(server_address, AWebhookHTTPServer)
    httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, certfile=aw_config.certfile, ssl_version=ssl.PROTOCOL_TLSv1)
    logging.info('HTTP server started')
    httpd.serve_forever()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    run()