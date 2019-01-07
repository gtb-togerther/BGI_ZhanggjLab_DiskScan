#!/usr/bin/env python3


"""

    Author: Hao Yu  (yuhao@genomics.cn)
    Date:   2018-11-05

    ChangeLog:
        v0.1
            2018-11-05
                Initiation
        v0.2
            2018-11-06
                To add a function for checking and outputting broken links
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
        v1.3
            2018-12-21
                To use Python3 as the default parser

"""

import sys
import os
import pwd
import datetime
import filetype


def __check_fragment_directory(__directory_path):
    """To check whether a directory takes more than 500 sub-items"""

    __is_fragment_directory = 'NO'

    __directory_owner = pwd.getpwuid(os.stat(__directory_path).st_uid).pw_name
    __directory_inode = os.stat(__directory_path).st_ino
    __directory_size = len(os.listdir(__directory_path))

    __modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(__directory_path)).strftime("%Y-%m-%d")
    __access_time = datetime.datetime.fromtimestamp(os.path.getatime(__directory_path)).strftime("%Y-%m-%d")

    if __directory_size > 500:
        __is_fragment_directory = 'YES'

    return __directory_owner, __directory_inode, __directory_size, \
           __modify_time, __access_time, \
           __directory_path, __is_fragment_directory


def __check_large_file(__file_path):
    """To check whether a uncompressed file is larger than 500M"""

    __is_large_file = 'NO'

    __file_owner = pwd.getpwuid(os.stat(__file_path).st_uid).pw_name
    __file_inode = os.stat(__file_path).st_ino
    __file_size = os.path.getsize(__file_path)

    __modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(__file_path)).strftime('%Y-%m-%d')
    __access_time = datetime.datetime.fromtimestamp(os.path.getatime(__file_path)).strftime('%Y-%m-%d')

    if __file_size > 524288000:

        __file_type = filetype.filetype.guess_mime(__file_path)

        if not __file_type:
            __is_large_file = 'YES'

    return __file_owner, __file_inode, __file_size, \
           __modify_time, __access_time, \
           __file_path, __is_large_file


def __check_broken_link(__link_path):
    """To check whether a symbolic link is a broken link"""

    __is_broken_link = 'NO'

    if os.path.lexists(__link_path):
        __is_broken_link = 'YES'

    return __link_path, __is_broken_link


def __check_accessible_directory(__directory_path):
    """To judge whether a directory is accessible"""

    __is_accessible_directory = 'NO'

    __directory_owner = pwd.getpwuid(os.stat(__directory_path).st_uid).pw_name
    __directory_inode = os.stat(__directory_path).st_ino

    if os.access(__directory_path, os.R_OK) and os.access(__directory_path, os.X_OK):
        __is_accessible_directory = 'YES'

    return __directory_owner, __directory_inode, \
           __is_accessible_directory


def __whitelist(__whitelist_path):
    """To initial the whitelist for ignoring when scanning"""

    __whitelist_set = set([])

    with open(__whitelist_path, 'r') as __inFH:

        for __ in __inFH:

            __ = __.strip()

            if not __.endswith('/'):

                __whitelist_set.add(__)
                __whitelist_set.add(__ + '/')

            elif __.endswith('/'):

                __whitelist_set.add(__[:-1])
                __whitelist_set.add(__)

    return __whitelist_set


def traverse_directory(__root_path, __whitelist_path):
    """To generate a subdirectory tree from an imported root, then to traverse them"""

    __fragment_directory_list = []
    __large_file_list = []
    __broken_link_list = []
    __nonAccessible_directory_list = []

    __whitelist_set = __whitelist(__whitelist_path)

    ############################################
    # An accessible directory could be scanned #
    ############################################

    __root_owner, __root_inode, __root_accessible = __check_accessible_directory(__root_path)

    ##############################################################################################
    # Only a sub-items which are from a non-fragment directory could join the following scanning,#
    # if not, this following scanning will stop                                                  #
    ##############################################################################################

    if os.path.isdir(__root_path) and __root_path not in __whitelist_set:

        if __root_accessible == 'YES':

            __d_owner, __d_inode, __d_size, __d_m_time, __d_a_time, __d_path, __is_fragment_directory = \
                __check_fragment_directory(__root_path)

            if __is_fragment_directory == 'YES':
                __fragment_directory_list.append([__d_owner, str(__d_inode), str(__d_size),
                                                  __d_m_time, __d_a_time,
                                                  __d_path])

            else:

                for __subitem in os.listdir(__root_path):

                    __item_name = os.path.join(__root_path, __subitem)

                    ######################################################################################
                    # If a subdirectory is in a non-fragment directory, it would be scanned recursively. #
                    # An accessible directory could be scanned                                           #
                    ######################################################################################

                    if os.path.isdir(__item_name) and \
                            not os.path.islink(__item_name) and \
                            __item_name not in __whitelist_set:

                        __frag_dir_lst, __larg_fil_lst, __brok_lnk_lst, __nonA_dir_list = \
                            traverse_directory(__item_name, __whitelist_path)

                        __fragment_directory_list.extend(__frag_dir_lst)
                        __large_file_list.extend(__larg_fil_lst)
                        __broken_link_list.extend(__brok_lnk_lst)
                        __nonAccessible_directory_list.extend(__nonA_dir_list)

                    ###########################################################
                    # An uncompressed large files should be recorded directly #
                    ###########################################################

                    elif os.path.isfile(__item_name) and \
                            not os.path.islink(__item_name) and \
                            __item_name not in __whitelist_set:

                        f_owner, f_inode, f_size, f_m_time, f_a_time, f_path, is_large_file = __check_large_file(
                            __item_name)

                        if is_large_file == 'YES':
                            __large_file_list.append(
                                [f_owner, str(f_inode), str('%.2fG' % (float(f_size) / 1024 / 1024 / 1024)), f_m_time,
                                 f_a_time, f_path])

                    ############################################
                    # A broken symbolic link would be recorded #
                    ############################################

                    elif os.path.islink(__item_name) and __item_name not in __whitelist_set:

                        l_path, is_broken_link = __check_broken_link(__item_name)

                        if is_broken_link == 'YES':
                            __broken_link_list.append(l_path)

                    ##############################################################
                    # An error would be raised if the type of an item is unknown #
                    ##############################################################

                    else:
                        print('Warning: ' + __item_name +
                              ' may not be either a directory or a normal file as well as a symbolic link',
                              file=sys.stderr)

        else:
            __nonAccessible_directory_list.append([__root_owner, str(__root_inode), __root_path])

    else:
        print('Warning: The inputting root path should be either a directory or a symbolic link pointed by a directory',
              file=sys.stderr)

    return __fragment_directory_list, __large_file_list, __broken_link_list, __nonAccessible_directory_list


def order_report(__fragment_directory_list, __large_file_list, __broken_link_list, __nonAccessible_directory_list,
                 __output_dir, __prefix):
    """To order all the scanned result into a report"""

    if not os.path.exists(__output_dir):
        os.mkdir(__output_dir, 0o755)

    with open(__output_dir + '/' + __prefix + '.fragment_directory.report.txt', 'w') as \
            __fragment_directory_ouFH:

        print('#CLASS\tOWNER\tINODE\tNUM_of_SUBITEM\tMODIFY_DATE\tACCESS_DATE\tPATH', file=__fragment_directory_ouFH)

        for i in __fragment_directory_list:
            print('FD\t' + '\t'.join(i), file=__fragment_directory_ouFH)

    with open(__output_dir + '/' + __prefix + '.large_file.report.txt', 'w') as \
            __large_file_ouFH:

        print('#CLASS\tOWNER\tINODE\tSIZE_of_ITEM\tMODIFY_DATE\tACCESS_DATE\tPATH', file=__large_file_ouFH)

        for i in __large_file_list:
            print('LF\t' + '\t'.join(i), file=__large_file_ouFH)

    with open(__output_dir + '/' + __prefix + '.broken_link.report.txt', 'w') as \
            __broken_link_ouFH:

        print('#CLASS\tBROKEN_LINK_PATH', file=__broken_link_ouFH)

        for i in __broken_link_list:
            print('BL\t' + i, file=__broken_link_ouFH)

    with open(__output_dir + '/' + __prefix + '.nonAccessible_directory.report.txt', 'w') as \
            __nonAccessible_directory_ouFH:

        print('#CLASS\tOWNER\tINODE\tNON-ACCESSIBLE_DIRECTORY_PATH', file=__nonAccessible_directory_ouFH)

        for i in __nonAccessible_directory_list:
            print('nAD\t' + '\t'.join(i), file=__nonAccessible_directory_ouFH)


if __name__ == '__main__':

    try:

        output_dir = 'scanning_result.' + datetime.datetime.today().strftime("%Y-%m-%d")
        output_prefix = sys.argv[3] if len(sys.argv) == 4 else 'output'

        fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list = \
            traverse_directory(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]))

        order_report(fragment_directory_list, large_file_list, broken_link_list, nonAccessible_directory_list,
                     output_dir, output_prefix)

    except (IOError, IndexError):
        print('USAGE:  ' + sys.argv[0] + ' <target_dir> <whitelist> [prefix]', file=sys.stderr)
