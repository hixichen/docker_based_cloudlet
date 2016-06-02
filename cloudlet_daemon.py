#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import netifaces as ni
import logging
import SocketServer  # for python 2.7,    sockerserver for python3.x
from cloudlet_restore import restore
from cloudlet_utl import *
import time
BUF_SIZE = 4096


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class cloudlet_handler(SocketServer.BaseRequestHandler):

    def recv_file(self, file_name, size):
        hd_file = open(file_name, 'wb')
        try:
            buffer = b''
            while True:
                data = self.request.recv(BUF_SIZE).strip()
                buffer = buffer + data
                if len(buffer) == size:
                    break
                if len(buffer) > size:
                    logging.error(
                        ' inner error: socket send file size donot match')

            hd_file.write(buffer)
            hd_file.close()
        except ConnectionError as conError:
            logging.error('connection error:conError:%s' % conError)

    def handle(self):

        data = self.request.recv(BUF_SIZE).strip()
        str_array = data.split(':')
        logging.debug(str_array)

        #msg = str_array[0]
        task_id = str_array[1]
        label = str_array[2]
        fs_size = int(str_array[3])
        mm_size = int(str_array[4])
        # just for debug.
        start_time = str_array[5]

        self.request.send('msg:success\n')

        os.chdir(base_dir + '/tmp')
        # os.system('rm -fr *') #just for tiny test
        os.mkdir(task_id)
        os.chdir(task_id)

        fs_name = task_id + '-fs.tar.gz'
        logging.debug('receiving mm file....')
        self.recv_file(fs_name, fs_size)
        self.request.send('fs:success\n')

        logging.debug('receiving mm file....')
        mm_name = task_id + '.tar.gz'
        self.recv_file(mm_name, mm_size)
        self.request.send('all:success\n')
        logging.debug('receive end..')

        restore(task_id, label)
        logging.debug('restore end..')
        end_time = time.time()
        print('migration time: %s' % (end_time - start_time))
        print('migration end time: %s' % end_time)


class daemon:

    def run(self):
        host = ni.ifaddresses('eth1')[2][0]['addr']
        port = 10018
        logging.info(host)
        server = ThreadedTCPServer((host, port), cloudlet_handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.debug(' stop by kebboard interrupt.')
