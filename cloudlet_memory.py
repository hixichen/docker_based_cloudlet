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
        os.chdir(self.workdir())

    def workdir(self):
        return base_dir + 'tmp/' + self.task_id + '/'

    def premm_img_path(self):
        return self.workdir() + self.task_id + '-pre.tar.gz'

    def mm_img_path(self):
        return self.workdir() + self.task_id + '-mm.tar.gz'

    def predump(self,pid):

        img_dir = './pre'
        os.mkdir(img_dir)

        pre_img_path= self.workdir() + img_dir

        predump_sh = 'criu pre-dump -o dump.log -v2 -t ' + \
            str(pid) + ' --images-dir ' + pre_img_path

        logging.info(predump_sh)

        out_msg = sp.call(predump_sh, shell=True)
        if out_msg:
            logging.error('criu dump failed')
            return False
        # package it.
        name = self.task_id + '-pre.tar.gz'
        self.pack_img(self.workdir(), name, img_dir)
        return True

    def pack_img(self,dir, name, path):
        os.chdir(dir)
        tar_file = tarfile.open(name, 'w:gz')
        tar_file.add(path)
        tar_file.close()

        if not check_file(name):
            logging.error("package failed")
            return False
        return True

    def dump(self, con):
        logging.debug(con)
        mm_dir = './mm'
        #image_dir = self.workdir() + mm_dir
        os.mkdir(mm_dir)
        img_path=self.workdir()+ mm_dir
        checkpoint_sh = 'docker checkpoint --image-dir=' + \
            img_path + ' ' + ' --work-dir=' + img_path + ' --allow-tcp=true ' + con
        logging.debug(checkpoint_sh)

        out_msg = sp.call(checkpoint_sh, shell=True)
        if out_msg:
            logging.error('criu dump failed')
            return False

        name = self.task_id + '-mm.tar.gz'  # eg: /tmp/mytest.tar.gz

        self.pack_img(self.workdir(), name, mm_dir)
        return True
