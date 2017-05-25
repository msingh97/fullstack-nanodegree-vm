from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cgi

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.bind = engine
Session = sessionmaker(bind = engine)
session = Session()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/edit"):
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				output = "<html><body>"
				rest_id = get_id(self.path)
				try:
					rest_name = session.query(Restaurant).filter_by(id = rest_id).one().name
					output += "<h1>{0}</h1>".format(rest_name)
					output += "<form method='POST' enctype = 'multipart/form-data' action='restaurants/{0}/edit'><input name='newRestaurantName' type='text' placeholder='New Restaurant Name'><input type='submit' value='Rename'> </form>".format(rest_id)
					output += "</body></html>"
					self.wfile.write(output)
					print(output)
					return
				except:
					return

			if self.path.endswith("/delete"):
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				output = "<html><body>"
				rest_id = get_id(self.path)
				rest = session.query(Restaurant).filter_by(id = rest_id).one()
				if rest != []:
					rest_name = rest.name
					output += "<h1>Are you sure you want to delete {0}?</h1>".format(rest_name)
					output += "<form method='POST' enctype = 'multipart/form-data' action='restaurants/{0}/delete'><input type='submit' value='Delete'> </form>".format(rest_id)
					output += "</body></html>"
					self.wfile.write(output)
					print(output)
					return


			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()

				output = "<html><body><a href='restaurants/new'>Make a new Reataurant</a>"
				restaurants = session.query(Restaurant).all()
				for i in restaurants:
					output += "<p>{0}</p>".format(i.name)
					output += "<a href=/restaurants/{0}/edit>Edit</a> </br>".format(i.id)
					output += "<a href=/restaurants/{0}/delete>Delete</a>".format(i.id)
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
				return
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				output = "<html><body><h1>Make a New Restaurant</h1>"
				output += "<form method='POST' enctype = 'multipart/form-data' action='/restaurants/new'><input name='newRestaurantName' type='text' placeholder='New Restaurant Name'><input type='submit' value='Create'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
				return

		except IOError:
			self.send_error(404, "File Not Found {0}".format(self.path))

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(
				self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')

					# Create new Restaurant Object
					newRestaurant = Restaurant(name=messagecontent[0])
					session.add(newRestaurant)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(
				self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')
					rest_id = get_id(self.path)
					rest = session.query(Restaurant).filter_by(id = rest_id).one()
				if rest != []:
					rest.name = messagecontent[0]
					session.add(rest)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(
				self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')
					rest_id = get_id(self.path)
					rest = session.query(Restaurant).filter_by(id = rest_id).one()
				if rest != []:
					session.delete(rest)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

		except:
			pass


def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print("Web server running on port {0}".format(port))
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nHalting web server...")
		server.socket.close()

def get_id(path):
	return path.split("/")[2]

if __name__ == '__main__':
	main()


