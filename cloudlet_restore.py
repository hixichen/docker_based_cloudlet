#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import logging
import commands
import shutil
import tarfile
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_memory import cloudlet_memory
from cloudlet_utl import *
import subprocess as sp


class restore:

    """docstring for ClassName"""

    def __init__(self):
        os.chdir(base_dir + '/tmp/')

    def init_restore(self, task_id, label):
        # set work dir.
        os.mkdir(task_id)
        os.chdir(task_id)
        self.task_id = task_id

        label_ar = label.split('-')
        con_name = label_ar[0]
        base_img = label_ar[1]
        img_id = label_ar[2]

        logging.debug('keep image id for verify %s ' % img_id)
        logging.debug(label_ar)

        cmd_option = 'docker run --name=foo -d ' + base_img + \
            ' tail -f /dev/null && docker rm -f foo'
        os.system(cmd_option)

        delete_op = 'docker rm -f ' + con_name + ' >/dev/null 2>&1'
        os.system(delete_op)

        create_op = 'docker create --name=' + con_name + ' ' + base_img
        logging.debug(create_op)
        ret, id = commands.getstatusoutput(create_op)
        self.con_id = id

    def workdir(self):
        return base_dir + '/tmp/' + self.task_id

    def restore_fs(self):

        restore_filesystem = cloudlet_filesystem(self.con_id, self.task_id)
        if restore_filesystem.restore() is False:
            logging.error('filesystem restore failed\n')
            return False

        return True

    def unpack_img(self, name):
        os.chdir(self.workdir())
        if not check_file(name):
            logging.error('file() not exist ,maybe receive error' % dump_mm)
            return False

        t = tarfile.open(name, "r:gz")
        t.extractall()
        t.close()
        return True

    def premm_restore(self, premm_name):
        self.unpack_img(premm_name)

    def restore(self, mm_img_name):
        self.unpack_img(mm_img_name)
        image_dir = self.workdir() + '/mm'

        restore_op = 'docker restore --force=true --work-dir=' + image_dir +\
            ' --image-dir=' + image_dir + ' ' + self.con_id

        logging.debug(restore_op)

        if sp.call(restore_op, shell=True) != 0:
            logging.error('criu restore failed')
            return False

        shutil.rmtree(self.workdir())
        return True
