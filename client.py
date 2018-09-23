import socket
import os

port = 12345
directory = "Download"
requests = 2
log_file_name = "download.log"
cookie_value = 0
for i in range(requests):
    #default for socket() is AF_INET i.e. ipv4 addresses and SOCK_STREAM i.e. TCP connection
    s = socket.socket()
    # http://10.0.0.199:9898/hello.txt
    # s.connect(('10.0.0.199', 9898))
    s.connect(('127.0.0.1', port))
    http_version = 'HTTP/1.0'
    filename = '/best_results_dtree.png'
    # filename = '/hello.txt'
    request_type = 'GET'
    request = request_type + ' ' + filename + ' ' + http_version + '\n'
    request += 'Host: 127.0.0.1:' + str(port) + '\n'

    #add cookie header
    request += 'Cookie:your_identifier=' + str(cookie_value)
    s.send(request)
    response = ''
    data = s.recv(1024)
    while data != '':
        response += data
        try:
            data = s.recv(1024)
        except Exception:
            data = ''

    response = response.split('\n\n')
    
    print response[0]
    if os.path.exists(log_file_name):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    log_file = open(log_file_name, append_write)
    log_file.write(response[0] + '\n')
    log_file.close()
    if len(response) == 2:
        if filename == '/':
            filename = '/index.html'
        file = open(directory + filename, "wb")
        file.write(response[1])
        file.close()

    s.close()
    

