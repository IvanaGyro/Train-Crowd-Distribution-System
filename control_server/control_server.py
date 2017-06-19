# File Transfer for Pythonista
# ============================
# This script allows you to transfer Python files from
# and to Pythonista via local Wifi.
# It starts a basic HTTP server that you can access
# as a web page from your browser.
# When you upload a file that already exists, it is
# renamed automatically.
# From Pythonista's settings, you can add this script
# to the actions menu of the editor for quick access.
#
# Get Pythonista for iOS here:
# http://omz-software.com/pythonista

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import urllib
import cgi
import socket
from socket import gethostname
import os
from cStringIO import StringIO
 
import sys
import time
import inspect
sys.stderr = sys.stdout

TEMPLATE = ('<!DOCTYPE html><html><head>' +
  '<link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.1.1/'+
  'css/bootstrap-combined.min.css" rel="stylesheet"></head><body>' +
  '<div class="navbar"><div class="navbar-inner">' +
  '<a class="brand" href="#">Pythonista File Transfer</a>' +
  '</div></div><div class="container">' +
  '<h2>Upload File</h2>{{ALERT}}'
  '<p><form action="/" method="POST" enctype="multipart/form-data">' +
  '<div class="form-actions">' +
  '<input type="file" name="file"></input><br/><br/>' +
  '<button type="submit" class="btn btn-primary">Upload</button>' +
  '</div></form></p><hr/><h2>Download Files</h2>' +
  '{{FILES}}</div></body></html>')
 
class TransferRequestHandler(BaseHTTPRequestHandler):
	def get_unused_filename(self, filename):
		if not os.path.exists(filename):
			return filename
		basename, ext = os.path.splitext(filename)
		suffix_n = 1
		while True:
			alt_name = basename + '-' + str(suffix_n) + ext
			if not os.path.exists(alt_name):
				return alt_name
			suffix_n += 1
	
	def get_html_file_list(self):
		buffer = StringIO()
		buffer.write('<ul>')
		root_dir = os.path.expanduser('.')
		
		files = []
		for dn, dc, filenames in os.walk(root_dir):
			for fn in filenames:
				rel_dir = os.path.relpath(dn, root_dir)
				if rel_dir != '.':
					rel_file = os.path.join(rel_dir, fn)
				else:
					rel_file = fn
				files.append(rel_file)
		
		for filename in files:
		#	if os.path.splitext(filename)[1] == '.py':
		#		buffer.write('<li><a href="%s">%s</a></li>' % (filename, filename))
			buffer.write('<li><a href="%s">%s</a></li>' % (filename, filename))
		buffer.write('</ul>')
		return buffer.getvalue()
	
	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		queries = urlparse.parse_qs(parsed_path.query)
		if 'action' in queries:
			if 'shutdown' in queries['action']:
				html = '<!DOCTYPE html><html><head></head><body><h1>The HTTP server is shutdown.</h1></body></html>'
				self.send_response(200)
				self.send_header('Content-Type', 'text/html')
				self.end_headers()
				self.wfile.write(html)
				import threading
				assassin = threading.Thread(target=server.shutdown)
				assassin.daemon = True
				assassin.start()
				return
		path = parsed_path.path
		if path == '/':
			html = TEMPLATE
			html = html.replace('{{ALERT}}', '')
			html = html.replace('{{FILES}}', self.get_html_file_list())
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write(html)
			return
		file_path = urllib.unquote(path)[1:]
		if os.path.isfile(file_path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/x-python')
			self.send_header('Content-Disposition',
			                 'attachment; filename=%s' % file_path)
			self.end_headers()
			with open(file_path, 'r') as f:
				data = f.read()
				self.wfile.write(data)
		else:
			html = TEMPLATE
			html = html.replace('{{ALERT}}', 
			       '<div class="alert alert-error">File not found</div>')
			html = html.replace('{{FILES}}', self.get_html_file_list())
			self.send_response(404)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write(html)
			
	def do_HEAD(self):
		parsed_path = urlparse.urlparse(self.path)
		path = parsed_path.path
		file_path = urllib.unquote(path)[1:]
		if os.path.isfile(file_path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/x-python')
			self.send_header('Content-Disposition',
			                 'attachment; filename=%s' % file_path)
			self.send_header('Content-Length', os.path.getsize(file_path))
			self.end_headers()
		else:
			html = TEMPLATE
			html = html.replace('{{ALERT}}', 
			       '<div class="alert alert-error">File not found</div>')
			html = html.replace('{{FILES}}', self.get_html_file_list())
			self.send_response(404)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write(html)
 
	def do_POST(self):
		# form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
		#                         environ={'REQUEST_METHOD':'POST',
		#                        'CONTENT_TYPE':self.headers['Content-Type']})
		i = inspect.getargspec(cgi.FieldStorage.__init__)
		print i[0]
		for k in i[3][3]:
			print k, i[3][3][k]
		print i[3]
		form = cgi.FieldStorage(fp=self.rfile)
		# with open('request', 'w') as fd:
		# 	fd.write('POST\n')
		# 	fd.write(str(form) + '\n')
		# 	fd.write(str(form.__dict__) + '\n')
		# 	for key in form:
		# 		fd.write(key + '\n')
		# 	fd.write('\n')
		print 'POST'
		print form
		print form.__dict__
		print list(form)
		for key in form:
			print key
		print
		self.send_response(200)
		self.send_header('Content-Type', 'text/html')
		self.end_headers()
		field_item = form['file']
		uploaded_filename = None
		dest_filename = None
		file_data = field_item.file.read()
		file_len = len(file_data)
		uploaded_filename = field_item.filename
		dest_filename = self.get_unused_filename(uploaded_filename)
		with open(dest_filename, 'w') as f:
			f.write(file_data)
		del file_data
		html = TEMPLATE
		if uploaded_filename != dest_filename:
			message = '%s uploaded (renamed to %s).' % (uploaded_filename,
			                                           dest_filename)
		else:
			message = '%s uploaded.' % (uploaded_filename)
		html = html.replace('{{ALERT}}',
		       '<div class="alert alert-success">%s</div>' % (message))
		html = html.replace('{{FILES}}', self.get_html_file_list())
		self.wfile.write(html)
 
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