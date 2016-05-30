#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import socket
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_memory import cloudlet_memory
from docker import Client
from cloudlet_utl import *
import logging

BUF_SIZE = 4096


class cloudlet_socket:

    def __init__(self, dst_ip):
        PORT = 10018
        HOST = dst_ip

        logging.info('dst ip %s:' % HOST)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except Exception, e:
            print 'Error connecting to server:%s' % e
            return False

    def send_file(self, file_path):
        logging.debug('sending file ....')
        filehandle = open(file_path, 'rb')
        self.socket.sendall(filehandle.read())
        filehandle.close()
        logging.debug('send file end')

    def send(self, msg):
        self.socket.send(str(msg), BUF_SIZE)

    def close(self):
        self.socket.close()

    def recv(self):
        return self.socket.recv(BUF_SIZE)


def get_con_info(name):
    cli = Client(version='1.21')
    out = cli.inspect_container(name)
    if 'Error' in out:
        logging.error('get container id failed')
        return None, None

    image = out['Config']['Image']
    image_id = out['Image']
    label = name + '-' + image + '-' + image_id
    logging.info(label)

    return out['Id'], label


def check_container_status(id):
    cli = Client(version='1.21')
    out = cli.containers(id)
    print(out)
    lines = str(out)
    if 'Id' in lines:
        logging.info('id get by docker-py:%s' % out[0]['Id'])
        return True

    return False


class handoff:

    def __init__(self, con, dst_ip):
        self.dst_ip = dst_ip
        self.task_id = random_str()
        self.con = con
        self.con_id, self.label = get_con_info(con)

    def send_image(self, fs_image, mm_image):
        '''
        #information we try to send
          - task id
          - container based image info

        '''
        try:

            clet_socket = cloudlet_socket(self.dst_ip)
            logging.debug(mm_image)
            logging.debug(fs_image)

            fs_image_size = os.path.getsize(fs_image)
            mm_image_size = os.path.getsize(mm_image)

            msg = 'msg:' + self.task_id + ':' + self.label + \
                ':' + str(fs_image_size) + ':' + str(mm_image_size)

            logging.debug(msg)

            clet_socket.send(msg)

            data = clet_socket.recv()
            if 'success' not in data:
                logging.error('send msg failed\n')
                return False
            logging.debug(data)

            clet_socket.send_file(fs_image)

            data = clet_socket.recv()
            logging.debug(data)
            logging.debug('start send mm file ....')

            clet_socket.send_file(mm_image)

            data = clet_socket.recv()
            if 'success' not in data:
                logging.error('send msg failed\n')
                return False
            logging.debug(data)

            clet_socket.close()

            return True
        except Exception, e:
            print 'Error,socket send/recv file  failed:%s' % e
            return False

    def run(self):

        fs_handle = cloudlet_filesystem(self.con_id, self.task_id)
        if not fs_handle.checkpoint():
            logging.error("extract file failed")
            return False

        if not check_container_status(self.con_id):
            logging.error("container is not runing,please check")
            return False

        mm_handle = cloudlet_memory(self.task_id)
        if not mm_handle.dump(self.con):
            logging.error("memory dump failed")
            return False

        self.send_image(fs_handle.image_path(), mm_handle.image_path())

        return True
