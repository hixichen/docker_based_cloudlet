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

Test:
	- python 2.7.
	- ubuntu 14.04.

'''

import os
import tarfile
import commands
import time
import json
import shutil
#from docker import Client

def sythesis_overlay(overlay,base_image):
    #overlay file.
    t1 = time.time()
 
    if os.path.isfile(overlay) == False:
	print("error: overlay file is not exit")
	exit(0)
 
    if os.path.isfile(base_image) == False:
	print("error: base image is not exit")
	exit(0)
    
    syn_image = 'synthesis.tar'

    #caeate new tar file.
    if os.path.exists(syn_image):
          os.remove(syn_image) 
  
    newtar = tarfile.TarFile.open(syn_image,'w')
    path = './synth_temp'
    os.mkdir(path)
    basetar = tarfile.TarFile.open(base_image,'r')
    basetar.extractall(path)
    basetar.close()

    #base tar file.
    tar = tarfile.TarFile.open(overlay,'r:gz')
    tar.extractall(path)
    tar.close()
    os.chdir(path)
    newtar.add('./')	
    newtar.close()
    t2 = time.time()
      #docker load.
    os.chdir('../')
    shutil.rmtree(path)
    cmd = 'docker load -i ' + syn_image
    os.system(cmd)
    t3 = time.time()

    print t2-t1, "first stage time"   
    print t3-t2,"load time"
    #if everythin goes well, delete the tar file.
    #os.remove(syn_image) 

    '''
    cli = Client(version='1.21')  
    cli.load_image('synthesis.tar') #issue happen.
    cli.history()
    '''
    #check and verify.

#main function.
if __name__ == '__main__':
    sythesis_overlay("overlay.tar.gz","ubuntu.tar")
    exit();
