#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import json
import logging
from docker import Client
from cloudlet_utl import *
import subprocess as sp
# check_status = False #after check , this should be true.

docker_api_version = ''


def cloudlet_check():
    logging.info("validate checking ...")
    if (docker_check() and criu_check() and docker_py_check()) is False:
        logging.error('cloudlet environment check failed')
        return False

    print('ok, your system seems good')
    return True


def docker_check():

    docker_version = sp.check_output('docker version', shell=True)
    lines = docker_version.split('\n')
    for line in lines:
        if 'API version' in line:
            global docker_api_version
            docker_api_version = line.split(':')[1]
            docker_api_version = ''.join(docker_api_version.split())

    if not docker_api_version:
        logging.error('Docker version failed')
        return False

    print('docker api version:' + docker_api_version)
    return True


def criu_check():
    out = sp.check_output('criu check', shell=True)
    if 'Error' in out:
        logging.error('criu check failed')
        return Fase
    else:
        logging.info('criu check ok')

    criu_info = sp.check_output('criu -V', shell=True)
    lines = criu_info.split('\n')
    for line in lines:
        if 'Version' in line:
            print('criu ' + line)
            return True

    return False


def docker_py_check():
    global docker_api_version
    if isBlank(docker_api_version):
        logging.error('criu check failed [inner issue happen]')

    cli = Client(version=docker_api_version)
    to_json = json.dumps(cli.info())
    # print(to_json)
    json_info = json.loads(to_json)
    if json_info['Driver'] != 'aufs':
        logging.error('sorry,just support aufs now.')
        return False
    print(json_info['OperatingSystem'] + ','),
    print(json_info['KernelVersion'])
    logging.debug('docker py works')
    return True
