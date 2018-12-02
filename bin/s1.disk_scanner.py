#!/usr/bin/env python
#-*- coding:utf-8 -*-


'''

    Author: Hao Yu  (yuhao@genomics.cn)
    Date:   2018-11-05

    ChangeLog:
        v0.1
            2018-11-05
                Initiation
        v0.2
            2018-11-06
                To add a function for checking and outputting brocken links
        v0.3
            2018-11-06
                To make the value of "SIZE_of_ITEM" in large file output
                more readable
        v1.0
            2018-11-07
                To add a function for checking and outputting directories
                if which would be not accessible
        v1.1
            2018-11-07
                To make an output directory for putting results in order
        v1.2
            2018-11-08
                To get and output the owner info of a directory or a file,
                and insert the class on the head of output

'''


import sys
import os
import pwd
import datetime
import filetype


def __check_fragment_directory__(directory_path):
    'To check whether a directory takes more than 500 subitems'

    is_fragment_directory = 'NO'

    directory_owner = pwd.getpwuid(os.stat(directory_path).st_uid).pw_name
    directory_inode = os.stat(directory_path).st_ino
    modif_time = datetime.datetime.fromtimestamp(os.path.getmtime(directory_path)).strftime("%Y-%m-%d")
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(directory_path)).strftime("%Y-%m-%d")

    directory_size = len(os.listdir(directory_path))

    if directory_size > 500:
        is_fragment_directory = 'YES'

    return (directory_owner, directory_inode, directory_size, modif_time, access_time, directory_path, is_fragment_directory)


def __check_large_file__(file_path):
    'To check whether a uncompressed file is larger than 500M'

    is_large_file = 'NO'

    file_owner = pwd.getpwuid(os.stat(file_path).st_uid).pw_name
    file_inode = os.stat(file_path).st_ino
    modif_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path)).strftime("%Y-%m-%d")

    file_size = os.path.getsize(file_path)

    if file_size > 524288000:
        file_type = filetype.filetype.guess_mime(file_path)

        if not file_type:
            is_large_file = 'YES'

    return (file_owner, file_inode, file_size, modif_time, access_time, file_path, is_large_file)


def __check_broken_link__(link_path):
    'To check whether a symbolic link is a brocken link'

    is_broken_link = 'NO'

    if os.path.lexists(link_path):
        is_broken_link = 'YES'

    return (link_path, is_broken_link)


def __check_accessible_directory__(directory_path):
    'To judge whether a directory is accessible'

    is_accessible_directory = 'NO'

    directory_owner = pwd.getpwuid(os.stat(directory_path).st_uid).pw_name
    directory_inode = os.stat(directory_path).st_ino

    if os.access(directory_path, os.R_OK) and os.access(directory_path, os.X_OK):
        is_accessible_directory = 'YES'

    return (directory_owner, directory_inode, is_accessible_directory)


def __whitelist__(whitelist_path):
    'To initial the whitelist for ignoring when scanning'

    whitelist = set([])

    with open(whitelist_path, 'rb') as fh:
        for l in fh:
            l = l.strip()
            if not l.endswith('/'):
                whitelist.add(l)
                whitelist.add(l + '/')
            elif l.endswith('/'):
                whitelist.add(l[:-1])
                whitelist.add(l)

    return whitelist


def traverse_directory(path, whitelist_path):
    'To generate a subdirectory tree from an imported root, then to traverse them'

    fragment_directory_list = []
    large_file_list = []
    broken_link_list = []
    nonAccessible_directory_list = []

    whitelist = __whitelist__(whitelist_path)

############################################
# An accessible directory could be scanned #
############################################

    root_owner, root_inode, root_accessible = __check_accessible_directory__(path)

#############################################################################################
# Only a subitem which are from a non-fragment directory could join the following scanning, #
# if not, this following scanning will stop                                                 #
#############################################################################################

    if os.path.isdir(path) and path not in whitelist:
        if root_accessible == 'YES':
            d_owner, d_inode, d_size, d_m_time, d_a_time, d_path, is_fragment_directory = __check_fragment_directory__(path)
            if is_fragment_directory == 'YES':
                fragment_directory_list.append([d_owner, str(d_inode), str(d_size), d_m_time, d_a_time, d_path])
            else:
                for subitem in os.listdir(path):
                    item_name = os.path.join(path, subitem)

######################################################################################
# If a subdirectory is in a non-fragment directory, it would be scanned recursively. #
# An accessible directory could be scanned                                           #
######################################################################################

                    if os.path.isdir(item_name) and not os.path.islink(item_name) and item_name not in whitelist:
                        frag_dir_lst, larg_fil_lst, brok_lnk_lst, nonA_dir_list = traverse_directory(item_name, whitelist_path)
                        fragment_directory_list.extend(frag_dir_lst)
                        large_file_list.extend(larg_fil_lst)
                        broken_link_list.extend(brok_lnk_lst)
                        nonAccessible_directory_list.extend(nonA_dir_list)

###########################################################
# An uncompressed large files should be recorded directly #
###########################################################

                    elif os.path.isfile(item_name) and not os.path.islink(item_name) and item_name not in whitelist:
                        f_owner, f_inode, f_size, f_m_time, f_a_time, f_path, is_large_file = __check_large_file__(item_name)
                        if is_large_file == 'YES':
                            large_file_list.append([f_owner, str(f_inode), str('%.2fG' % (float(f_size) / 1024 / 1024 / 1024)), f_m_time, f_a_time, f_path])

############################################
# A broken symbolic link would be recorded #
############################################

                    elif os.path.islink(item_name) and item_name not in whitelist:
                        l_path, is_broken_link = __check_broken_link__(item_name)
                        if is_broken_link == 'YES':
                            broken_link_list.append(l_path)

##############################################################
# An error would be raised if the type of an item is unknown #
##############################################################

                    else:
                        print >> sys.stderr, 'Warning: ' + item_name + ' may not be either a directory or a normal file as well as a symbolic link'
        else:
            nonAccessible_directory_list.append([root_owner, str(root_inode), path])
    else:
        print >> sys.stderr, 'Warning: The inputting root path should be either a directory or a symbolic link pointed by a directory'

    return (fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list)


def order_report(fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list, prefix):
    'To order all the scanned result into a report'

    outdir = 'scanning_result.' + datetime.datetime.today().strftime("%Y-%m-%d")
    if not os.path.exists(outdir):
        os.mkdir(outdir, 0755)

    with open(outdir + '/' + prefix + '.fragment_directory.report.txt', 'wb') as fragment_directory_outFH:
        print >> fragment_directory_outFH, '#CLASS\tOWNER\tINODE\tNUM_of_SUBITEM\tMODIFY_DATE\tACCESS_DATE\tPATH'
        for i in fragment_directory_list:
            print >> fragment_directory_outFH, 'FD\t' + '\t'.join(i)

    with open(outdir + '/' + prefix + '.large_file.report.txt', 'wb') as large_file_outFH:
        print >> large_file_outFH, '#CLASS\tOWNER\tINODE\tSIZE_of_ITEM\tMODIFY_DATE\tACCESS_DATE\tPATH'
        for i in large_file_list:
            print >> large_file_outFH, 'LF\t' + '\t'.join(i)

    with open(outdir + '/' + prefix + '.brocken_link.report.txt', 'wb') as broken_link_outFH:
        print >> broken_link_outFH, '#CLASS\tBROKEN_LINK_PATH'
        for i in broken_link_list:
            print >> broken_link_outFH, 'BL\t' + i

    with open(outdir + '/' + prefix + '.nonAccessible_directory.report.txt', 'wb') as nonAccessible_directory_outFH:
        print >> nonAccessible_directory_outFH, '#CLASS\tOWNER\tINODE\tNON-ACCESSIBLE_DIRECTORY_PATH'
        for i in nonAccessible_directory_list:
            print >> nonAccessible_directory_outFH, 'nAD\t' + '\t'.join(i)


if __name__ == '__main__':
    try:
        fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list = traverse_directory(os.path.abspath(sys.argv[1]), \
                                                                                                                      os.path.abspath(sys.argv[2]))

        prefix = sys.argv[3] if sys.argv[3] else 'output'
        order_report(fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list, prefix)
    except (IOError,IndexError):
        print >> sys.stderr, 'USAGE:  ' + sys.argv[0] + ' <targe_dir> <whitelist> [prefix]'
