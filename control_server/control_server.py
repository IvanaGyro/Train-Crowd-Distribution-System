from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import urllib
import cgi
import socket
from socket import gethostname
import os
import json

 
class TransferRequestHandler(BaseHTTPRequestHandler):	
	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		queries = urlparse.parse_qs(parsed_path.query)
		if 'action' not in queries:
			return
		else:
			action = queries['action'][0]

		if action == 'light':
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			response = {}
			with open('crowd_level', 'r') as fd:
				response['crowd_level'] = int(fd.readlines()[-1])
			self.wfile.write(json.dumps(response))
 
	def do_POST(self):
		form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
		self.send_response(200)
		self.send_header('Content-Type', 'text/html')
		self.end_headers()
		parsed_path = urlparse.urlparse(self.path)
		queries = urlparse.parse_qs(parsed_path.query)
		if 'action' not in queries:
			return
		else:
			action = queries['action'][0]

		if action == 'calcu':
			if 'pic' not in form:
				print 'pic not in form'
				return
			if type(form['pic']) == type([]):
				picField = form['pic'][0]
			else:
				picField = form['pic']
			if picField.filename:
				destFn = os.path.join('..', 'image_process', picField.filename)
				print destFn
				with open(destFn, 'wb') as fd:
					fd.write(picField.value)
				self.wfile.write('OK')
				
 
if __name__ == '__main__':
	from BaseHTTPServer import HTTPServer
	server = HTTPServer(('', 8080), TransferRequestHandler)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	IP = s.getsockname()[0]
	s.close()
	URL = 'http://%s.local:8080' % gethostname()
	URLIP = 'http://%s:8080' % IP
	print 'hostname:%s' % gethostname()
	print 'Open this page in your browser:'
	print URL
	print URLIP
	print 'Tap the stop button when you\'re done.'
	server.serve_forever()
	server.server_close()