#!/usr/bin/env python3


"""

    Author: Hao Yu (yuhao@genomics.cn)
    Date:   2018-11-07

    ChangeLog:
        v0.1
            2018-11-07
                Initiation
        v0.2
            2018-11-15
                To use a new data structure
        v1.0
            2018-12-10
                To add report function
        v1.1
            2018-12-10
                To add a function for judging modify time
        v1.2
            2018-12-11
                To add a function for judging unhandled ratio
        v1.3
            2018-12-21
                To use Python3 as the default parser

"""

import sys
import os
import time
import datetime
import math


def combine_result(__input_list):
    """This function is used for combining all the separate result into one box"""

    __result_path_list = []

    for __list in __input_list:

        if os.path.isdir(__list):

            for __item in os.listdir(__list):
                __result_path_list.append(os.path.join(__list, __item))

        else:
            __result_path_list.append(__list)

    __result_box = {}

    if 'FD' not in __result_box:
        __result_box.update({'FD': {}})

    if 'LF' not in __result_box:
        __result_box.update({'LF': {}})

    if 'BL' not in __result_box:
        __result_box.update({'BL': []})

    if 'nAD' not in __result_box:
        __result_box.update({'nAD': {}})

    for __result_path in __result_path_list:

        with open(__result_path, 'r') as __inFH:

            for __ in __inFH:

                __ = __.split()

                if __[0].startswith('#'):
                    continue

                __record_class = __[0]

                if __record_class == 'FD' or __record_class == 'LF':

                    __record_owner = __[1]
                    __record_inode = __[2]
                    __record_size = __[3]

                    __record_path = __[6]

                    __record_mtime = __[4]
                    __record_atime = __[5]

                    __time_now = time.strptime(str(datetime.date.today()), "%Y-%m-%d")
                    __time_now = datetime.datetime(__time_now[0], __time_now[1], __time_now[2])

                    __time_rec_m = time.strptime(__record_mtime, "%Y-%m-%d")
                    __time_rec_m = datetime.datetime(__time_rec_m[0], __time_rec_m[1], __time_rec_m[2])

                    __time_rec_a = time.strptime(__record_atime, "%Y-%m-%d")
                    __time_rec_a = datetime.datetime(__time_rec_a[0], __time_rec_a[1], __time_rec_a[2])

                    __length_from_now_to_modify = str(__time_now - __time_rec_m)
                    __length_from_now_to_access = str(__time_now - __time_rec_a)

                    if 'days' in __length_from_now_to_modify and 'days' in __length_from_now_to_access:

                        __length_from_now_to_modify = __length_from_now_to_modify.split()
                        __length_from_now_to_access = __length_from_now_to_access.split()

                        if int(__length_from_now_to_modify[0]) <= 180:
                            continue

                    else:
                        continue

                    if __record_owner not in __result_box[__record_class]:
                        __result_box[__record_class].update({__record_owner: {}})

                    if __record_inode not in __result_box[__record_class][__record_owner]:
                        __result_box[__record_class][__record_owner].update({__record_inode: [__record_size,
                                                                                              __record_mtime,
                                                                                              __record_atime,
                                                                                              __record_path]})

                    if 'count' not in __result_box[__record_class][__record_owner]:
                        __result_box[__record_class][__record_owner].update({'count': 0})

                    __result_box[__record_class][__record_owner]['count'] += 1

                elif __record_class == 'BL':

                    __record_path = __[1]

                    __result_box[__record_class].append(__record_path)

                elif __record_class == 'nAD':

                    __record_owner = __[1]
                    __record_inode = __[2]
                    __record_path = __[3]

                    if __record_owner not in __result_box[__record_class]:
                        __result_box[__record_class].update({__record_owner: {}})

                    if __record_inode not in __result_box[__record_class][__record_owner]:
                        __result_box[__record_class][__record_owner].update({__record_inode: [__record_path]})

                    if 'count' not in __result_box[__record_class][__record_owner]:
                        __result_box[__record_class][__record_owner].update({'count': 0})

                    __result_box[__record_class][__record_owner]['count'] += 1

                else:
                    print(__result_path + ' may be not your kind of record in disk-scanning', file=sys.stderr)

    return __result_box


def compare_newAndOld_results(__new_result_box, __old_result_box=None):
    """This function is used for comparing new and old results"""

    __unhandled_item_box = {}

    for __record_class in __new_result_box:

        if __record_class not in __unhandled_item_box:
            __unhandled_item_box.update({__record_class: {}})

        if __record_class != 'BL':

            for __record_owner in __new_result_box[__record_class]:

                if __record_owner not in __unhandled_item_box[__record_class]:
                    __unhandled_item_box[__record_class].update({__record_owner: {'record': [], 'count': []}})

                __unhandled_count = 0
                __oldRecord_count = 0

                for __record_inode in __new_result_box[__record_class][__record_owner]:

                    if __record_inode != 'count':

                        if __old_result_box and \
                                __record_class in __old_result_box and \
                                __record_owner in __old_result_box[__record_class] and \
                                __record_inode in __old_result_box[__record_class][__record_owner]:

                            __unhandled_item_box[__record_class][__record_owner]['record'].append([__record_class,
                                                                                                   __record_owner,
                                                                                                   __new_result_box[
                                                                                                       __record_class][
                                                                                                       __record_owner][
                                                                                                       __record_inode],
                                                                                                   __old_result_box[
                                                                                                       __record_class][
                                                                                                       __record_owner][
                                                                                                       __record_inode],
                                                                                                   'UH'])

                            __unhandled_count += 1

                        else:
                            __unhandled_item_box[__record_class][__record_owner]['record'].append([__record_class,
                                                                                                   __record_owner,
                                                                                                   __new_result_box[
                                                                                                       __record_class][
                                                                                                       __record_owner][
                                                                                                       __record_inode],
                                                                                                   ['-'], 'NR'])

                    else:

                        if __old_result_box and \
                                __record_class in __old_result_box and \
                                __record_owner in __old_result_box[__record_class]:
                            __oldRecord_count = __old_result_box[__record_class][__record_owner]['count']

                __unhandled_item_box[__record_class][__record_owner]['count'] = [__unhandled_count, __oldRecord_count]

        else:

            for broken_link in __new_result_box[__record_class]:

                if 'WARNING' not in __unhandled_item_box[__record_class]:
                    __unhandled_item_box[__record_class].update({'WARNING': []})

                __unhandled_item_box[__record_class]['WARNING'].append([__record_class, 'WARNING',
                                                                        [broken_link], ['-'], 'WA'])

    return __unhandled_item_box


def report_result(__compared_result_box):
    """This function is used for plotting"""

    __statisticsByOwner_box = {}

    for __record_class in __compared_result_box:

        if __record_class == 'BL':
            continue

        for __record_owner in __compared_result_box[__record_class]:

            if __record_owner not in __statisticsByOwner_box:
                __statisticsByOwner_box.update({__record_owner: {}})

            if __record_class not in __statisticsByOwner_box[__record_owner]:
                __statisticsByOwner_box[__record_owner].update({__record_class: {'new': 0, 'old': 0}})

            for __record in __compared_result_box[__record_class][__record_owner]['record']:

                __new_item_size = 0
                __old_item_size = 0

                if __record_class == 'LF':

                    __new_item_size = float(__record[2][0][:-1])

                    if __record[3][0] != '-':
                        __old_item_size = float(__record[3][0][:-1])

                    else:
                        __old_item_size = 0

                else:

                    __new_item_size = 1

                    if __record[3][0] != '-':
                        __old_item_size = 1

                    else:
                        __old_item_size = 0

                __statisticsByOwner_box[__record_owner][__record_class]['new'] += __new_item_size
                __statisticsByOwner_box[__record_owner][__record_class]['old'] += __old_item_size

            if 'unhandled_ratio' not in __statisticsByOwner_box[__record_owner][__record_class]:
                __statisticsByOwner_box[__record_owner][__record_class].update({'unhandled_ratio': []})

            if __compared_result_box[__record_class][__record_owner]['count'][1] > 0:
                __statisticsByOwner_box[__record_owner][__record_class]['unhandled_ratio'] = [
                    '%d' % __compared_result_box[__record_class][__record_owner]['count'][0],
                    '%d' % __compared_result_box[__record_class][__record_owner]['count'][1],
                    '%.2f' % (float(__compared_result_box[__record_class][__record_owner]['count'][0]) /
                              float(__compared_result_box[__record_class][__record_owner]['count'][1]) * 100)]

            else:
                __statisticsByOwner_box[__record_owner][__record_class]['unhandled_ratio'] = ['-', '-', '-']

    return __statisticsByOwner_box


if __name__ == '__main__':

    name = 'NO_NAME'

    if len(sys.argv) == 3:
        name = os.path.basename(os.path.realpath(sys.argv[1])) + '__vs__' + os.path.basename(
            os.path.realpath(sys.argv[2]))

    else:
        name = os.path.basename(os.path.realpath(sys.argv[1])) + '__only'

    ouFH = open(name + '.output.txt', 'w')
    rpFH = open(name + '.report.txt', 'w')

    try:

        if len(sys.argv) == 3:
            outbox = compare_newAndOld_results(combine_result([sys.argv[1], ]), combine_result([sys.argv[2], ]))

        else:
            outbox = compare_newAndOld_results(combine_result([sys.argv[1], ]))

        for record_class in outbox:
            for record_owner in outbox[record_class]:
                for record in outbox[record_class][record_owner]:
                    if record != 'record' and record != 'count':
                        print('\t'.join([record[0], record[1], '\t'.join(record[2]), '\t'.join(record[3]), record[-1]]),
                              file=ouFH)

        ouFH.close()

        report_box = report_result(outbox)

        for report_owner in sorted(report_box.keys()):
            for report_class in sorted(report_box[report_owner].keys()):

                consumed_ration = '-'

                if report_box[report_owner][report_class]['old'] > 0:
                    consumed_ration = '%.4f' % (math.log(float(report_box[report_owner][report_class]['new']) / float(
                        report_box[report_owner][report_class]['old'])))

                if report_class == 'LF':
                    print('%-18s         LF: %12.2f Gb   vs. %12.2f Gb%9s   | %12s   vs. %12s%9s' %
                          (report_owner,
                           report_box[report_owner]['LF']['new'],
                           report_box[report_owner]['LF']['old'],
                           consumed_ration,
                           report_box[report_owner]['LF']['unhandled_ratio'][0],
                           report_box[report_owner]['LF']['unhandled_ratio'][1],
                           report_box[report_owner]['LF']['unhandled_ratio'][2]),
                          file=rpFH)

                else:
                    print('%-18s%11s: %12d      vs. %12d%12s   | %12s   vs. %12s%9s' %
                          (report_owner, report_class,
                           report_box[report_owner][report_class]['new'],
                           report_box[report_owner][report_class]['old'],
                           consumed_ration,
                           report_box[report_owner][report_class]['unhandled_ratio'][0],
                           report_box[report_owner][report_class]['unhandled_ratio'][1],
                           report_box[report_owner][report_class]['unhandled_ratio'][2]),
                          file=rpFH)

            print('', file=rpFH)

        rpFH.close()

    except IOError:
        print('USAGE:  ' + sys.argv[0] + ' <scanning outdir> [old scanning outdir]', file=sys.stderr)
