#!/usr/bin/env python
#coding=utf-8
#file: coinsdeptartments.py

"""
Read a COINS csv file and split into separate smaller csv files.
Can split according to department or data_type.
"""

import os
import os.path
import csv
import time
from optparse import OptionParser

import coinsfields

# filename reflects date, data subset, and non-zero values (nz)
FILENAME_TEMPLATE = '../data/csv/coins_%(date)s_%(code)s_nz.csv'

def write_selected_csv(input_filename, date, field_no, code, limit, verbose):
    """
    Read COINS .csv file

    Keyword arguments:
    input_filename -- the name of the COINS input file.
    date -- the date period for the data, reflected in the output filename.
    field_no -- field for selection.
    code -- code for selection to be extracted.
    limit -- max number of lines of input to be read. Useful for debugging.
    verbose -- give detailed status updates.

    """
    if verbose:
        print 'Reading:', input_filename
    csv_reader = csv.reader(open(input_filename, "rb"), 'excel', delimiter='@')
    output_filename = FILENAME_TEMPLATE % {'date':date, 'code':code}
    csv_writer = csv.writer(open(output_filename, 'w'))
 
    # read in the first row, which contains the column headings
    # eg Data_type, Data_type_description,
    column_headings = csv_reader.next()
    csv_writer.writerow(column_headings)

    start_time = time.time()
    reporting_interval = 50000
    row_count = 0
    selected_count = 0
    # read in the data
    try:
        while True:
            row = csv_reader.next()
            row_count += 1
            if verbose and row_count % reporting_interval == 0:
                elapsed_time = time.time() - start_time
                print('%s: %s' % (row_count, round(elapsed_time, 2)))
            if row[field_no] == code:
                selected_count += 1
                csv_writer.writerow(row)
            if limit > 0 and selected_count > limit:
                break
    except StopIteration:
        pass
    print('Total row count: %s' % row_count)
    print('Selected row count: %s' % selected_count)


def write_all_depts_csv(input_filename, date, limit, verbose):
    """
    Read a COINS .csv file.
    Write out the data for each department in a separate CSV file.

    Keyword arguments:
    input_filename -- the name of the COINS input file.
    date -- the date period for the data, reflected in the output filename.
    limit -- max number of lines of input to be read. Useful for debugging.
    verbose -- give detailed status updates.

    """
    if verbose:
        print 'Reading:', input_filename
    dept_csv_writers = {}
    depts_reader = csv.reader(open('../data/desc/department.csv', 'r'))
    # skip the column headings
    row = depts_reader.next()
    try:
        while True:
            # create a csv writer for each department
            row = depts_reader.next()
            dept = row[0]
            dept_code = dept.replace('/',' ')
            output_filename = FILENAME_TEMPLATE % {'date':date, 'code':dept_code}
            dept_csv_writers[dept] = csv.writer(open(output_filename, 'w'))
    except StopIteration:
        pass

    csv_reader = csv.reader(open(input_filename, "rb"), 'excel', delimiter='@')
    column_headings = csv_reader.next()
    for i in dept_csv_writers:
        dept_csv_writers[i].writerow(column_headings)

    start_time = time.time()
    reporting_interval = 50000
    row_count = 0
    counts = {}
    for i in dept_csv_writers:
        counts[i] = 0
    # read in the data
    try:
        while True:
            row = csv_reader.next()
            row_count += 1
            if verbose and row_count % reporting_interval == 0:
                elapsed_time = time.time() - start_time
                print('%s: %s' % (row_count, round(elapsed_time, 2)))
            dept = row[coinsfields.DEPARTMENT_CODE]
            dept_csv_writers[dept].writerow(row)
            counts[dept] += 1
            if limit > 0 and row_count > limit:
                break
    except StopIteration:
        pass
    print('Total row count: %s' % row_count)
    for i in sorted(dept_csv_writers):
        print('%(dept)s row count: %(count)s' % {'dept':i, 'count':counts[i]})


def write_all_data_types_csv(input_filename, date, limit, verbose):
    """
    Read a COINS .csv file.
    Write out the data for each data_type in a separate CSV file.

    Keyword arguments:
    input_filename -- the name of the COINS input file.
    date -- the date period for the data, reflected in the output filename.
    limit -- max number of lines of input to be read. Useful for debugging.
    verbose -- give detailed status updates.

    """
    if verbose:
        print 'Reading:', input_filename
    csv_writers = {}
    data_types = ['outturn', 'forecasts', 'plans', 'snapshots']
    # skip the column headings
    for data_type in data_types:
        output_filename = FILENAME_TEMPLATE % {'date': date, 'code': data_type}
        csv_writers[data_type] = csv.writer(open(output_filename, 'w'))

    csv_reader = csv.reader(open(input_filename, "rb"), 'excel', delimiter='@')
    column_headings = csv_reader.next()
    for i in csv_writers:
        csv_writers[i].writerow(column_headings)

    start_time = time.time()
    reporting_interval = 50000
    row_count = 0
    counts = {}
    for i in data_types:
        counts[i] = 0
    # read in the data
    try:
        while True:
            row = csv_reader.next()
            row_count += 1
            if verbose and row_count % reporting_interval == 0:
                elapsed_time = time.time() - start_time
                print('%s: %s' % (row_count, round(elapsed_time, 2)))
            data_type = row[coinsfields.DATA_TYPE]
            if data_type == 'Outturn':
                csv_writers['outturn'].writerow(row)
                counts['outturn'] += 1
            elif data_type == 'Plans':
                csv_writers['plans'].writerow(row)
                counts['plans'] += 1
            elif data_type[:8] == 'Forecast':
                csv_writers['forecasts'].writerow(row)
                counts['forecasts'] += 1
            elif data_type[:8] == 'Snapshot':
                csv_writers['snapshots'].writerow(row)
                counts['snapshots'] += 1
            else:
                print 'Unknown data_type:', data_type
            if limit > 0 and row_count > limit:
                break
    except StopIteration:
        pass
    print('Total row count: %s' % row_count)
    for i in sorted(csv_writers):
        print('%(data_type)s row count: %(count)s' % {'data_type':i, 'count':counts[i]})


def process_options(arglist=None):
    """
    Process options passed either via arglist or via command line args.

    """
    parser = OptionParser(arglist)
    #parser.add_option("-f", "--file", dest="filename",
    #                  help="file to be converted", metavar="FILE")
    parser.add_option("-c", "--code", dest="selection_code",
                      help="selection code", metavar="SELECTION_CODE")
    parser.add_option("-v", action="store_true", dest="verbose", default=False,
                      help="print status messages to stdout")

    (options, args) = parser.parse_args()
    return options, args


def main():
    """
    Read in the COINS csv file, write out the records for each data_type into a separate
    .csv file.

    """
    (options, args) = process_options()
    if len(args) == 0:
        input_filename = '../data/facts_2008_09_nz.csv'
    else:
        input_filename = args[0]
    limit = 0
    date = '2008_09'
    input_filename = '../data/facts_%s_nz.csv' % date
    options.verbose = True
    if not os.path.isdir('../data/csv'):
        os.makedirs('../data/csv')
    if options.selection_code == None:
        #write_all_depts_csv(input_filename, date, limit, options.verbose)
        write_all_data_types_csv(input_filename, date, limit, options.verbose)
        date = '2009_10'
        input_filename = '../data/facts_%s_nz.csv' % date
        write_all_data_types_csv(input_filename, date, limit, options.verbose)
        #write_selected_csv(input_filename, date, coinsfields.DATA_TYPE, 'outturn', limit, options.verbose)
    else:
        write_selected_csv(input_filename, date, coinsfields.DEPARTMENT_CODE,
            options.selection_code, limit, options.verbose)


if __name__ == "__main__":
    main()
