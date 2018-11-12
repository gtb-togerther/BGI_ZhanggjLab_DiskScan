#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''

    Author: Hao Yu (yuhao@genomics.cn)
    Date:   2018-11-07

    ChangeLog:
        v0.1
            2018-11-07
                Initiation

'''


import sys
import os
import matplotlib


def combine_result(input_list):
    'This function is used for combining all the separate result into one box'

    result_path_list = []

    for i in input_list:
        if os.path.isdir(i):
            for r in os.listdir(i):
                result_path_list.append(os.path.join(i, r))
        else:
            result_path_list.append(i)

    result_box = {'FD':{},'LF':{},'BL':{},'nAD':{}}

    for result_path in result_path_list:
        with open(result_path, 'rb') as fh:
            for l in fh:
                l = l.split()

                if l[0].startswith('#'):
                    continue

                record_class = l[0]
                record_owner = l[1]

                if record_class == 'FD' or record_class == 'LF':
                    record_inode = l[2]
                    record_size = l[3]
                    record_mtime = l[4]
                    record_atime = l[5]
                    record_path = l[6]

                    if not result_box[record_class].has_key(record_owner):
                        result_box[record_class].update({record_owner:[]})
                        result_box[record_class][record_owner].append([record_inode,record_size,record_mtime,record_atime,record_path])
                    else:
                        result_box[record_class][record_owner].append([record_inode,record_size,record_mtime,record_atime,record_path])
                elif record_class == 'BL':
                    record_path = l[2]

                    if not result_box[record_class].has_key(record_owner):
                        result_box[record_class].update({record_owner:[]})

                    result_box[record_class][record_owner].append([record_path,])
                elif record_class == 'nAD':
                    record_inode = l[2]
                    record_path = l[3]

                    if not result_box[record_class].has_key(record_owner):
                        result_box[record_class].update({record_owner:[]})

                    result_box[record_class][record_owner].append([record_inode,record_path])
                else:
                    print >> sys.stderr, result_path + ' may be not your kind of record in disk-scanning'

    return result_box


def compare_newAndOld_results(new_result_box, old_result_box):
    'This function is used for comparing new and old results'

    noHandle_item_box = {}

    for record_class in new_result_box:
        for record_owner in new_result_box[record_class]:
            if record_class != 'BL':
                if old_result_box[record_class][record_owner]:
                    if new_result_box[record_class][record_owner][0] == old_result_box[record_class][record_owner][0]:  # error
                        if not noHandle_item_box.has_key(record_class):
                            noHandle_item_box.update({record_class:{}})
                        else:
                            if not noHandle_item_box[record_class].has_key(record_owner):
                                noHandle_item_box[record_class].update({record_owner:[]})
                            else:
                                noHandle_item_box[record_class][record_owner].append([old_result_box[record_class][record_owner],new_result_box[record_class][record_owner]])

    return noHandle_item_box


def plot_compared_result(compared_result_box):
    'This function is used for plotting'

    pass


if __name__ == '__main__':
    if sys.argv > 1:
        outbox = compare_newAndOld_results(combine_result([sys.argv[1],]), combine_result([sys.argv[2],]))

        for record_class in outbox:
            for record_owner in outbox[record_class]:
                #print '\t'.join(outbox[record_class][record_owner])
                pass
