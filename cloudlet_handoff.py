#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import socket
import struct
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_memory import cloudlet_memory
from docker import Client
from cloudlet_utl import *
import logging
import time

start_time = ''

BUF_SIZE = 1024


class cloudlet_socket:

    def __init__(self, dst_ip):
        PORT = 10021
        HOST = dst_ip

        logging.info('dst ip %s:' % HOST)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except Exception, e:
            logging.error('Error connecting to server:%s' % e)
            return False

    def send_file(self, file_path):
        filehandle = open(file_path, 'rb')
        self.socket.sendall(filehandle.read())
        filehandle.close()

    def send(self, msg):
        length = len(msg)
        self.socket.sendall(struct.pack('!I', length))
        self.socket.sendall(msg)

    def close(self):
        self.socket.close()

    def recv(self):
        len_buf = self.socket.recv(4)
        length, = struct.unpack('!I', len_buf)
        return self.socket.recv(length)


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

    # get pid.
    pid = out['State']['Pid']
    logging.info(pid)

    return out['Id'], label, pid


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def check_container_status(id):
    cli = Client(version='1.21')
    out = cli.containers(id)
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
        self.con_id, self.label, self.pid = get_con_info(con)

    def run(self):
        start_time = time.time()

    #-----step1: check status.
        if not check_container_status(self.con_id):
            logging.error("container is not runing,please check")
            return False

        #---: we need to know the status of destionation node.
        #   for eaxmple, CRIU version and docker version.

        clet_socket = cloudlet_socket(self.dst_ip)
        msg = 'init#' + self.task_id + '#' + self.label
        clet_socket.send(msg)

        data = clet_socket.recv()
        if 'success' not in data:
            logging.error('send msg failed\n')
            return False

    #---step2: fils system:
        fs_handle = cloudlet_filesystem(self.con_id, self.task_id)
        if not fs_handle.checkpoint():
            logging.error("extract file failed")
            return False

        fs_img = fs_handle.image_path()
        msg_fs = 'fs#' + str(os.path.getsize(fs_img)) + '#'
        clet_socket.send(msg_fs)
        clet_socket.send_file(fs_img)
        data = clet_socket.recv()

        #logging.debug('start send predump mm file ....')

    #---step3: predump:
        pre_time_start = time.time()
        mm_handle = cloudlet_memory(self.task_id)
        if not mm_handle.predump(self.pid):
            return False

        premm_img = mm_handle.premm_img_path()
        premm_size = os.path.getsize(premm_img)
        # send predump image:
        msg_premm = 'premm#' + str(premm_size)+'#'
        clet_socket.send(msg_premm)
        send_pre_img_time = time.time()
        clet_socket.send_file(premm_img)

        data = clet_socket.recv()

        pre_time_end = time.time()
    #-----step4: dump and send the dump images.

        if not mm_handle.dump(self.con):
            logging.error("memory dump failed")
            return False

        mm_img = mm_handle.mm_img_path()
        mm_size = os.path.getsize(mm_img)
        msg_mm = 'mm#' + str(mm_size)+'#'
        clet_socket.send(msg_mm)
        clet_socket.send_file(mm_img)
        data = clet_socket.recv()
        # logging.debug(data)

        data = clet_socket.recv()
        # logging.debug(data)

        down_time_end = time.time()

        print("mm size: "+sizeof_fmt(mm_size))
        print('predump prepare time: %f ' % (send_pre_img_time - pre_time_start))
        print("predump mm size: "+sizeof_fmt(premm_size))
        premm_img_send_time = (pre_time_end - send_pre_img_time)
        print('send predump image time: %f ' % premm_img_send_time)
        print('measure bandwith:' +
              sizeof_fmt((premm_size*8)/(premm_img_send_time)) + '/s')

        print("mm size: "+sizeof_fmt(mm_size))
        print('migration total time: %f ' % (down_time_end - start_time))
        print('migration down time: %f  ' % (down_time_end - pre_time_end))

        return True
