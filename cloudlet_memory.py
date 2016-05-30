#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import os
import tarfile
import subprocess as sp
import commands
from cloudlet_check import cloudlet_check
from cloudlet_utl import *


class cloudlet_memory:

    def __init__(self, task_id):
        self.task_id = task_id

    def workdir(self):
        return base_dir + 'tmp/' + self.task_id + '/'

    def image_path(self):
        return self.workdir() + self.task_id + '.tar.gz'

    def dump(self, con):

        logging.debug(con)
        mm_dir = 'mm/'
        image_dir = self.workdir() + mm_dir
        os.mkdir(image_dir)
        checkpoint_sh = 'docker checkpoint --image-dir=' + \
            image_dir + ' ' + con
        logging.debug(checkpoint_sh)

        out_msg = sp.call(checkpoint_sh, shell=True)
        if out_msg:
            logging.error('criu dump failed')
            return False

        os.chdir(self.workdir())
        name = self.task_id + '.tar.gz'  # eg: /tmp/mytest.tar.gz
        tar_file = tarfile.open(name, 'w:gz')
        tar_file.add(mm_dir)
        tar_file.close()

        if not check_file(name):
            logging.error("tar memory dump info failed")
            return False
        return True

    def image_unpack(self):
        os.chdir(self.workdir())
        dump_mm = self.task_id + '.tar.gz'
        if not check_file(dump_mm):
            logging.error('file() not exist ,maybe receive error' % dump_mm)
            return False

        t = tarfile.open(dump_mm, "r:gz")
        t.extractall()
        t.close()

        if not check_dir('./mm'):
            logging.error('innner error, extract file failed')
            return False
        # os.remove(dump_mm)
        return True

    def restore(self, new_con_id):
        self.image_unpack()
        image_dir = self.workdir() + 'mm/'
        logging.debug(image_dir)

        restore_op = 'docker restore --force=true --image-dir=' + \
            image_dir + ' ' + new_con_id

        if sp.call(restore_op, shell=True) != 0:
            logging.error('criu restore failed')
            return False

        return True
