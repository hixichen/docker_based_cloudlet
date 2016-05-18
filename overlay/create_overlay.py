#usr/bin/env /usr/local/bin/python
#encoding: utf-8

'''
author: chen xi
Description:
	Tiny demo for synthesis the overlay cross nodes.
	overlay: extract Docker layers.
	layer info:
		Json file: /var/lib/docker/graph
		layer tar file: /var/lib/docker/aufs/diff
		version :   1.0

		modify repositories in '/' directory.

Test:
	- python 2.7.
	- ubuntu 14.04.

'''

import os
import sys
import tarfile
import commands
import subprocess
import time
import json
import shutil
from docker import Client

def manual():
    print("python  modified_image_name  base_image_name ")

def get_input_images():
   cli = Client(version='1.21')  
   if len(sys.argv) != 3:
	print("input argument is not correct\n");
	manual()
	modified_image = raw_input("please enter the name of the modified image:\n")
	base_image = raw_input("please enter the base image name:\n");
   else:
	modified_image = sys.argv[1]
	base_image = sys.argv[2]

   to_json_m = json.dumps(cli.history(modified_image))
   json_m = json.loads(to_json_m)
   tag = (json_m[0]['Tags'])
   name,version = str(tag).split(":")
   name = name.split("'")[1]
   version = version.split("'")[0]
   id = (json_m[0]['Id'])
   label = name + ":" + version + ":" + id
   #print(label)

   to_json_b = json.dumps(cli.history(base_image))
   json_b = json.loads(to_json_b) 
   
   #get layer id.
   set_b = set()
   for item in json_b:
	set_b.add(item['Id'])
   
   layers_set = set()
   for item in json_m:
	layer_id = item['Id']
	if not layer_id in set_b:
	    layers_set.add(layer_id)

   if len(layers_set) ==0:
	print("error: donot find image Id\n")
   
   return label,layers_set

def extract_layers(label,set):
    #print(len(set))
    if len(set) == 0 :
	raise NameError('there is no input layer id')

    #get the layer contents.
    root_path = 'overlay'
    if os.path.exists(root_path):
	shutil.rmtree(root_path)

    os.mkdir(root_path)
    os.chdir(root_path)
    while len(set) > 0:#currently, we just extract the top lay.
        id = set.pop()
        os.mkdir(id)
        os.chdir(id)
	json_file = "/var/lib/docker/graph/"+ id + "/json"
	#copy 
        os.system("cp "+ json_file+ " ./")
        os.chmod("json",0644)
        f = open("VERSION","w")
        f.write('1.0')
        f.close()      
        layer_path = "/var/lib/docker/aufs/diff/" + id +'/'

        tar_file = tarfile.TarFile.open("layer.tar",'w')
	tar_file.add(layer_path,arcname=os.path.basename(layer_path))	
	tar_file.close()
        os.chdir("../")

    repos_file = open("repositories","w")

    cont = '{"name":{"version":"id"}}\n'
    image = label.split(":")
    #print(image)
    cont = cont.replace("name",image[0])
    cont = cont.replace("version",image[1])
    cont = cont.replace("id",image[2])     
    repos_file.write(cont)
    repos_file.close()      
 
    ol_file = 'overlay.tar.gz'
    overlay_tar = tarfile.open(ol_file,'w:gz')
    overlay_tar.add('./')
    overlay_tar.close()
    #exit(0)

    if os.path.exists('../overlay.tar.gz'):
          os.remove('../overlay.tar.gz') 

    shutil.move('overlay.tar.gz','../')
    #we need to delete overlay directory
    #currently, keep it for debug
    os.chdir('../')
    #exit(0)
    shutil.rmtree(root_path)
    print("sucess generate overlay.tar.gz\n")


#main function.
if __name__ == '__main__':
    tag,set = get_input_images()
    extract_layers(tag,set)
    exit();
