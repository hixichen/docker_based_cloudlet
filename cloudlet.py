#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import sys
import logging

from cloudlet_check import cloudlet_check
from cloudlet_overlay import overlay
from cloudlet_handoff import handoff
from cloudlet_daemon import daemon


cloudlet_version = '0.1'
cloudlet_info = 'Dev container based cloudlet'


def help():
    print('cloudlet: ')
    print('usage:  cloudlet [opt] [argv]')
    print('usage:  cloudlet check')
    print('usage:  cloudlet -h')
    print('     service     -l #listeng to the connections ')
    print('     fetch  [service name]   #get overlay image')
    print('     overlay [new image] [base image] #create overlay image')
    print('     migrate [container name]] -t [des ip] #migrate container ')


def parase(argv):
    argv_len = len(argv)
    logging.debug(argv_len)
    ret = True
    opt = argv[0]
    if argv_len == 1:
        if opt == 'check':
            ret = cloudlet_check()

    if argv_len == 2:
        if opt == 'service' and argv[1] == '-l':
            clet = daemon()
            clet.run()

        elif opt == 'fetch':
            overlay_name = argv[1]
            ovlay = overlay(overlay_name, None)
            ovlay.fetch()
            # ovlay.sythesis()
        elif opt == 'search':
            print(" to be implement.")

    if argv_len == 3:
        if opt == 'overlay':
            modified_image = argv[1]
            base_image = argv[2]
            logging.info(modified_image)
            logging.info(base_image)
            ol = overlay(modified_image, base_image)
            ret = ol.generate()

    if argv_len == 4:
        if opt == 'migrate':
            con = argv[1]
            cmd_option = argv[2]
            dst_ip = argv[3]
            if cmd_option != '-t':
                logging.error('please follow opt format:')
                logging.error(' migrate [container] -t [dst ip]')
                return False
            # handoff
            hdoff = handoff(con, dst_ip)
            ret = hdoff.run()

    if ret is False:
        logging.error('service failed')
        return False

    return True


if __name__ == '__main__':

    # log control.
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 5:
        logging.error("too many input arguments.")

    logging.debug(sys.argv)

    # help info and version info
    opt = sys.argv[1]
    if opt == '-h' or opt == '-help' or opt == 'help':
        help()
        sys.exit(0)
    elif opt == '-v' or opt == 'version':
        print('cloudlet_version: ' + cloudlet_version)
        print('cloudlet_info: ' + cloudlet_info)
        sys.exit(0)

    ret = parase(sys.argv[1:])
    if ret is False:
        logging.error("service faliled")
        sys.exit(-1)
    sys.exit(0)
