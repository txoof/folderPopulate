
# coding: utf-8

# In[147]:

#!/usr/bin/python

# Student Portfolio Folder Populator

# Takes a CSV file containing student information and creates Portfolio Folders using folders.txt 
# located on ~/Desktop or in the working directory as a template

# usage: populate.py StudentList.csv

# CSV notes: 
#     * CSV must contain the following fields (in no particular order):
#         - ClassOf
#         - LastFirst
#         - Student_Number
#     * Extra fields are ignored

# CSV Format:
#     ClassOf,LastFirst,Student_Number
#     2029,"Amundsun, Siv Elizabeth",999988
#     2027,"Johnson, Annke",888888

    
# folders.txt notes:
#     * folders.txt must exist either in the same working directory as this script or in ~/Desktop/
#     * One folder per line
#     * Blank lines are ignored
#     * Accented characters, special characters (!@#$%^&*()), leading spaces are all stripped
                                               
# Written by Aaron Ciuffo (aaron.ciuffo @ gmail.com)
# March 10, 2017
# Released under GPL V3


# In[152]:

print sys.argv


# In[150]:

sys.argv.pop()


# In[151]:

sys.argv.append('./stuexp.txt')


# In[87]:

import csv
import sys
import os
import re
import datetime
import unicodedata


# In[88]:

def strip_accents(s):
    s = unicode(s, "utf-8")
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')


# In[80]:

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces
    """
    s = s.strip()
    s = strip_accents(s)
    return re.sub(r'(?u)[^-\w., ]', '', s)


# In[3]:

def mkdir(directory):
    try:
        os.stat(directory)
    except (OSError, IOError) as e:
        try:
            os.makedirs(directory)
        except (OSError, IOError) as mke:
            print e
            return(False, mke)
    
    return(True, directory)    


# In[145]:

def fileRead(fname):
    '''
    read a file into a list, strip out all accented and special characters, leading spaces
    '''
    lines = []
    try:
        with open(fname) as f:
            for each in f:
                each = get_valid_filename(each)
                lines.append(each.strip('\n'))
            return(lines)
    except (OSError, IOError) as e:
        print 'error reading file:', fname, e
        return(False)


# In[5]:

def pathify(parts = [], basepath = ''):
    '''
    create a path from a list of strings
    
    accepts:
        * parts (list): list of strings ['part_one', 'part_two', 'part_three']
        * basepath (string): string to append to the start of the path (default: ./)
    
    returns:
        * path: basePath/part_one/part_two/part_three/
    '''
    path = basepath
    if len(parts ) > 0:
        for each in parts:
            if re.match('.*\/$', each):
                path = path + each
            else:
                path = path + each + '/'
    return(path)


# In[154]:

def main():
    
    # path to Desktop of the user (this should work on macs)
    desktopPath = pathify([os.path.expanduser('~'), 'Desktop'])
    
    # output path for populated directories
    outputPath = pathify([desktopPath, 'STUDENT RECORDS ' + datetime.datetime.now().strftime("%Y-%m-%d")])
    
    
    # expected fields in CSV
    expected = ['ClassOf', 'LastFirst', 'Student_Number']
    
    # sample student data for output
    sampleStudent = '2031,"Ammund, Siv Elizabeth",999998'

    # map of csv fields to element in list 
    headerMap = {}
        
    # list of folders to populate into each students' directory
    if os.path.exists(desktopPath+'folders.txt'):
        fileList = desktopPath + 'folders.txt'
    else:
        fileList = './folders.txt'
    
    # list of student information
    studentInfo = ''
    
    # list for contents of CSV
    studentCSV =[]
    
    # list of folders to add under each student path
    folders = fileRead(fileList)
    
    

    try:
        print 'input file:', sys.argv[3]
        studentInfo = sys.argv[3]
    except IndexError as e: 
        print '\nError: please drop a valid CSV list of students onto this application'
        print 'CSV Format:'
        string = ''
        for each in expected:
            string = string + each + ','
        print '     ', string
        print '     ', sampleStudent
        return(False)
    
    
    if folders:
        print 'number of folders to create for each student:', len(folders)
        print 'following folders will be created for each student:'
        for each in folders:
            print '     ', each
    else:
        print 'Please place a file named "folders.txt" containing a list of folders to add to each student directory'
        print 'in one of the following locations:'
        print '    * ', os.getcwd()
        print '    * ', desktopPath
        print 'exiting'
        return(False)
    
    # read the csv file
    try:
        with open(studentInfo, 'rU') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                studentCSV.append(row)
    except (OSError, IOError) as e:
        print 'error reading file:', fname, e
        print 'exiting'
        return(False)
    
    if len(studentCSV) > 1:
        print len(studentCSV)-1, 'student records found in', studentInfo, '\n'
    else:
        print 'no student records found in', studentInfo
        return(False)
    
    # check for expected headers in CSV data
    missingHeaders = []
    for each in expected:
        if each not in studentCSV[0]:
            missingHeaders.append(each)
        
    if len(missingHeaders) > 0:
        print 'ERROR'
        for each in missingHeaders:
            print studentInfo, ' missing header: ', each
        print 'please recreate file', studentInfo, 'with all required headers:'
        print '     ', expected
        print 'stopping'
        return(False)
    
    # map headers to their index
    for index, value in enumerate(studentCSV[0]):
        headerMap[value]=index
    
    
    # work through the CSV file
    totalCreated = 0
    totalExisting = 0
    created = []
    existing = []
    
    print 'creating student folders here:'
    print '     ',outputPath
    for index, value in enumerate(studentCSV):
        if index > 0:
            path = pathify([outputPath, 'Class Of ' + get_valid_filename(value[headerMap['ClassOf']]), 
                     get_valid_filename(value[headerMap['LastFirst']]) + ' - ' 
                     + get_valid_filename(value[headerMap['Student_Number']])
                    ])
            for each in folders:
                try:
                    if os.stat(path + each):
                        totalExisting += 1
                        existing.append(each)
                except (OSError, IOError) as e:
                    result = mkdir(path + each)
                    if not result[0]:
                        print result[1]
                    else:
                        totalCreated += 1
                        created.append(each)
                        
    print 'Total folders created:', totalCreated
    print 'Total folders already existing:', totalExisting
    
    return()


# In[155]:

if __name__ == "__main__":
    main()


