import socket
import os
import sys, getopt

port = 12345
directory = "Download"
log_file_name = "download.log"
cookie_value = 0

def main(argv):
    requests = 1
    if len(argv) < 4:
        print "Usage: python client.py serverHost serverPort filename command -d(optional) number_of_Requests"
    else:
        server_host = argv[0]
        port = int(argv[1])
        filename = argv[2]
        request_type = argv[3]
        if len(argv) == 6:
            requests = int(argv[5])
    for i in range(requests):
        #default for socket() is AF_INET i.e. ipv4 addresses and SOCK_STREAM i.e. TCP connection
        s = socket.socket()
        s.connect((server_host, port))
        http_version = 'HTTP/1.0'
        request = request_type + ' ' + filename + ' ' + http_version + '\n'
        request += 'Host: 127.0.0.1:' + str(port) + '\n'

        #add cookie header
        request += 'Cookie:your_identifier=' + str(cookie_value)
        s.send(request)
        response = ''
        data = s.recv(1024*100)
        while data != '':
            response += data
            try:
                data = s.recv(1024)
            except Exception:
                data = ''

        response = response.split('\n\n')
        for i in range(2,len(response)):
            response[1] += '\n\n' + response[i]
        if os.path.exists(log_file_name):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        log_file = open(log_file_name, append_write)
        log_file.write(response[0] + '\n')
        log_file.close()
        if len(response) >= 2:
            if filename == '/':
                filename = '/index.html'
            file = open(directory + filename, "wb")
            file.write(response[1])
            file.close()

        s.close()

if __name__ == '__main__':
    main(sys.argv[1:])
    

