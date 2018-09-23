import socket
import os
import sys, getopt

port = 12345
directory = "Download"
requests = 1
log_file_name = "download.log"
cookie_value = 0

def main(argv):
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
        # http://10.0.0.199:9898/hello.txt
        # s.connect(('10.0.0.199', 9898))
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
        print "length of response is ",  len(response)
        for i in range(2,len(response)):
            response[1] += '\n\n' + response[i]
        # print response[0]
        # print len(response[1])
        # print len(response[2])
        if os.path.exists(log_file_name):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        log_file = open(log_file_name, append_write)
        log_file.write(response[0] + '\n')
        log_file.close()
        # print "filename is " + filename
        if len(response) >= 2:
            if filename == '/':
                filename = '/index.html'
            # print "filename is " + filename
            file = open(directory + filename, "wb")
            file.write(response[1])
            file.close()

        s.close()

if __name__ == '__main__':
    main(sys.argv[1:])
    

