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
            self.lable = str_array[2]
            rstore_handle.init_restore(self.task_id, self.lable)
            self.send_msg('init:success')
            logging.info("get int msg success\n")

        while(True):
            new_msg = self.recv_msg()
            str_array = new_msg.split('#')

            cmd_type = str_array[0]

            if(cmd_type == 'fs'):
                fs_time_start = time.time()
                fs_name = self.task_id + '-fs.tar'
                fs_size = int(str_array[1])
                msg = "fs:"
                if self.recv_file(fs_name, fs_size):
                    msg += "sucess"
                else:
                    msg += "failed"
                self.send_msg(msg)

                rstore_handle.restore_fs()
                fs_time_end = time.time()

            if(cmd_type == 'premm'):
                pre_restore_time_start = time.time()
                premm_name = self.task_id + str_array[1]+'.tar'
                premm_size = int(str_array[2])
                if not self.recv_file(premm_name, premm_size):
                    self.send_msg('premm:error')
                else:
                    self.send_msg('premm:success')

                logging.debug('receive premm end..')
                rstore_handle.premm_restore(premm_name, str_array[1])
                pre_restore_time_end = time.time()

            if(cmd_type == 'mm'):
                restore_time_start = time.time()
                mm_name = self.task_id + '-mm.tar'
                mm_size = int(str_array[1])
                last_pre_dir = str_array[2]
                if(last_pre_dir != 'pre0'):
                    os.rename(last_pre_dir, 'pre')

                if not self.recv_file(mm_name, mm_size):
                    self.send_msg('mm:error')
                else:
                    self.send_msg('mm:success')

                restore_dump_img_time = time.time()

                logging.debug('receive mm end..')
                rstore_handle.restore(mm_name)
                restore_end_time = time.time()

                self.send_msg('restore:success')
                break

        # this is just for test.
        '''
        print('pre restore time:%f' %
              (pre_restore_time_end - pre_restore_time_start))
        print('recv file time:%f' %
              (restore_dump_img_time - restore_time_start))
        print('restore process time:%f' %
              (restore_end_time - restore_dump_img_time))
        '''
        cmd = 'docker ps -a '
        out = sp.call(cmd, shell=True)
        print(out)


class daemon:

    def run(self):
        host = ni.ifaddresses('eth1')[2][0]['addr']
        #port is defined in cloudlet_utl
        logging.info(host)
        server = ThreadedTCPServer((host, port), cloudlet_handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.debug(' stop by kebboard interrupt.')
            server.shutdown()
            server.server_close()
