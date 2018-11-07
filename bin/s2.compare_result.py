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


def __stat_fragment_directory__(parsed_result_box):
    'This function is used for put the scanning result of fragment directory in order'

    pass


def __stat_large_file__(parsed_result_box):
    'This function is used for put the scanning result of large file in order'

    pass


def __stat_broken_link__(parsed_result_box):
    'This function is used for put the scanning result of broken link in order'

    pass


def __stat_nonAccessible_directory__(parsed_result_box):
    'This function is used for put the scanning result of non-accessible directory in order'

    pass


def combine_result(result_dir_path_list):
    'This function is used for combining all the separate result into one box'

    for result_dir_path in result_dir_path_list:
        pass


def compare_newAndOld_results(new_result_box, old_result_box):
    'This function is used for comparing new and old results'

    pass


def plot_compared_result(compared_result_box):
    'This function is used for plotting'

    pass


if __name__ == '__main__':
    if len(sys.argv) == 3:
        combine_result(sys.argv)
