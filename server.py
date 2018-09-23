import socket
import sys
import os, stat
import threading
import time
import json
from Queue import *
import time

directory = "Upload"
cookie_key = "id"
banned_ips = set()

cookie_count = 0
client_ip_addr_map = {}
cookie_last_number_visit_map = {}

def get_file_type(file_name):
    if file_name.endswith(".jpg"):
        mimetype = 'image/jpg'
    elif file_name.endswith(".png"):
        mimetype = 'image/png'
    else:
        mimetype = 'text/html'
    return mimetype

def get_cookie_header(cookie_value):
    # print "cookie value is ", cookie_value, " test"
    if cookie_last_number_visit_map.has_key(cookie_value):
        # print "cookie value ", cookie_value, " exists"
        cookie_dictionary = cookie_last_number_visit_map[cookie_value]
        visit_count = cookie_dictionary['count']
        cookie_dictionary['count'] = visit_count+1
        cookie_dictionary['last_visit'] = time.ctime(time.time())
    else:
        cookie_dictionary = {'count': 1, 'last_visit': time.ctime(time.time())}
        cookie_last_number_visit_map[cookie_value] = cookie_dictionary

    cookie_header = "Set-Cookie: your_identifier=" + str(cookie_value)
    return cookie_header

def parse(request):
    response_code = '400 Bad Request'
    http_version = 'HTTP/1.0'
    response_headers = ''
    headers = request.splitlines()
    cookie_value = None
    for header in headers:
        cookie_fields = header.split(':')
        if cookie_fields[0] == 'Cookie':
            cookie_value = cookie_fields[1].split('=')[1].strip()
    if cookie_value is None:
        cookie_value = cookie_count
        cookie_count += 1     

    # print headers
    header_fields = headers[0].split(' ')
    request_type = header_fields[0].strip()
    if request_type != "GET" and request_type != 'HEAD':
        raise Exception('Unknown request type method')

    if header_fields[1] == '/':
        file_name = directory + "/index.html"
    else:
        file_name = directory + header_fields[1]
    http_version = header_fields[2]
    response_code = '200 OK'
    content_length = None
    file_content = None
    cookie_header = get_cookie_header(cookie_value)

    try:
        accessCode = oct(stat.S_IMODE(os.stat(file_name).st_mode))
        global_permission = int(accessCode[3])
        if global_permission < 4:
            raise Exception('File does not have read permission to public')
        if os.path.isfile(file_name):
            content_length = os.path.getsize(file_name)
            mimetype = get_file_type(file_name)
            if request_type == 'GET':
                with open(file_name, mode = 'rb') as file:
                    file_content = file.read()
        else:
            response_code = '404 NOT FOUND'
    except Exception, e:
        # print e
        response_code = '403 FORBIDDEN'

    response_header1 = http_version + ' ' + response_code
    response_headers += response_header1
    if content_length is not None:
        response_header2 = "Content-Length: " + str(content_length)
        response_headers += '\n' + response_header2
        response_header3 = 'Content-Type: ' + mimetype
        response_headers += '\n' + response_header3

    response_headers += '\n' + cookie_header
    date_header = "\nDate: " + str(time.ctime(time.time()))
    if file_content is None:
        response_headers += date_header
        return response_headers + '\n'
    response_headers += date_header
    print "content length is ", len(file_content)
    return response_headers + '\n\n' + file_content + '\n'

def listen_to_client(connection, client_addr):
    print "client ip addr is ", client_addr
    request = ''
    request = connection.recv(4096)
    try:
        response = parse(request)
    except Exception:
        response = "HTTP/1.0 400 Bad Request\n"
    connection.send(response)
    connection.close()

def get_429_response(connection, client_ip):
    print client_ip, " is banned"
    response = "HTTP/1.0 429 TOO MANY REQUESTS"
    connection.send(response)
    connection.close()

def main(argv):
    s = socket.socket()

    port = 12345

    if len(argv) != 0:
        port = int(argv[0])

    print "listening at port ", port
    s.bind(('', port))
    s.listen(5)

    while True:
        connection, client_addr = s.accept()
        client_ip = client_addr[0]

        '''
        check if client already banned or not
        '''
        if client_ip in banned_ips:
            get_429_response(connection, client_ip)
            continue

        '''
        if client is not banned yet, check whether this request is more than 100th in the last 1 minute
        '''
        if client_ip_addr_map.has_key(client_ip):
            timestamp_queue = client_ip_addr_map[client_ip]
        else:
            timestamp_queue = Queue()
            client_ip_addr_map[client_ip] = timestamp_queue
        ts = int(time.time())
        # print "timestamp now is ", ts
        if timestamp_queue.qsize() == 100:
            last_timestamp = timestamp_queue.get()

            #this checks if the client can be banned or not
            time_difference = ts - last_timestamp
            # print "time difference is ", time_difference
            if time_difference <= 60:
                banned_ips.add(client_ip)
                get_429_response(connection, client_ip)
                continue
            else:
                timestamp_queue.put(ts)
        else:
            timestamp_queue.put(ts)

        # print "requests made by client are ", timestamp_queue.qsize()
        '''
        if client is not banned, then serve the request in a new thread
        '''
        threading.Thread(target = listen_to_client, args = (connection, client_addr)).start()


if __name__ == '__main__':
    try:
        if os.path.isfile('cookies.json'):
            with open('cookies.json') as fp:
                json_dump = json.loads(fp.read())
                if len(json_dump) == 2:
                    cookie_count = json_dump['cookie_count']
                    cookie_last_number_visit_map = json_dump['cookie_dictionary']
        main(sys.argv[1:])
    except KeyboardInterrupt:
        with open('cookies.json', 'wb') as fp:
            json_dump = {'cookie_count':cookie_count, 'cookie_dictionary':cookie_last_number_visit_map}
            json.dump(json_dump, fp)
