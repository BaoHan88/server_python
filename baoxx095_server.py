#!/usr/bin/env python3
# See https://docs.python.org/3.2/library/socket.html
# for a description of python socket and its parameters
import socket

from threading import Thread
from argparse import ArgumentParser

BUFSIZE = 4096

def client_talk(client_sock, client_addr):
    req = ""
    code = 200 # default to 200
    print('talking to {}'.format(client_addr))
    
    data = client_sock.recv(BUFSIZE)
    #currently only processing simple requests so buffersize of 4096 is sufficient
    # while data:
      # print(data.decode('utf-8'))
      # req = req + data.decode('utf-8')
      # print("data: " + data.decode('utf-8'))
      # print("req: "+req)
      # data = client_sock.recv(BUFSIZE)
    ############################################
    req = req + data.decode('utf-8')
    print("debug: " + req)
    req_method = req.split(' ')[0]
    print("req!!!: ", req_method)
    #pagehtml
    
    #test for csumn
    res = req.split(' ')[1].split('?')[0].split('/')
    length = len(res)
    res = res[length-1]
    if "csumn" in res:
        print("Error code 301: Moved Permanently!")
        response = "HTTP/1.1 301 Moved Permanently\r\nLocation: https://www.cs.umn.edu"
        response =  response.encode()
        client_sock.send(response)
        client_sock.shutdown(1)
        client_sock.close()
        print('connection closed.')
        return
    
    if (req_method == 'GET') | (req_method == 'HEAD'):
        req_page = req.split(' ')[1].split('?')[0].replace('/','')
        
        print("requested page: " + req_page)
        try:
            fpage = open(req_page,'rb')
            if req_method == 'GET':
                pagehtml = fpage.read()
            fpage.close()
        
        except Exception as e: #no page or no permission for access
            #check e
            print("error: " + str(e))
            
            if ("Permission denied" in str(e)) | ("Errno 13" in str(e)):
                print ("Permission denied\n")
                code = 403
                fpage = open("403.html",'rb')
                if req_method == 'GET':
                   pagehtml = fpage.read()
                fpage.close()
            elif ("No such file or directory" in str(e)) | ("Errno 2" in str(e)):
                print ("Error 404, File Not Found\n")
                code = 404
                fpage = open("404.html",'rb')
                if req_method == 'GET':
                   pagehtml = fpage.read()
                fpage.close()
        

        #test for error 406
        if req_method == 'GET':
            req_all = req.split('\n')
            req_accept = ""
            for i in range(1, len(req_all)):
                req_accept = req_accept + req_all[i]
            
            print(req_accept)
            print(req_page.split('.')[1])
            if req_page.split('.')[1] not in req_accept:
                print ("Error 406, Requested File Not Accepted!\n")
                code = 406
                pagehtml = "<html><body><h1>Requested File Not Accepted<\h1></body></html>"
                pagehtml = pagehtml.encode()
        
        header = ''
        if code == 200:
           header = 'HTTP/1.1 200 OK\r\n'
        elif code == 404:
           header = 'HTTP/1.1 404 Not Found\r\n'
        elif code == 403:
           header = 'HTTP/1.1 403 Forbidden\r\n'
        elif code == 406:
           header = 'HTTP/1.1 406 Not Accepted\r\n'
           
        response = header
        if req_method == 'GET':
            response =  response+ 'Content-type:text/html;charset=utf8\r\n\r\n' + pagehtml.decode('ascii')
        
        response =  response.encode()
        
        print(response)
        client_sock.send(response)

    elif req_method == 'POST':
        print("POST!!")
        req_all = req.split('\n')
        formdata = req_all[len(req_all)-1]
        formlist = formdata.split('&')
        print(formlist)
        text = "<h2>Following Form Data Submitted Successfully</h2>"
        for i in range(0,len(formlist)):
            formelement = formlist[i].split('=')
            if "%3A" in formelement[1]:
                formelement[1] = formelement[1].replace('%3A',':')
            text = text + "<p>" + formelement[0] + ": " + formelement[1] +"</p>"
        text = "<html><body>" + text + "</body></html>"
        header = 'HTTP/1.1 200 OK\r\n'
        response = header + 'Content-type:text/html;charset=utf8\r\n\r\n' + text
        response =  response.encode()
        
        print(response)
        client_sock.send(response)
    else:
        print("ERROR 405 Method Not Allowed")
        code = 405
        response="HTTP/1.1 405 Method Not Allowed\r\nContent-type:text/html;charset=utf8\r\n\r\n<html><body><h1>Method Not Allowed<\h1></body></html>"
        response =  response.encode()
        client_sock.send(response)
    #############################################
    # clean up
    client_sock.shutdown(1)
    client_sock.close()
    print('connection closed.')

class EchoServer:
  def __init__(self, host, port):
    print('listening on port {}'.format(port))
    self.host = host
    self.port = port

    self.setup_socket()

    self.accept()

    self.sock.shutdown()
    self.sock.close()

  def setup_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.host, self.port))
    self.sock.listen(128)

  def accept(self):
    while True:
      (client, address) = self.sock.accept()
      th = Thread(target=client_talk, args=(client, address))
      th.start()

def parse_args():
  parser = ArgumentParser()
  parser.add_argument('--host', type=str, default='localhost',
                      help='specify a host to operate on (default: localhost)')
  parser.add_argument('-p', '--port', type=int, default=9001,
                      help='specify a port to operate on (default: 9001)')
  args = parser.parse_args()
  print(args)
  return (args.host, args.port)


if __name__ == '__main__':
  (host, port) = parse_args()
  EchoServer(host, port)

