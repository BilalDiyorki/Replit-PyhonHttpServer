from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from templates import render_template
from user_new import User


class MyRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    parsed_url = urlparse(self.path)
    path = parsed_url.path

    if path == '/':
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      context = {}
      content = render_template('index.html', context)
      self.wfile.write(content.encode())

    elif path == '/login':
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      context = {}
      content = render_template('login.html', context)
      self.wfile.write(content.encode())

    elif path == '/register':
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      context = {}
      content = render_template('register.html', context)
      self.wfile.write(content.encode())

    elif path == '/home':
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      # Tüm kullanıcıları al
      # Tüm kullanıcıları al
      users = User.get_all_users()

      # Kullanıcıları HTML tablosuna dönüştür
      user_table = '<tbody>'
      for user in users:
        user_table += f'<tr><td>{user["first_name"]}</td><td>{user["last_name"]}</td><td>{user["username"]}</td><td data-genel-anahtar="{user["genel_anahtar_base64"]}">{user["genel_anahtar_base64"][:7]} ...</td><td><button class="btn btn-primary copy-button">Copy</button></td></tr>'
      user_table += '</tbody>'

      context = {'user_table': user_table}
      content = render_template('home_new.html', context)
      self.wfile.write(content.encode())

    else:
      self.send_response(404)
      self.end_headers()
      self.wfile.write("404 Not Found".encode())

  def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    parsed_data = parse_qs(post_data)

    if self.path == '/register':

      print("register post edildi")
      print("register post edildi")
      print("register post edildi")

      print("parsed_data['firstname'][0]")
      print(parsed_data['firstname'][0])
      print("parsed_data['lastname'][0]")
      print(parsed_data['lastname'][0])
      print("parsed_data['username'][0]")
      print(parsed_data['username'][0])
      print("parsed_data['password'][0]")
      print(parsed_data['password'][0])

      # Formdan gelen verileri al
      firstname = parsed_data['firstname'][0]
      lastname = parsed_data['lastname'][0]
      username = parsed_data['username'][0]
      password = parsed_data['password'][0]

      print("username")
      print(username)
      print("firstname")
      print(firstname)
      print("lastname")
      print(lastname)
      print("password")
      print(password)

    # Yeni kullanıcı oluştur ve veritabanına kaydet
    new_user = User(username, firstname, lastname, password)
    new_user.save()

    # Yönlendirme yap
    self.send_response(302)
    self.send_header('Location', '/home')
    self.end_headers()


def run(server_class=HTTPServer, handler_class=MyRequestHandler, port=8000):
  server_address = ('', port)
  httpd = server_class(server_address, handler_class)
  print(f"Starting server on port {port}")
  httpd.serve_forever()


if __name__ == '__main__':
  run()
