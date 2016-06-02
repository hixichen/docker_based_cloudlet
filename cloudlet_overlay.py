#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
'''
Description:
  Tiny demo for synthesis the overlay cross nodes.
  overlay: extract Docker layers.
  layer info:
    Json file: /var/lib/docker/graph
    layer tar file: /var/lib/docker/aufs/diff
    version :   1.0

    modify repositories in '/' directory.
'''

import os
import tarfile
import time
import json
import shutil
import logging

import subprocess as sp
from docker import Client
from cloudlet_utl import *


class overlay:

    def __init__(self, modified_image, base_image):
        self.m_image = modified_image
        self.base_image = base_image

    def get_image_label(self, image_name):
        cli = Client(version='1.21')
        to_json = json.dumps(cli.history(image_name))
        json_file = json.loads(to_json)
        tag = (json_file[0]['Tags'])
        name, version = str(tag).split(":")
        name = name.split("'")[1]
        version = version.split("'")[0]
        id = (json_file[0]['Id'])
        label = name + "-" + version + "-" + id
        logging.info(label)
        return label, json_file

    def get_images_info(self, modified_image, base_image):
        # TODO
        # docker_api_version = get_api_v()
        # logging.debug(api_v)

        self.label, json_m = self.get_image_label(modified_image)
        self.base_label, json_b = self.get_image_label(base_image)

        # get layer id.
        set_b = set()
        for item in json_b:
            set_b.add(item['Id'])

        layers_set = set()
        for item in json_m:
            layer_id = item['Id']
            if not layer_id in set_b:
                layers_set.add(layer_id)

        if len(layers_set) == 0:
            logging.error("error: donot find image Id\n")
            return False

        self.set = layers_set
        logging.debug(layers_set)
        return True

    def extract_layers(self, m_image):
        set = self.set
        # logging.info(set)
        if len(set) == 0:
            logging.error('there is no input layer id')

        # get the layer contents.
        root_path = '/tmp/' + m_image + '-overlay/'
        if os.path.exists(root_path):
            shutil.rmtree(root_path)
            logging.error('radom dir error')

        os.mkdir(root_path)
        os.chdir(root_path)
        while len(set) > 0:  # currently, we just extract the top lay.
            id = set.pop()
            os.mkdir(id)
            os.chdir(id)
            json_file = "/var/lib/docker/graph/" + id + "/json"
            # copy
            os.system("cp " + json_file + " ./")
            os.chmod("json", 0644)
            f = open("VERSION", "w")
            f.write('1.0')
            f.close()
            layer_path = "/var/lib/docker/aufs/diff/" + id + '/'

            tar_file = tarfile.TarFile.open("layer.tar", 'w')
            tar_file.add(layer_path, arcname=os.path.basename(layer_path))
            tar_file.close()
            os.chdir("../")

        repos_file = open("repositories", "w")

        cont = '{"name":{"version":"id"}}\n'
        temp_array = self.label.split("-")

        cont = cont.replace("name", temp_array[0])
        cont = cont.replace("version", temp_array[1])
        cont = cont.replace("id", temp_array[2])
        repos_file.write(cont)
        repos_file.close()
        logging.debug(cont)

        image_info = open("base_image", "w")
        image_info.write(self.base_label)
        image_info.close()

        ol_file = m_image + '-overlay.tar.gz'
        overlay_tar = tarfile.open(ol_file, 'w:gz')
        overlay_tar.add('./')
        overlay_tar.close()

        if os.path.exists('../' + ol_file):
            os.remove('../' + ol_file)

        shutil.move(ol_file, '../')
        # we need to delete overlay directory
        # currently, keep it for debug
        os.chdir('../')
        shutil.rmtree(root_path)
        print("sucess generate overlay file:/tmp/%s" % ol_file)
        return True

    def generate(self):
        if not self.get_images_info(self.m_image, self.base_image):
            logging.error('get_images_info failed')
            return False

        if not self.extract_layers(self.m_image):
            logging.error('extract_layers failed')
            return False

        return True

    def synthesis(self, overlay_file):
        
        # overlay file.
        syn_image = self.m_image + '-synthesis.tar'

        # caeate new tar file.
        if check_file(syn_image):
            os.remove(syn_image)

        logging.info(overlay_file)
        t1 = time.time()
        dir = random_str()
        os.mkdir(dir)

        overlay = tarfile.TarFile.open(overlay_file, 'r:gz')

        try:
            image_info = overlay.getmember('./base_image')
            info_file = overlay.extractfile(image_info)
            name, version, id = str(info_file.read()).split("-")
            info_file.close()

            base_file = name + '.tar'
            basetar = tarfile.TarFile.open(base_file, 'r')
            basetar.extractall(dir)
            basetar.close()
            # verify
            if not check_dir(dir + '/' + id):
                logging.error('!base image not match')
                return False

            overlay.extractall(dir)
            overlay.close()
            os.remove(dir + '/base_image')

            newtar = tarfile.TarFile.open(syn_image, 'w')
            newtar.add(dir + '/', arcname="./")
            newtar.close()

        except KeyError:
            logging.error('base image info not in overlay(%s)' % overlay_file)
        except OSError as err:
            logging.error(err)
        finally:
            shutil.rmtree(dir)

        t2 = time.time()
        # docker load.
        cmd = 'docker load -i ' + syn_image
        sp.call(cmd, shell=True)
        t3 = time.time()

        print("tar file time %s" % (t2 - t1))
        print("load time %s" % (t3 - t2))
        print("total synethsis time %s" % (t3 - t1))
        # if everythin goes well, delete the tar file.
        # os.remove(syn_image)

        '''
            cli = Client(version='1.21')  
            cli.load_image('synthesis.tar') #issue happen.
            cli.history()
          '''

        return True

    def fetch(self):
        m_image = self.m_image
        overlay_file = m_image + '-overlay.tar.gz'
        work_dir = '/tmp/'
        os.chdir(work_dir)

        if not check_file(overlay_file):
            logging.error("overlay file is not exit")
            return False
        else:
            if not self.synthesis(overlay_file):
                logging.error("overlay synthesis failed")
                return False

        return True
