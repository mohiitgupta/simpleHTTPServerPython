In this lab:
1. I create a socket
2. I bind it to a specific address and port 
3. I send and receive a HTTP packet from client to server
4. I send a cookie header to every new client that sends me request so that I can identify it for future requests. The database is stored in cookies.json. Kindly note that I write to cookies.json when the server is shutdown using keyboard interrupt.
5. The server is a multithreaded server and can serve upto 5 requests in parallel i.e. the limit on the queue size for the socket. I take a lock on the cookie_counter which is incremented and provided to every new client which connects to it. Also I take a lock on the cookie to last visit date, total visit map whenever a thread modifies it.
5. The client stores the logs in download.log file.
6. The server has inbuilt mechanism to prevent Denial of Service (DOS) attacks. Currently, if there are more than 100 requests from a particular client ip address in the past 1 minute, then the ip is permanently banned. Everytime, the server is restarted, this is refreshed.


to run the server kindly run python server.py 45677
to run the client kindly run python client.py 127.0.0.1 45677 /hello.txt GET -d 100

The response codes are:
200 OK when the request is served successfully without error by the server to the client
400 Bad Request when the request is malformed for example if client sends a POST request which is not supported by the server
403 Forbidden when the file being requested by the client does not have read permission to the public
404 Not found when the file being requested by the client is not present in the Upload directory of the server

I have the Upload directory from where server checks for the file being requested by the client
I have Download directory where the client saves the file with the same name as entered on command line with the content if GET request or with the metadata if HEAD request
In addition I have download.log file where the client logs the response headers for each response from the server.

My cookies are stored in cookies.json.

In this json, I have a map which stores the identifier for the cookie sent to the client which contains total visits by the client and last visit. It also has the counter used for cookie identifier which the server should give to the next new client which it has not served before.

 I have sample jpg, png, txt, html files in Upload folder.

