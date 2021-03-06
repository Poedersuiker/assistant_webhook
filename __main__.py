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

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            policy_text = open('policy.html', 'rb')
            self.wfile.write(policy_text.read())
            policy_text.close()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("OK {0}".format(path).encode())

    def do_POST(self):
        logging.info(self.path)
        authkey = self.headers.get('authkey')
        path = self.path.split('/')

        if authkey == aw_config.authkey:
            jsonstring = self.rfile.read(int(self.headers['Content-Length']))
            msg_id = self.awpubsub.publish_msg(path[1], path[2], jsonstring)
            if len(str(msg_id)) > 3:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                logging.info(jsonstring.decode('utf-8'))
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