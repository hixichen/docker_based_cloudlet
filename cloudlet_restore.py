#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import logging
import commands
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_memory import cloudlet_memory


def pre_restore(base_image, name):

    cmd_option = 'docker run --name=foo -d ' + base_image + \
        ' tail -f /dev/null && docker rm -f foo'
    os.system(cmd_option)

    delete_op = 'docker rm -f ' + name + ' >/dev/null 2>&1'
    os.system(delete_op)

    create_op = 'docker create --name=' + name + ' ' + base_image
    logging.debug(create_op)
    ret, id = commands.getstatusoutput(create_op)
    logging.info(id)
    return id


def restore(task_id, label):

    label_ar = label.split('-')
    con_name = label_ar[0]
    image_name = label_ar[1]
    image_id = label_ar[2]
    logging.debug('keep image id for verify %s ' % image_id)
    logging.debug(label_ar)

    # verify image.
    con_id = pre_restore(image_name, con_name)

    restore_filesystem = cloudlet_filesystem(con_id, task_id)
    if restore_filesystem.restore() is False:
        logging.error('filesystem restore failed\n')
        return False

    mhandle = cloudlet_memory(task_id)
    mhandle.restore(con_id)
    return True
