#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter03/tcp_sixteen.py
# Simple TCP client and server that send and receive 16 octets

import argparse 
import socket
import sys
import time
import glob
import os

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data

def server(interface, port):
    cek = 0
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((interface, port))
        sock.listen(1)
        sc, sockname = sock.accept()
        if cek==0:
            print('Waiting to accept a new connection...')
            print('We have accepted a connection from', sockname)
            cek+=1
        print('Socket name:', sc.getsockname())
        print('Socket peer:', sc.getpeername())
        len_msg = recvall(sc, 3)
        message = recvall(sc, int(len_msg))

        #Decode and split the client message
        recv_message = message.decode()
        split_message = recv_message.split()

        #Condition
        if split_message[0] == 'ping':
            str_messageJoin = ' '.join(split_message[1:])
            format1 = "terima: "
            bit_message = format1.encode() + str_messageJoin.encode()
            len_bit_message = b"%03d" % (len(bit_message.decode()),)
            sc.sendall(len_bit_message)
            sc.sendall(bit_message)

        elif split_message[0] == "ls":
            if len(split_message) == 1:
                files = '*'
            elif len(split_message) > 1:
                files = split_message[1]

            listed_files = glob.glob(files,recursive=True)
            return_files = ''
            for i in listed_files:
                basename = os.path.basename(i)
                return_files += basename + '\n'
            len_ret_files = b"%03d" % (len(return_files))
            sc.sendall(len_ret_files)
            bit_return_files = return_files.encode()
            sc.sendall(bit_return_files)

        elif split_message[0] == "get":
            p = os.path.dirname(split_message[1])
            names = split_message[2]
            sizes = 0
            for files in os.scandir(p):
                basename = os.path.basename(files)
                if basename.startswith(split_message[2]):
                    f = open(files,"rb")
                    b = f.read()
                    sizes += len(b)
                    f.close()
            size = str(sizes)
            space =" "
            format1 = "fetch: "
            format2 = "size: "
            format3 = "lokal: "
            
            return_message = format1.encode() + p.encode() + space.encode() + format2.encode() + size.encode() + space.encode() + format3.encode() + names.encode()
            len_ret_message = b"%03d" % (len(return_message.decode()),)
            sc.sendall(len_ret_message)
            sc.sendall(return_message)
        
        elif split_message[0] == "quit":
            print("Server shutdown..")
            sc.close()
            sys.exit(0)

def client(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print('Client has been assigned socket name', sock.getsockname())
        
        input_msg = input("> ")
        msgSplit = input_msg.split()
       
        if msgSplit[0] == "ping":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            len_recv = recvall(sock, 3)
            msg_recv = recvall(sock, int(len_recv))
            reply1 = msg_recv.decode()
            print(reply1)

        elif msgSplit[0] == "ls":
            if len(msgSplit) == 1:
                msg = input_msg.encode()
                len_msg = b"%03d" % (len(msg),)
                msg = len_msg + msg
                sock.sendall(msg)
                len_recv = recvall(sock, 3)
                msg_recv = recvall(sock, int(len_recv))
                reply1 = msg_recv.decode()
                print(reply1)

            elif len(msgSplit) > 1:
                msgJoin = ' '.join(msgSplit)
                msg = msgJoin.encode()
                len_msg = b"%03d" % (len(msg),)
                msg = len_msg + msg
                sock.sendall(msg)
                len_recv = recvall(sock, 3)
                msg_recv = recvall(sock, int(len_recv))
                reply1 = msg_recv.decode()
                print(reply1)

        elif msgSplit[0] == "get":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            len_recv = recvall(sock, 3)
            msg_recv = recvall(sock, int(len_recv))
            reply1 = msg_recv.decode()
            print(reply1)

        elif msgSplit[0] == "quit":
            msg = input_msg.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg) 
            time.sleep(2)
            print('Client shutdown...')
            sock.close()
            sys.exit(0)

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)