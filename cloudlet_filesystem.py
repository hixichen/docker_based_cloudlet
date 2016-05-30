#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import tarfile
import shutil
import logging
from cloudlet_utl import *


class cloudlet_filesystem:

    def __init__(self, con_id, task_id):
        self.con_id = con_id
        self.task_id = task_id
        self.fs_tar_name = task_id + '-fs.tar.gz'
        self.con_tar = 'con.tar'
        self.con_init_tar = 'con-init.tar'

    def tar_file_without_path(self, con_tar, path):
        os.chdir(path)
        tar_file = tarfile.TarFile.open(con_tar, 'w')
        tar_file.add('./')
        tar_file.close()
        shutil.move(con_tar, self.workdir())
        os.chdir('../')

    def checkpoint(self):
        '''
          tar file in  /$(container_id)/
        '''
        os.mkdir(self.workdir())

        layer_dir = base_dir + 'aufs/diff/'
        con_path = layer_dir + self.con_id  # container id.

        if not check_dir(con_path):  # check path exist or not?
            logging.error('file path %s not exist' % con_path)
            return False
        con_tar = self.con_tar
        self.tar_file_without_path(con_tar, con_path)

        '''
         tar file in  /$(container_id)-init/
        '''
        con_init_path = con_path + '-init'
        if not check_dir(con_init_path):
            logging.error('path %s not exist' % con_init_path)
            return False

        con_init_tar = self.con_init_tar
        self.tar_file_without_path(con_init_tar, con_init_path)

        '''
           tar file in fs.tar.gz
        '''
        os.chdir(self.workdir())

        # check file exist
        if not (check_file(con_tar) and check_file(con_init_tar)):
            logging.error('extract fs layers failed')
            return false

        fs_tar_name = self.fs_tar_name
        fs_gz = tarfile.TarFile.open(fs_tar_name, 'w:gz')
        fs_gz.add(con_tar)
        fs_gz.add(con_init_tar)
        fs_gz.close()

        if not check_file(fs_tar_name):
            logging.error('extract fs layers failed')
            return False

        os.remove(con_tar)
        os.remove(con_init_tar)
        return True

    def workdir(self):
        return base_dir + 'tmp/' + self.task_id + '/'

    def image_path(self):
        return self.workdir() + '/' + self.fs_tar_name

    def untar_file_to_path(self, tar_file, path):
        tar = tarfile.TarFile.open(tar_file, 'r')
        tar.extractall(path)
        tar.close()
        os.remove(tar_file)

    def restore(self):
        '''
          extract file from fs.tar.gz
        '''
        # fs_tar_name file path
        os.chdir(self.workdir())

        fs_tar_name = self.fs_tar_name

        if not check_file(fs_tar_name):  # check file exist
            logging.error('fs file is not exist')
            return False
        fs_tar = tarfile.TarFile.open(fs_tar_name, 'r:gz')
        fs_tar.extractall()
        fs_tar.close()

        con_tar = self.con_tar
        con_init_tar = self.con_init_tar

        # check file exist
        if not (check_file(con_tar) and check_file(con_init_tar)):
            logging.error('inner error:fs extract file fail')
            return False

        '''
             put file to /$(container_id)/
        '''

        con_path = base_dir + 'aufs/diff/' + self.con_id  # container id.
        if not check_dir(con_path):
            logging.error('dir(%s)not exist' % con_path)
            return False

        self.untar_file_to_path(con_tar, con_path)

        '''
            put file to /$(container_id)-init/
        '''
        con_init_path = con_path + '-init'
        if not check_dir(con_init_path):
            return False

        self.untar_file_to_path(con_init_tar, con_init_path)

        # delete fs.tar.gz
        # os.remove(fs_tar_name)
        return True
