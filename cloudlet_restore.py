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
import time


def lz4_uncompress(in_name='memory.lz4', out_name='pages-1.img'):
    cmd = 'lz4 -d ' + in_name + ' ' + out_name
    logging.info(cmd)
    sp.call(cmd, shell=True)
    os.remove(in_name)


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

    def unpack_img(self, tar_ball, mm_dir):
        os.chdir(self.workdir())
        if not check_file(tar_ball):
            logging.error('file() not exist ,maybe receive error' % dump_mm)
            return False

        t = tarfile.open(tar_ball, "r")
        t.extractall()
        t.close()
        os.chdir(mm_dir)
        lz4_uncompress()
        os.chdir('../')
        return True

    def premm_restore(self, premm_name, mm_dir):
        self.unpack_img(premm_name, mm_dir)

    def restore(self, mm_img_name):
        self.unpack_img(mm_img_name, 'mm')
        image_dir = self.workdir() + '/mm'

        restore_op = 'docker restore --force=true --allow-tcp=true --work-dir=' \
            + image_dir + ' --image-dir=' + image_dir + ' ' + self.con_id

        logging.debug(restore_op)

        ret = sp.call(restore_op, shell=True)
        logging.info(ret)

        if ret != 0:
            logging.error('criu restore failed')
            return False

        # shutil.rmtree(self.workdir())
        return True
