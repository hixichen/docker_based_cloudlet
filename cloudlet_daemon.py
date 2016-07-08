#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import netifaces as ni
import logging
import SocketServer  # for python 2.7,    sockerserver for python3.x
from cloudlet_restore import restore
from cloudlet_utl import *
import time
import struct


BUF_SIZE = 1024


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class cloudlet_handler(SocketServer.BaseRequestHandler):

    def recv_file(self, file_name, size):
        hd_file = open(file_name, 'wb')
        try:
            buffer = b''
            length = size
            while (length > 0):
                data = self.request.recv(length)
                if not data:
                    return False
                buffer += data
                length = size - len(buffer)

            hd_file.write(buffer)
            hd_file.close()
            return True

        except Exception as conError:
            logging.error('connection error:conError:%s' % conError)

    def send_msg(self, msg):
        length = len(msg)
        self.request.send(struct.pack('!I', length))
        self.request.send(msg)

    def recv_msg(self):
        len_buf = self.request.recv(4)
        length, = struct.unpack('!I', len_buf)
        return self.request.recv(length)

    def handle(self):
        data = self.recv_msg()
        str_array = data.split('#')
        rstore_handle = restore()
        cmd_type = str_array[0]

        if(cmd_type == 'init'):
            # do init job.
            self.task_id = str_array[1]
            lable = str_array[2]
            rstore_handle.init_restore(self.task_id, lable)
            self.send_msg('init:success')

        while(True):
            new_msg = self.recv_msg()
            str_array = new_msg.split('#')
            # logging.debug(str_array)

            cmd_type = str_array[0]

            if(cmd_type == 'fs'):
                fs_name = self.task_id + '-fs.tar.gz'
                fs_size = int(str_array[1])
                msg = "fs:"
                if self.recv_file(fs_name, fs_size):
                    msg += "sucess"
                else:
                    msg += "failed"
                self.send_msg(msg)

                rstore_handle.restore_fs()

            if(cmd_type == 'premm'):
                premm_name = self.task_id + '-pre.tar.gz'
                premm_size = int(str_array[1])
                #logging.info(premm_size)

                if not self.recv_file(premm_name, premm_size):
                    self.send_msg('premm:error')
                else:
                    self.send_msg('premm:success')

                #logging.debug('receive premm end..')
                rstore_handle.premm_restore(premm_name)

            if(cmd_type == 'mm'):
                mm_name = self.task_id + '-mm.tar.gz'
                mm_size = int(str_array[1])
                if not self.recv_file(mm_name, mm_size):
                    self.send_msg('mm:error')
                else:
                    self.send_msg('mm:success')

                #logging.debug('receive mm end..')
                rstore_handle.restore(mm_name)
                self.send_msg('restore:success')
                break

            #end_time = time.time()
            #print('migration time: %s' % (end_time - start_time))
            #print('migration end time: %s' % end_time)


class daemon:

    def run(self):
        host = ni.ifaddresses('eth1')[2][0]['addr']
        port = 10021
        logging.info(host)
        server = ThreadedTCPServer((host, port), cloudlet_handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.debug(' stop by kebboard interrupt.')
            server.shutdown()
            server.server_close()
