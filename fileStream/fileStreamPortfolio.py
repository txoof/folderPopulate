#!/usr/bin/python


# In[3]:

import os
import fnmatch
import subprocess
import re
import simpleMenu
import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
import sys
import unicodedata
import csv

appShortName = 'fileStreamPortfolio'

# get the current working directory
# When launching a .comman from the OS X Finder, the working directory is typically ~/; this is problematic
# for locating resource files
# I don't love this hack, but it works.
try:
    __file__
    cwd = os.path.dirname(__file__)+'/'
except NameError as e:
    cwd = os.getcwd()


# In[4]:

class configuration(object):
    def __init__(self, configFile = '~/.config/'+appShortName+'/config.ini'):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('starting configuration check')
        self.configPath = os.path.dirname(configFile)
        self.configFile = os.path.expanduser(configFile) # os.path.join(configPath, 'config.ini')
        self.logger.debug('config path: {}'.format(self.configPath))
        self.logger.debug('config file: {}'.format(self.configFile))
        self.getConfig()
    
    def writeConfig(self):
        # write out all the defined preferences (self.prefs) to the config file
        self.logger.debug('writing configuration to file: {}'.format(self.configFile))
        for key in self.prefs:
            eval ("self.parser.set('{0}', '{1}', self.{1})".format(self.mainSection, key))
        try:
            self.parser.write(open(os.path.expanduser(self.configFile), 'w'))
        except Exception as e:
            self.logger.error('Error writing configuration file: {}'.format(e))
    
    def printConfig(self):
        '''
        Prints configuration file for debugging'''
        for section in self.parser.sections():
            print 'Section: {0}'.format(section)
            for key in self.parser.options(section):
                print '{0} = {1}'.format(key, self.parser.get(section, key))
#         for key in self.prefs:
#             print '{0} ='.format(key), eval('self.{0}'.format(key))
    
    
    def getConfig(self, mainSection = 'Main'):
        '''
        Reads configuration file and sets the following attributes:
        '''
        
        self.logger.debug('getting configuration file')
        self.parser = ConfigParser.SafeConfigParser()
        
        # required options in the 'Main' section
        self.mainSection = mainSection
        
        # required key: [method for getting, default value]
        self.prefs = {
                        'mountpoint': [self.parser.get, '/Volumes/GoogleDrive'],
                        'teamdrive': [self.parser.get, ''],
                        'portfoliofolder': [self.parser.get, '']
        }
        
        # deal with the different working directories provided by various environments
        self.gradefolders = cwd+'/gradefolders.txt'

        # make sure a configuration path exists
        if len(self.parser.read(self.configFile)) <= 0:
            self.logger.warn('no configuration files found at: {}'.format(self.configFile))
            self.logger.info('creating configuration directory')
            try:
                os.makedirs(os.path.expanduser(self.configPath))
            except OSError as e:
                if e.errno != 17:
                    self.logger.critical(e)
                    sys.exit(1)
        
        # make sure there is a main section
        if not self.parser.has_section(self.mainSection):
            self.logger.info('')
            self.parser.add_section(self.mainSection)
        
        preferences = {}
        
        # read search for the expected preferences in the configuration file
        # note which are missing and set to the default values above
        for key in self.prefs:
            try:
                preferences[key] = self.prefs[key][0](self.mainSection, key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                self.parser.set(self.mainSection, key, self.prefs[key][1])
                preferences[key] = self.prefs[key][1]
                
        # set the values from the config
        for key in self.prefs:
            exec ("self.{0} = preferences['{0}']".format(key))


# In[5]:

class teamDrives(object):
    '''
    make working with google Team Drives through filestream a little easier
    '''

    def __init__(self, mountpoint='/Volumes/GoogleDrive/Team Drives/'):
        self.logger = logging.getLogger(__name__)
        self.mountpoint = mountpoint
        self.getDrives()
    
    def getDrives(self):
        self.logger.debug('Searching for Google Drive File Stream Mount Points')
        self.drives = {}
        try:
            drives = next(os.walk(self.mountpoint))[1]
        except Exception as e:
            self.logger.critical('error retriving list of Team Drives: {0}'.format(e))
            self.logger.critical('is Google Drive File Stream application running and configured?')
            self.logger.critical('mount point: {} is not accessible'.format(self.mountpoint))
            self.logger.critical('exiting')
            raise os.error('Error in os.walk for mount point: {0}'.format(self.mountpoint))
        for drive in drives:
            self.drives[drive] = oct(os.stat(self.mountpoint+drive).st_mode & 0o777)
    
    def listrwDrives(self):
        rwDrives = []
        for drive in self.drives:
            if 777 - int(self.drives[drive]) < 277:
                rwDrives.append(drive)
        return(sorted(rwDrives))
    
    def listFolders(self, teamDrive):
        try:
            folders = next(os.walk(self.mountpoint+teamDrive))[1]
        except Exception as e:
            self.logger.critical('Error getting list of Team Drives: {0}'.format(e))
            self.logger.critical('Is Google Drive File Stream application running and configured?')
            raise os.error('Error in os.walk for mount point: {0}'.format(self.mountpoint))
        return(folders)
    
    def find(self, pattern, teamDrive):
        result = []
        for root, dirs, files in os.walk(self.mountpoint+teamDrive):
            for name in dirs:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result
                
                
    

        


# In[6]:

def checkFSMount(mountpoint = '/Volumes/GoogleDrive'):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug('Searching for Google Drive File Stream Mount Points')
    # list the local partitions (including FUSE partitions)
    mount = subprocess.check_output(['df', '-hl'])
    mountLines = mount.split('\n')
    mountPoints = []
    
    # makek a list of all the partitions
    for line in mountLines:
        try:
            # re extract anything that looks like a mount point
            mountSearch = re.search('\s+(\/[\S+]{0,})$', line)
            mountPoints.append(mountSearch.group(1))
        # ignore anything that doesn't match the re
        except Exception:
            pass    
    # check for mount point and try to launch the google drive file stream app
    if mountpoint in mountPoints:
        logger.debug('Found what appears to be a valid mountpoint at: {0}'.format(mountpoint))
        return True
    else:
        logger.info('Google Drive File Stream appears to not be running')
        return False
    


# In[7]:

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces
    """
    s = s.strip()
    s = strip_accents(s)
    return re.sub(r'(?u)[^-\w., ]', '', s)


# In[8]:

def strip_accents(s):
    s = unicode(s, "utf-8")
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')


# In[9]:

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


# In[16]:

class parseCSV(object):

    def __init__(self, filename = False, headers = []):
        '''
        Create a CSV object; creates an empty CSV object if no filename is passed
        accepts:
            filename (string): Path to CSV file
            headers (list): list of headers to expect on the first line of the CSV
            
        sets:
            filename (string): name of file
            expectedHeacders (list): list of headers that must be included
            headerMap (dictionary): lookup table of header <--> index
            csvList (list): list of all CSV elements
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.filename = os.path.expanduser(filename)
        self.expectedHeaders = headers
        self.headerMap = {}
        self.csvList = False
        self.headersOK = False
        self.readCSV(self.filename)
        
    def readCSV(self, filename):
        '''
        process a CSV into a list object and map indexes to headers 
        only after successful processing sets params below
        accepts:
            filename (string): path to CSV file
            
        sets:
            filename (string): path to file
            csvList (list): list of all CSV elements
            headerMap (dictionary): lookup table of header <--> index
        '''
        # allow an parser object to be created with no filename
        if not filename:
            return() 
        self.logger.info('parsing CSV {0}'.format(filename))
        # raw CSV
        csvList = []

        # map of positions in CSV
        headerMap = {}

        # read the csv file in Universal newline mode (rU)    
        try:
            with open(filename, 'rU') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    csvList.append(row)
        except (OSError, IOError) as e:
            self.logger.critical('error reading file {}\n{}'.format(self.filename, e))
            return(False)

        # if len > 1, set the object properties
        if len(csvList) > 1:
            self.logger.info('{} student records found'.format(len(csvList)-1))
            self.filename = filename
            self.csvList = csvList
        else:
            self.logger.critical('no records found in file: {}.'.format(self.filename))
            self.logger.critical('please check that the above file is a comma sepparated values file (CSV)')
            return(False)
        
        self.mapHeaders()

        
    def mapHeaders(self):
        '''
        map headers to list indicies
        sets:
            headerMap (dictionary): lookup table of header <--> index        
        '''
        # headers that were not inlcuded
        missingHeaders = []
        
        # pop the headers from the list
        csvHeader = self.csvList.pop(0)
        
        
        # check for the expected headers
        self.logger.info('checking for expected headers')
        for each in self.expectedHeaders:
            if not each in csvHeader:
                self.logger.warn('missing header: {0}'.format(each))
                missingHeaders.append(each)

        if len(missingHeaders) > 0:
            self.logger.critical('error in student record file: {}'.format(self.filename))
            self.logger.critical('The following header fields were missing:')
            self.logger.critical('{:>5}'.format(missingHeaders))
            self.logger.critical('*'*5)
            self.logger.critical('Please re-run the export and ensure that all of the following headers are included:')
            for each in self.expectedHeaders:
                self.logger.critical('{:>5}'.format(each))
                self.headersOK = False
        else:
            self.headersOK = True

        # map headers to their index
        for index, value in enumerate(csvHeader):
            self.headerMap[value]=index
            
    def lookup(self, index = 0, key = 0):
        '''
        lookup a row index in the list and return field specified by key
        accepts:
            index (integer): list index to return (defautlts to 0)
            key (string): key to lookup in headerMap 
        '''
        self.logger.info('looking up index: {0} for key: {1}'.format(index, key))
        if not key in self.headerMap:
            self.logger.warn('key: {0} not in headerMap'.format(key))
            return('')
        try:
            return(self.csvList[index][self.headerMap[key]])
        except (KeyError, IndexError) as e:
            if 'KeyError' in e:
                self.logger.warn('\"{0}\" not found in headerMap'.format(key))
                return('')
            if 'IndexError' in e:
                logger.warn('index out of range')
                return('')
    


# In[18]:

def main():
    
    # default location for configuration file - this will be created if needed
    cfgfile = '~/.config/'+appShortName+'/config.ini'
    
    # Create the Logger
    logger = logging.getLogger(__name__)

    for each in range (0, len(logger.handlers)):
        logger.removeHandler(logger.handlers[0])

    datefmt = '%y-%m-%d %H:%M:%S'

    logger.setLevel(logging.INFO)

    # file handler
    fileformat = '%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s'
    file_handler = logging.FileHandler(appShortName+'.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt = fileformat, datefmt = datefmt))

    # stream handler
    streamformat = '%(levelname)s: %(message)s'
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.CRITICAL)
    stream_handler.setFormatter(logging.Formatter(fmt = streamformat, datefmt = ''))

    # rotation handler
    fileformat = '%(asctime)s %(levelname)s - %(funcName)s: %(message)s'
    rotation_handler = RotatingFileHandler(appShortName+'.log', maxBytes = 500000, backupCount = 5)
    rotation_handler.setLevel(logging.DEBUG)
    rotation_handler.setFormatter(logging.Formatter(fmt = fileformat, datefmt = datefmt))


    # add handler to logger
    #logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(rotation_handler)
    logger.info('===================== Starting Log =====================')
    
    def getTeamDrive():
        '''menu interaction to ask for the appropriate team drive to search'''
        logger.debug('getting Team Drive name')
        try:
            myDrives.getDrives()
        except Exception as e:
            logger.critical(e)
            return(0)
        if len(myDrives.listrwDrives()) < 1:
            logger.critical('No Team Drives with write permissions available; exiting')
            return(0)
        else:
            rwDrivesMenu = simpleMenu.menu(name = 'Team Drives', items = myDrives.listrwDrives())        
            myDrive = rwDrivesMenu.loopChoice(optional = True, message = 'Which Team Drive contains the portfolio folder?')
 
            if myDrive is 'Q':
                print 'exiting'
                return(1)
            return(myDrive)
    
    def getPortfolioFolder():
        '''menu interaction to ask for appropriate portfolio folder in a team drive'''
        logger.debug('beggining search for portfolio folder')
        print 'Searching in Team Drive: {0}'.format(myConfig.teamdrive)
        folderSearch = raw_input('Please enter part of the portfolio folder name (case sensitive search): ')
        logger.debug('searching TD \"{0}\" for \"{1}\"'.format(myConfig.teamdrive, folderSearch))
        fileList = myDrives.find(pattern = '*'+folderSearch+'*', teamDrive = myConfig.teamdrive)
        logger.debug('found {0} matches'.format(len(fileList)))
        if len(fileList) < 1:
            print 'No folders matching \"{0}\" found'.format(folderSearch)
            retry = retryMenu.loopChoice(optional = False, message = 'Would you like to try your search again?')
            if retry is 'Yes':
                getPortfolioFolder()
            if retry is 'No' or 'Quit':
                print 'exiting'
                return(1)
        
        # ask user to choose folder from list, quit or try again
        foldersMenu = simpleMenu.menu(name = 'Matching Folders', items = myDrives.find(
                                    pattern = '*'+folderSearch+'*', teamDrive = myConfig.teamdrive))
        myFolder = foldersMenu.loopChoice(optional = True, optchoices = {'Q': 'Quit', 'T': 'Try search with different folder name'},
                                        message = 'Which folder contains portfolios?')
        if myFolder is 'T':
            getPortfolioFolder()
        if myFolder is 'Q':
            print 'exiting'
            return(1)
                                                                         
        
        return(myFolder)
    
    def fileSearch(path, search = ''):
        '''search for a file name string in a given path'''
        logger.debug('searching path: {0} for {1}'.format(path, search))
        searchPath = os.path.expanduser(path)
        mySearch = '*'+search+'*'
        result = []
        try:
            allFiles = os.listdir(searchPath)
        except OSError as e:
            logger.warn(e)
            return(False)
        
        # list comprehension search with regex
        #http://www.cademuir.eu/blog/2011/10/20/python-searching-for-a-string-within-a-list-list-comprehension/
        regex = re.compile('.*('+search+').*')
        return([m.group(0) for l in allFiles for m in [regex.search(l)] if m])

    
    def getStudentFile(items = ['Desktop', 'Downloads', 'Documents']):
        '''menu interaction to ask for appropriate student_export.text file'''
        logger.debug('getting student_export.text file')
        foldersMenu = simpleMenu.menu(name = 'student_export file location', 
                                      items = items)
        foldersMenu.sortMenu()
        myFolder = foldersMenu.loopChoice(optional = True, message = 'Please specify the location of the student_export.text file')
        
        if myFolder is 'Q':
            print 'exiting'
            return(1)
        
        searchPath = '~/'+myFolder+'/'
        fileList = fileSearch(searchPath, 'text')
        if not fileList:
            print 'That folder does not appear to exist. Try again.'
            getStudentFile()
        
        fileMenu =simpleMenu.menu(name = 'student export files', items = fileList)
        foldersMenu.sortMenu()
        
        myFile = fileMenu.loopChoice(optional = True, message = 'Please choose the student_export text file to use')
        
        return(searchPath+myFile)
        
    
    def askContinue():
        '''menu interaction to ask if everything is correct and run the folder population'''
        logger.debug('prompting to continue')
        logger.debug('teamdrive: {0}'.format(myConfig.teamdrive))
        logger.debug('portfolio folder: {0}'.format(myConfig.portfoliofolder))
        continueMenu = simpleMenu.menu(name = 'Continue?', items = ['Yes', 'No: Set new team drive and folder'])
        response = continueMenu.loopChoice(optional = True, message = 'Continue with the portfolio folder: {0}'
                            .format(myConfig.portfoliofolder))
        if response is 'Yes':
            logger.info('using portfolio folder: {0}'.format(myConfig.portfoliofolder))
            myConfig.writeConfig()
            return(0)
        if response is 'No: Set new team drive and folder':
            #need to do something about this; make some defs for get teamdrive and portofolio folder 
            myConfig.teamdrive = getTeamDrive()
            myConfig.portfoliofolder = getPortfolioFolder()
            askContinue()
        if response is 'Q':
            print 'exiting'
            return(1)

    print 'Welcome to the portfolio creator for Google Team Drive!'
    print 'This program will create portfolio folders in Google Team Drive for students.'
    print 'You will need a student_export.text file from PowerSchool with at least the following information:'
    print 'ClassOf, FirstLast, Student_Number\n'
    print 'The order of the CSV does not matter, but the headers must be on the very first line.'
    print 'You will also need Google File Stream installed configured'
    print 'File Stream can be downloaded here: https://support.google.com/drive/answer/7329379?hl=en'
    raw_input("Press Enter to continue...\n\n\n")


        
    if checkFSMount():
        pass
    else:
        logger.info('Attempting to start Google Drive File Stream')
        try:
            gDriveFS = subprocess.check_call(["open", "-a", "Google Drive File Stream"])
        except subprocess.CalledProcessError as err:
            logger.warn('OS Error: {0}'.format(err))
            logger.critical('Google Drive File Stream does not appear to be installed. Please download from the link below')            
            logger.critical('https://support.google.com/drive/answer/7329379?hl=en')
            logger.critical('exiting')
            return(0)
        if checkFSMount():
            pass
        else:
            print "exiting"
            return(0)

    # get the configuration settings from the config.ini file
    logger.debug('getting configuration')
    myConfig = configuration(cfgfile)
    logger.info('=== Current Configuration Settings ===')
    for key in myConfig.prefs:
        try:
            logger.info('{0} -- {1}'.format(key, eval('myConfig.{0}'.format(key))))
        except Exception as e:
            pass
    
    # set the file stream drives object
    myDrives = teamDrives()
    
    # General purpose retry menu
    retryMenu = simpleMenu.menu(name = 'retry', items = ['Yes', 'No', 'Quit'])    
        
    if not myConfig.teamdrive:
        # if teamdrive is not in the configuration file, get it
        logger.info('no teamdrive set in configuration file')
        myConfig.teamdrive = getTeamDrive()
        if myConfig.teamdrive == 1:
            return(0)
    
    if not myConfig.portfoliofolder:
        # if portfolio folder is not in the configuration file, ask for it
        logger.info('no portfolio folder set in configuration file')
        myConfig.portfoliofolder = getPortfolioFolder()
        if myConfig.portfoliofolder == 1:
            return(0)
    
    # get the appropriate student file 
    studentFile = getStudentFile()
    
    # bail out if the getting the student failed
    if studentFile == 1:
        return(0)
    
    # bail out if user chose to quit
    if askContinue() == 1:
        return(0)
    
    # use the default ./gradefolders.txt file; if an alternative is on the desktop use that one instead
    logger.info('checking for alternative gradefolder.txt on Desktop')
    if os.path.exists(os.path.expanduser('~/Desktop/gradefolders.txt')):
        myConfig.gradefolders = os.path.expanduser('~/Desktop/gradefolders.txt')
        logger.info('set gradefolders path to: {}'.format(myConfig.gradefolders))
    else:
        logger.info('alternative not found; continuing with {0}'.format(myConfig.gradefolders))
        # check for grade folder description file
    
    # if there is no grade folder, bail out with the error messages below
    if not os.path.exists(myConfig.gradefolders):
        logger.critical('current working directory: {}'.format(cwd))
        logger.critical('"gradefolders.txt" file is missing in folder: {}'.format(cwd))
        logger.critical('gradefolders.txt should contain one grade level per line: \n00-Preeschool\n00-Transition Kindergarten\n00-zKindergarten...\n11-Grade\n12-Grade')
        logger.critical('please create a file named \"gradefolders.txt\" and place it on the Desktop')
        print 'exiting'
        return(1)
    
    # Open the gradefolders file and read all the lines into an array
    logger.info('opening grade folders file: {0}'.format(myConfig.gradefolders))
    # read in and sanitize the grade folders list (remove accents, invalid chars, etc)
    gradeFoldersList = fileRead(myConfig.gradefolders)
    if not gradeFoldersList:
        logger.critical('failed to open grade folders file')
        return(1)
    
    # open the student data file and start creating folders as needed
    myCSV = parseCSV(studentFile, headers = ['ClassOf', 'LastFirst', 'Student_Number'])
    
    if not myCSV.headersOK:
        logger.critical('error reading student file. exiting')
        return(1)
    
    # empty list for storing student paths to be created
    studentPathList = []
    
    # step through the CSV lines and build a list of directories that should be created
    for index, value in enumerate(myCSV.csvList):
        classOfString = get_valid_filename('Class Of-' + myCSV.lookup(index, 'ClassOf'))
        studentName = get_valid_filename(myCSV.lookup(index, 'LastFirst'))
        studentNumber = get_valid_filename(myCSV.lookup(index, 'Student_Number'))
        studentPathList.append('{0}/{1}/{2} - {3}'.format(myConfig.portfoliofolder, classOfString, studentName, studentNumber))
        

    # record failed, skipped creations
    makedirsFail = []
    makedirsSkip = []
    
    # step through the list of directories to create and creat them as needed
    for directory in studentPathList:
        logger.info('attempting to create directory: {0}'.format(directory))
        if not os.path.exists(directory):
            logger.info('creating directory')
            try:
                os.makedirs(directory)
            except OSError as e:
                logger.warn('Error creating directory: {0}'.format(e))
                makedirsFail.append(directory)
        else:
            logger.info('directory exists, skipping')
            makedirsSkip.append(directory)
    
    success = len(studentPathList) - len(makedirsFail) - len(makedirsSkip)
    logger.info('successfully created {0} of {1} student directories'.format(success, len(studentPathList)))
    logger.info('skipped: {0}'.format(len(makedirsSkip)))
    logger.info('errors: {0}'.format(len(makedirsFail)))
    if len(makedirsFail)>0:
        logger.info('failed to create:\n{0}'.format(makedirsFail))
            
        
    print '\n\n\nCompleted creating portfolio folders.'
    print 'successfully created {0} of {1} student directories'.format(success, len(studentPathList))
    print 'skipped (these already existed): {0}'.format(len(makedirsSkip))
    print 'errors: {0}'.format(len(makedirsFail))
    
    print '\n\n\n'
    print '='*10
    print 'Press CMD + Q to quit'
main()

