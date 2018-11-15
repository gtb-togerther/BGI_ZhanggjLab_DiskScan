#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''

    Author: Hao Yu (yuhao@genomics.cn)
    Date:   2018-11-07

    ChangeLog:
        v0.1
            2018-11-07
                Initiation
        v0.2
            2018-11-15
                To use a new data structure

'''


import sys
import os


def combine_result(input_list):
    'This function is used for combining all the separate result into one box'

    result_path_list = []

    for i in input_list:
        if os.path.isdir(i):
            for r in os.listdir(i):
                result_path_list.append(os.path.join(i, r))
        else:
            result_path_list.append(i)

    result_box = {'FD':{},'LF':{},'BL':[],'nAD':{}}

    for result_path in result_path_list:
        with open(result_path, 'rb') as fh:
            for l in fh:
                l = l.split()

                if l[0].startswith('#'):
                    continue

                record_class = l[0]

                if record_class == 'FD' or record_class == 'LF':
                    record_owner = l[1]
                    record_inode = l[2]
                    record_path = l[6]

                    record_size = l[3]
                    record_mtime = l[4]
                    record_atime = l[5]

                    if not result_box[record_class].has_key(record_owner):
                        result_box[record_class].update({record_owner:{}})

                    if not result_box[record_class][record_owner].has_key(record_inode):
                        result_box[record_class][record_owner].update({record_inode:[record_size,record_mtime,record_atime,record_path]})
                elif record_class == 'BL':
                    record_path = l[1]

                    result_box[record_class].append(record_path)
                elif record_class == 'nAD':
                    record_owner = l[1]
                    record_inode = l[2]
                    record_path = l[3]

                    if not result_box[record_class].has_key(record_owner):
                        result_box[record_class].update({record_owner:{}})

                    if not result_box[record_class][record_owner].has_key(record_inode):
                        result_box[record_class][record_owner].update({record_inode:[record_path]})
                else:
                    print >> sys.stderr, result_path + ' may be not your kind of record in disk-scanning'

    return result_box


def compare_newAndOld_results(new_result_box, old_result_box = None):
    'This function is used for comparing new and old results'

    noHandle_item_box = {}

    for record_class in new_result_box:
        if not noHandle_item_box.has_key(record_class):
            noHandle_item_box.update({record_class:{}})

        if record_class != 'BL':
            for record_owner in new_result_box[record_class]:
                if not noHandle_item_box[record_class].has_key(record_owner):
                    noHandle_item_box[record_class].update({record_owner:[]})

                for record_inode in new_result_box[record_class][record_owner]:
                    if old_result_box and old_result_box[record_class][record_owner][record_inode]:
                        noHandle_item_box[record_class][record_owner].append([record_class,record_owner,\
                                                                              new_result_box[record_class][record_owner][record_inode],\
                                                                              old_result_box[record_class][record_owner][record_inode],'UH'])
                    else:
                        noHandle_item_box[record_class][record_owner].append([record_class,record_owner,\
                                                                              new_result_box[record_class][record_owner][record_inode],['-'],'NR'])
        else:
            for broken_link in new_result_box[record_class]:
                if not noHandle_item_box[record_class].has_key('WARNING'):
                    noHandle_item_box[record_class].update({'WARNING':[]})

                noHandle_item_box[record_class]['WARNING'].append([record_class,'WARNING',\
                                                                  [broken_link],['-'],'WA'])

    return noHandle_item_box


def report_result(compared_result_box):
    'This function is used for plotting'

    pass


if __name__ == '__main__':
    try:
        if len(sys.argv) == 3:
            outbox = compare_newAndOld_results(combine_result([sys.argv[1],]), combine_result([sys.argv[2],]))
        else:
            outbox = compare_newAndOld_results(combine_result([sys.argv[1],]))

        for record_class in outbox:
            for record_owner in outbox[record_class]:
                for i in outbox[record_class][record_owner]:
                    print '\t'.join([i[0],i[1],'\t'.join(i[2]),'\t'.join(i[3]),i[-1]])
    except:
        print >> sys.stderr, 'USAGE:  ' + sys.argv[0] + ' <scanning outdir> [old scanning outdir]'
