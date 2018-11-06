#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''

    Author: Hao Yu  (yuhao@genomics.cn)
    Date:   2018-11-05

    ChangeLog:
        v0.1
            2018-11-05
                Initiation.

'''


import sys
import os
import datetime
import filetype


def __check_fragment_directory__(directory_path):
    'To check whether a directory takes more than 500 subitems'

    is_fragment_directory = 'NO'

    directory_inode = os.stat(directory_path).st_ino
    modif_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory_path)).strftime("%Y-%m-%d")
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(directory_path)).strftime("%Y-%m-%d")

    directory_size = len(os.listdir(directory_path))

    if directory_size > 500:
        is_fragment_directory = 'YES'

    return (directory_inode, directory_size, modif_time, access_time, directory_path, is_fragment_directory)


def __check_large_file__(file_path):
    'To check whether a uncompressed file is larger than 500M'

    is_large_file = 'NO'

    file_inode = os.stat(file_path).st_ino
    modif_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path)).strftime("%Y-%m-%d")

    file_size = os.path.getsize(file_path)

    if file_size > 524288000:
        file_type = filetype.filetype.guess_mime(file_path)

        if not file_type:
            is_large_file = 'YES'

    return (file_inode, file_size, modif_time, access_time, file_path, is_large_file)


def __whitelist__(whitelist_path):
    'To initial the whitelist for ignoring when scanning'

    whitelist = []

    with open(whitelist_path, 'rb') as fh:
        for l in fh:
            l = l.strip()
            whitelist.append(l)

    return whitelist


def traverse_directory(path, whitelist_path):
    'To generate a subdirectory tree from an imported root, then to traverse them'

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    if not os.path.isabs(whitelist_path):
        whitelist_path = os.path.abspath(whitelist_path)

    fragment_directory_list = []
    large_file_list = []

    whitelist = __whitelist__(whitelist_path)

    if os.path.isdir(path) and path not in whitelist:
        d_inode, d_size, d_m_time, d_a_time, d_path, is_fragment_directory = __check_fragment_directory__(path)
        if is_fragment_directory == 'YES':
            fragment_directory_list.append([str(d_inode), str(d_size), d_m_time, d_a_time, d_path])

#####################################################################################################
# Only a subitem which are from non-fragment directory could join the following large file scanning #
#####################################################################################################

        else:
            for subitem in os.listdir(path):
                item_name = os.path.join(path, subitem)

######################################################################################
# If a subdirectory is in a non-fragment directory, it should be scanned recursively #
######################################################################################

                if os.path.isdir(item_name):
                    frag_dir_lst, larg_fil_lst = traverse_directory(item_name, whitelist_path)
                    fragment_directory_list.extend(frag_dir_lst)
                    large_file_list.extend(larg_fil_lst)

###########################################################
# An uncompressed large files should be recorded directly #
###########################################################

                elif os.path.isfile(item_name) and item_name not in whitelist:
                        f_inode, f_size, f_m_time, f_a_time, f_path, is_large_file = __check_large_file__(item_name)
                        if is_large_file == 'YES':
                            large_file_list.append([str(f_inode), str(f_size), f_m_time, f_a_time, f_path])

    return (fragment_directory_list, large_file_list)


def order_report(fragment_directory_list, large_file_list):
    'To order all the scanned result into a report'

    with open('fragment_directory.report.txt', 'wb') as fragment_directory_outFH:
        print >> fragment_directory_outFH, '#INODE\tNUM_of_SUBITEM\tMODIFY_DATE\tACCESS_DATE\tPATH'
        for i in fragment_directory_list:
            print >> fragment_directory_outFH, '\t'.join(i)

    with open('large_file.report.txt', 'wb') as large_file_outFH:
        print >> large_file_outFH, '#INODE\tSIZE_of_ITEM\tMODIFY_DATE\tACCESS_DATE\tPATH'
        for i in large_file_list:
            print >> large_file_outFH, '\t'.join(i)


if __name__ == '__main__':
    fragment_directory_list, large_file_list = traverse_directory(sys.argv[1], sys.argv[2])
    order_report(fragment_directory_list, large_file_list)
