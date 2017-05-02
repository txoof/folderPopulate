
# coding: utf-8

# In[1]:

import sys
import re
#import datetime
import unicodedata
import csv
import logging
import argparse

# I kind of hate this
#from __future__ import print_function

import httplib2
import os

from datetime import datetime
from apiclient import discovery
from apiclient import errors 
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage 
from urlparse import urlsplit

# SCOPES = 'https://www.googleapis.com/auth/drive'
#SCOPES = 'https://www.googleapis.com/auth/drive.file' # try this one!
# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
# CLIENT_SECRET_FILE = 'client_secret_qs.json'
# APPLICATION_NAME = 'Drive API Python Quickstart'
APP_SHORT_NAME = 'portfolioCreator'


# # TODO:
# ## getCredentials
# * look into why on initial credential fetching script halts after deny/allow screen
# * needs to accept client_secrets; currently not using the proper path
# 
# ## imports:
# * check full imports and slim down?
# 
# ## logging
# * move logging configuration into main program
# 
# 

# In[2]:

def strip_accents(s):
    s = unicode(s, "utf-8")
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')


# In[3]:

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces
    """
    s = s.strip()
    s = strip_accents(s)
    return re.sub(r'(?u)[^-\w., ]', '', s)


# In[4]:

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


# In[6]:

def getWorkingPath():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath("__file__"))
    
    return(bundle_dir)


# In[7]:

def getCredentials(config_path = os.path.expanduser('~/.config/'+APP_SHORT_NAME), 
                   client_secret = './client_secret+'+APP_SHORT_NAME+'.json'):
    scopes = 'https://www.googleapis.com/auth/drive' # this is a bit expansive, consider a slimmer set
    
    # update this - this is not valid; need to pass in client_secret from the main module
    #client_secret = './client_secret_'+APP_SHORT_NAME+'.json'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(config_path, 'credentials')
    credential_file = os.path.join(credential_dir, APP_SHORT_NAME+'_credentials.json')
    flags = tools.argparser.parse_args([])
        
    if not os.path.exists(client_secret):
        logging.critical('fatal error - missing client secret file: {}'.format(client_secret))
        logging.critical('please obtain a client secret file and place it in the same dirctory as this script')
        logging.critical('filename: {}'.format(client_secret))
        logging.critical('instructions: https://developers.google.com/drive/v3/web/quickstart/python')
        sys.exit(1)
        
    logging.debug('checking for credentail store directory: {}'.format(credential_dir))
    if not os.path.exists(credential_dir):
        try:
            os.makedirs(credential_dir)
        except (IOError, OSError) as e:
            logging.critical(e)
    
    store = Storage(credential_file)
    creds = store.get()
    
    
    if not creds or creds.invalid:
        logging.debug('credential store not found or is invalid; refreshing')
        flow = client.flow_from_clientsecrets(client_secret, scopes)
        logging.debug('preparing to set store')
        creds = tools.run_flow(flow, store, flags)
        
    
    return(creds)
    


# In[8]:

class GDriveError(Exception):
    pass


# In[9]:

class gDrive():
    '''
    creates a google drive interface object
    
    Accepts:
    google drive v3 service object: (discover.build('drive', 'v3', credentials = credentials_object)
    
    '''
    def __init__(self, object):
        if  not isinstance(object, discovery.Resource):
            print ('Error: googleapicleint.discovery.Resource object expected')
            print ('{:>5}create a resource object:'.format(''))
            print ('{:>10}credentials = getCredentials(credJSON = "cleint_secret.json")'.format(''))
            print ('{:>10}service = discovery.build("drive", "v3", credentials=credentials)'.format(''))
            print ('{:>10}myDrive = gDrive(service)'.format(''))
            return(None)
        self.service = object
        # https://developers.google.com/drive/v3/web/mime-types
        self.mimeTypes = {'audio': 'application/vnd.google-apps.audio',
                          'docs': 'application/vnd.google-apps.document',
                          'drawing': 'application/vnd.google-apps.drawing',
                          'file': 'application/vnd.google-apps.file',
                          'folder': 'application/vnd.google-apps.folder',
                          'forms': 'application/vnd.google-apps.form',
                          'mymaps': 'application/vnd.google-apps.map',
                          'photos': 'application/vnd.google-apps.photo',
                          'slides': 'application/vnd.google-apps.presentation',
                          'scripts': 'application/vnd.google-apps.script',
                          'sites': 'application/vnd.google-apps.sites',
                          'sheets': 'application/vnd.google-apps.spreadsheet',
                          'video': 'application/vnd.google-apps.video'}
        
        # fields to include in partial responses
        # https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.create
        self.fields = ['id', 'parents', 'mimeType', 'webViewLink', 'size', 'createdTime', 'trashed', 'kind', 'name']
    
#     types = property()
    
    @property
    def types(self):
        '''
        Display supported mimeTypes
        '''
        print('supported mime types:')
        for key in self.mimeTypes:
            #print('%10s: %s' % (key, self.mimeTypes[key]))
            print('{:8} {val}'.format(key+':', val=self.mimeTypes[key]))
    
#     def quote(self, string):
#         '''
#         add double quotes arounda string
#         '''
#         return('"'+str(string)+'"')
    

    
    def add(self, name = None, mimeType = False, parents = None, 
            fields = 'webViewLink, mimeType, id', sanitize = True):
        '''
        add a file to google drive:
        
        args:
            name (string): human readable name
            mimeType (string): mimeType (see self.mimeTypes for a complete list)
            parents (list): list of parent folders
            fields (comma separated string): properties to query and return any of the following:
                'parents', 'mimeType', 'webViewLink', 
                'size', 'createdTime', 'trashed'
                'id'
            sanitize (bool): remove any field options that are not in the above list - false to allow anything
            
        '''

        fieldsExpected = self.fields
        fieldsProcessed = []
        fieldsUnknown = []
        
        if sanitize:
            # remove whitespace and unknown options
            for each in fields.replace(' ','').split(','):
                if each in fieldsExpected:
                    fieldsProcessed.append(each)
                else:
                    fieldsUnknown.append(each)
        else:
            fieldsProcessed = fields.split(',')
            
        if len(fieldsUnknown) > 0:
            logging.warn('unrecognized fields: {}'.format(fieldsUnknown))
        
        
        body={}
        if name is None:
            logging.error('expected a folder or file name')
            return(False)
        else:
            body['name'] = name
        
        if mimeType in self.mimeTypes:
            body['mimeType'] = self.mimeTypes[mimeType]
        
        if isinstance(parents, list):
            body['parents'] = parents
        elif parents:
            body['parents'] = [parents]
        
        apiString = 'body={}, fields={}'.format(body, ','.join(fieldsProcessed))
        logging.debug('api call: files().create({})'.format(apiString))
        try:
            result = self.service.files().create(body=body, fields=','.join(fieldsProcessed)).execute()
            return(result)
        except errors.HttpError as e:
            raise GDriveError(e)
            return(False)
        
        
        #body = {'name':'release the schmoo!', 'mimeType':'application/vnd.google-apps.folder', 'parents':["0BzC-V2QIsGRGWXNxNmhjc0FITDQ"]}
# service.files().create(body=body).execute()
        

    
    def search(self, name = None, trashed = None, mimeType = False, fuzzy = False, date = None, dopperator = '>', 
               parents = None, orderBy = 'createdTime', quiet = True):
        '''
        search for an item by name and other properties in google drive
        
        args:
            name (string): item name in google drive - required
            trashed (bool): item is not in trash - default None (not used)
            mimeType = (string): item is one of the known mime types (gdrive.mimeTypes) - default None
            fuzzy = (bool): substring search of names in drive
            date = (RFC3339 date string): modification time date string (YYYY-MM-DD)
            dopperator (date comparison opprator string): <, >, =, >=, <=  - default >
            parents = (string): google drive file id string
            orderBy = (comma separated string): order results assending by keys below - default createdTime:
                        'createdTime', 'folder', 'modifiedByMeTime', 
                        'modifiedTime', 'name', 'quotaBytesUsed', 
                        'recency', 'sharedWithMeTime', 'starred', 
                        'viewedByMeTime'
            fields (comma separated string): properties to query and return any of the following:
                'parents', 'mimeType', 'webViewLink', 
                'size', 'createdTime', 'trashed'
                'id'
            sanitize (bool): remove any field options that are not in the above list - false to allow anything
                        
                        
            
        returns:
            list of file dict
        '''
        features = ['name', 'trashed', 'mimeType', 'date', 'parents']
        build = {'name' : 'name {} "{}"'.format(('contains' if fuzzy else '='), name),
                 'trashed' : 'trashed={}'. format(trashed),
                 'mimeType' : 'mimeType="{}"'.format(self.mimeTypes[mimeType] if mimeType in self.mimeTypes else ''),
                 'parents': '"{}" in parents'.format(parents),
                 'date': 'modifiedTime{}"{}"'.format(dopperator, date)}

        
        # provides for setting trashed to True/False if the input is not None
        if not isinstance(trashed, type(None)):
            # set to true as the variable is now in use, but it's value has been set above
            trashed = True
        
        qList = []

        # evaluate feature options; if they are != None/False, use them in building query
        for each in features:
            if eval(each):
                qList.append(build[each])
                
        if not quiet:
            print(' and '.join(qList))
        
        apiString = 'q={}, orderBy={})'.format(' and '.join(qList), orderBy)
        logging.debug('apicall: files().list({})'.format(apiString))
        try:
            # build a query with "and" statements
            result = self.service.files().list(q=' and '.join(qList), orderBy=orderBy).execute()
            return(result)
        except errors.HttpError as e:
            raise GDriveError(e)
            return(False)

    def ls(self, *args, **kwargs):
        '''
        List files in google drive using any of the following properties:
            
        accepts:
            name (string): item name in google drive - required
            trashed (bool): item is not in trash - default None (not used)
            mimeType = (string): item is one of the known mime types (gdrive.mimeTypes) - default None
            fuzzy = (bool): substring search of names in drive
            date = (RFC3339 date string): modification time date string (YYYY-MM-DD)
            dopperator (date comparison opprator string): <, >, =, >=, <=  - default >
            parent = (string): google drive file id string    
        '''
        try:
            result = self.search(*args, **kwargs)
            for eachFile in result.get('files', []):
                print('name: {f[name]}, ID:{f[id]}, mimeType:{f[mimeType]}'.format(f=eachFile))
            return(result)
        except GDriveError as e:
            raise GDriveError(e)
            
    
    
    def getprops(self, fileId = None, fields = 'parents, mimeType, webViewLink', sanitize=True):
        '''
        get a file or folder's properties based on google drive fileId
        
        for a more complete list: https://developers.google.com/drive/v3/web/migration
        
        args:
            fileId (string): google drive file ID
            fields (comma separated string): properties to query and return any of the following:
                'parents', 'mimeType', 'webViewLink', 'size', 'createdTime', 'trashed'
            sanitize (bool): remove any field options that are not in the above list - false to allow anything
            
        returns:
            list of dictionary - google drive file properties
            
        raises GDriveError
        '''
        fieldsExpected = self.fields
        
        fieldsProcessed = []
        fieldsUnknown = []

        if sanitize:
            # remove whitespace and unknown options
            for each in fields.replace(' ','').split(','):
                if each in fieldsExpected:
                    fieldsProcessed.append(each)
                else:
                    fieldsUnknown.append(each)
        else:
            fieldsProcessed = fields.split(',')
        if len(fieldsUnknown) > 0:
            print ('unrecognized fields: {}'.format(fieldsUnknown))
        
        apiString = 'fileId={}, fields={}'.format(fileId, ','.join(fieldsProcessed))
        logging.debug('files().get({})'.format(apiString))
        try:
            result = self.service.files().get(fileId=fileId, fields=','.join(fieldsProcessed)).execute()
            return(result)
        except errors.HttpError as e:
            raise GDriveError(e)
            return(False)
        

    def parents(self, fileId):
        """get a file's parents.

        Args:
            fileId: ID of the file to print parents for.
        
        raises GDriveError
        """
        apiString = 'fileId={}, fields="parents"'.format(fileId)
        logging.debug('api call: {}'.format(apiString))
        try:
            parents = self.service.files().get(fileId=fileId, fields='parents').execute()
            return(parents)
        except errors.HttpError as e:
            raise GDriveError(e)
            return(False)
    
    def rm(self):
        pass


# In[15]:

# alternatively pass in the configuration object?
def gDrivePopulate(gdBaseFolderURL = '', gradeFoldersFile = './gradefolders.txt', 
                   studentInfo = '', client_secret = './client_secret_'+APP_SHORT_NAME+'.json', outputPath = os.path.expanduser('~/')):
    
    gdBaseFolderId = urlsplit(gdBaseFolderURL).path.split('/')[-1]
    
#     # this needs to be moved out of this def and moved into the main loop of the other program
#     # init the log; this removes any old log handlers (this is particularly useful when testing in an IDE)
#     log = logging.getLogger()
#     logging.getLogger("googleapiclient").setLevel(logging.ERROR)

#     # useful for removing old log handlers when developing from an IDE such as Jupyter
#     if len(log.handlers) > 0:
#         for each in range(0, len(log.handlers)):
#             log.removeHandler(log.handlers[0])
    
    
#     # set the log format
#     logFormatter = logging.Formatter('[%(levelname)8s %(asctime)s] %(message)s', '%Y-%m-%d %H:%M')
#     #consoleFormatter = logging.Formatter('[%(levelname)-8s] %(message)s')
#     consoleFormatter = logging.Formatter('[%(levelno)-3s] %(message)s')
#     # set root logger
#     rootLogger = logging.getLogger()       
    
#     # set the logging level for the api discovery service to "ERROR"
#     logging.getLogger('discovery').setLevel(logging.ERROR)

    
#     # add a conshole handle to the root logger
#     consoleHandler = logging.StreamHandler(sys.stdout)
# #     consoleHandler.setFormatter(logFormatter)
#     consoleHandler.setFormatter(consoleFormatter)
#     rootLogger.addHandler(consoleHandler) 
    
#     # Set default logging level
#     rootLogger.setLevel(logging.DEBUG)
# #     rootLogger.setLevel(logging.WARNING)
# #     rootLogger.setLevel(logging.INFO)
    
        
    logging.info('checking google credentials')
    try:
        credentials = getCredentials(client_secret = client_secret)
    except SystemExit:
        logging.critical('You have chosen to deny access to google drive.')
        logging.critical('This program cannot continue without access to google drive.')
        
    http = credentials.authorize(httplib2.Http())
    
    logging.debug('building api discovery service')
    
    try:
        service = discovery.build('drive', 'v3', http=http, cache_discovery=False)
    except Exception as e:
        logging.critical('Error communicating with Google: {}'.format(e))
        logging.critical('exiting')
        return(False)

    logging.debug('preparing google drive object')
    myDrive = gDrive(service)

    # path to desktop of this user (this should work on macs)
    desktopPath = pathify([os.path.expanduser('~')], 'Desktop')

    # Fields expected in CSV file containing student data
    # move this into a resource file? - see the folder list below
    expected = ['ClassOf', 'LastFirst', 'Student_Number']

    # map of CSV fields to elements in list
    headerMap = {}

    # list of folders to populate into each students' folder
    if os.path.exists(desktopPath+'gradefolders.txt'):
        gradeFoldersFile = desktopPath + 'gradefolders.txt'

    # list of student information
    studentLinks = []
    
    # list of problem students
    studentFailure = []
    
    # list containing CSV
    studentCSV = []

    # new students created
    studentsCreated = 0
    
    # Grade folders created
    foldersCreated = 0
    
    outputFileName = 'Student_URLs-'+datetime.today().strftime('%Y-%m-%d_%H.%M')+'.csv'
    
    # list of folders to add under each students' path
    logging.info('reading list of folders to create for each student:')
    gradeFolders = fileRead(gradeFoldersFile)

    if gradeFolders:
        logging.info('Folders to be created for each student: {}'.format(len(gradeFolders)))
        logging.info('{:>5}List of folders to be created for each student:'.format(''))
        
        for folder in gradeFolders:
            logging.info('{:>10}{}'.format('', folder))

    else:
        logging.critical('default grade folders file is missing')
        logging.critical('please place a file named "folders.txt" containing a list of folders (one on each line) on the Desktop')
        logging.critical('exiting')
        return(False)

    # read the csv file in Universal newline mode (rU)
    logging.info('reading student CSV file')
    try:
        with open(studentInfo, 'rU') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                studentCSV.append(row)
    except (OSError, IOError) as e:
        logging.critical('error reading file: {}\n{}'.format(studentInfo, e))
        logging.critical('exiting')
        return(False)

    # check if there is content in the CSV
    if len(studentCSV) > 1:
        logging.info('{} student records found in {}'.format(len(studentCSV)-1, studentInfo))
#         print('{} student records found in {}'.format(len(studentCSV)-1, studentInfo))
    else:
        logging.critical('no student records found in {}'.format(studentInfo))
        logging.critical('exiting') 
        return(False)

    # check for expected headers in CSV data
    # pop the headers from the list
    csvHeader = studentCSV.pop(0)
    missingHeaders = []
    for each in expected:
        if each not in csvHeader:
            missingHeaders.append(each)

    if len(missingHeaders) > 0:
        loggig.critical('error reading student student CSV fle: {}'.format(studentInfo))
        for each in missingHeaders:
            print('{:>5} missing header: {}'.format(studentInfo, each))
        logging.critical('please recreate file {} with all required headers:'.format(studentInfo))
        logging.critical('{:>5}'.format(expected))
        logging.critical('stopping')
        return(False)

    # map headers to their index
    for index, value in enumerate(csvHeader):
        headerMap[value]=index
    
    # process the CSV and start creating folders

    studentRecords = [] # list of student name, id number, etc, and dict of google information
    studenetFailures = [] # list of students that had one failure or another
    gdClassOfFoldersDict = {} # dict of created or discovered Class Of xxxx folders
    
    ### check for BASE FOLDER before continuing
    # if it does not exist inform the user and bail
    logging.info('checking for student portfolio folder on google drive')
    try:
        gdBaseFolder = myDrive.getprops(fileId = gdBaseFolderId, fields = 'webViewLink, id')
    except GDriveError as e:
        logging.critical('Error checking for student portfolio directory')
        logging.critical(e)
        return(False)
    except Exception as e:
        logging.critical('unexpected error: {}'.format(e))
        return(False)

    if not gdBaseFolder.get('webViewLink'):
        logging.critical('Fatal error: student portfolio directory not found')
        logging.critical('the supplied google drive URL is not valid; please update and try again')
        logging.critical(gdBaseFolderURL)
        return(False)

    ### loop through students in the 
    logging.info('Searching for existing google drive folders and creating missing folders...')
    for index, student in enumerate(studentCSV):
    
        ## check if the Class OF folder exists, record in  (gdClassOfFoldersList)
        # it it does not exist, create it and record 
        # if more than one exists, inform the user

        classOf = 'Class Of-' + student[headerMap['ClassOf']]

        logging.info('#'*20)
        logging.info('searching google drive portfolio folder for: {}'.format(classOf))
        # check to see if 'Class Of' folder has been accessed before
        if classOf in gdClassOfFoldersDict:
            gdClassOfFolder = gdClassOfFoldersDict[classOf]
            logging.debug('folder has been previously accessed')
        else: # search google drive for the folder
            try:
                folder = myDrive.search(name = classOf, parents = gdBaseFolderId, orderBy = 'createdTime', 
                                        trashed = False, mimeType = 'folder')
            except GDriveError as e:
                logging.error('error processing student: {}'.format(student[headerMap['LastFirst']]))
                logging.error(e)
                studentFailure.append(student)
                continue
            except Exception as e:
                logging.critical('Fatal error. Exiting')
                logging.critical(e)
                return(False)

            # check for results
            # always check for the oldest - [files][0] (set by orderBy = 'createdTime)
            if len(folder['files']) > 0:
                logging.debug('{:>5}{} folder found'.format('', classOf))
                gdClassOfFolder = folder['files'][0].get('id')
            else:
                logging.debug('{:>5}folder not found. creating.'.format(''))
                # create a folder if no results were found
                try:
                    folder = myDrive.add(name = classOf, parents = gdBaseFolderId, mimeType = 'folder')
                except GDriveError as e:
                    logging.error('error processing student {}'.format(student[headerMap['LastFirst']]))
                    logging.error(e)
                    studentFailure.append(student)
                    continue
                except Exception as e:
                    logging.critical('Fatal error. Exiting')
                    logging.critical(e)
                    return(False)

                gdClassOfFolder = folder.get('id')

            gdClassOfFoldersDict[classOf] = gdClassOfFolder
            
        # end Class Of Folder check

        ## check if the student folder exists in the class of folder gdStudentFolder
        # if it does, record 
        # if it does not, create and record
        # if more than one exists, inform the user

        studentFolder = student[headerMap['LastFirst']] + ' - ' + student[headerMap['Student_Number']]

        logging.info('{:>5}searching for student folder: {}'.format('',studentFolder))
        logging.debug('{:>5}searching parent folder: {}'.format('',gdClassOfFoldersDict[classOf]))

        # search for the "class of" folder within the root of the portfolio structure
        try:
            folder = myDrive.search(name = studentFolder, trashed = False, mimeType = 'folder',
                                   parents = gdClassOfFoldersDict[classOf], orderBy = 'createdTime')
        except GDriveError as e:
            logging.error('{:>5}error processing student {}'.format('',student[headerMap['LastFirst']]))
            logging.error(e)
            studentFailure.append(student)
            continue
        except Exception as e:
            logging.critical('Fatal error. Exiting')
            logging.critical(e)
            return(False)
        
        # if results are returned, get the properties of the first returned folder
        if len(folder['files']) > 0:
            logging.debug('{:>5}getting properties of folder'.format(''))
            try:
                gdStudentFolder = myDrive.getprops(fileId = folder['files'][0].get('id'), fields = 'id, webViewLink' )
            except GDriveError as e:
                logging.error('{:>5}error processing student {}'.format('',student[headerMap['LastFirst']]))
                logging.error(e)
                studentFailire.append(student)
                continue
            except Exception as e:
                logging.critical('Fatal error. Exiting')
                logging.critical(e)
                return(False)                
            
            logging.info('{:>5}existing student folder found'.format(''))
        else:
            logging.info('{:>5}creating student folder'.format(''))
            try:
                folder = myDrive.add(name = studentFolder, mimeType = 'folder', 
                                     parents = gdClassOfFoldersDict[classOf], fields = 'webViewLink, id')
                # add one to the students created
                studentsCreated += 1
                
                
            except GDriveError as e:
                logging.error('{:>5}error processing student {}'.format('',student[headerMap['FirstLast']]))
                studentFailure.append(student)
                continue
            except Exception as e:
                logging.critical('Fatal error. Exiting')
                logging.critical(e)
                return(False)
            logging.debug('{:>5}folder created'.format(''))
            gdStudentFolder = folder # save the gdStudentFolder for the grade folder check
            
        logging.debug('{:>5}student data: {}'.format('', student))
        logging.debug('{:>5}webViewLink: {}'.format('', folder.get('webViewLink')))
        logging.debug('{:>5}(API v2) embedLink: {}'.format(
            '','https://drive.google.com/a/ash.nl/embeddedfolderview?id='+gdStudentFolder.get('id')) )
        # the webViewLink will not display properly in an iFrame
        # this method is supported in v2 of the API (embedLink), but not V3; 
        # this is a hack and may break when v2 is depricated
        # - https://drive.google.com/a/ash.nl/embeddedfolderview?id=
        student.append('https://drive.google.com/a/ash.nl/embeddedfolderview?id='+gdStudentFolder.get('id'))
        #student.append(gdStudentFolder.get('webViewLink'))
        studentLinks.append(student)
            
        
        # end of student folder
    
        ## loop through all of the grade folders (02-Grade, 03-Grade...) check if gdGradeFolder exists
        # if it does continue to next folder
        # if it does not, record
        for eachFolder in gradeFolders:
            
            logging.info('{:>10}searching for grade folder: {}'.format('',eachFolder))
            try:
                folder = myDrive.search(name = eachFolder, mimeType = 'folder', trashed = False, 
                                             parents = gdStudentFolder.get('id'), orderBy = 'createdTime')
            except GDriveError as e:
                logging.error('{:>10}error processing student {}'.format('',student[headerMap['FirstLast']]))
                studentFailure.append(student)
                continue
            except Exception as e:
                logging.critical('Fatal error. Exiting')
                logging.critical(e)
                return(False)
                
            if len(folder['files']) > 0:
                logging.info('{:>10}folder exists, no action needed: {}'.format('', eachFolder))
                continue
            else:
                logging.info('{:>10}creating folder: {}'.format('', eachFolder))
                try:
                    folder = myDrive.add(name = eachFolder, mimeType = 'folder', 
                                         parents = gdStudentFolder.get('id'))
                except GDriveError as e:
                    logging.error('{:>10}error processing student {}'.format('',student[headerMap['FirstLast']] ))
                    studentFailure.append(student)
                    continue
                except Exception as e:
                    logging.critical('Fatal error. Exiting')
                    logging.critical(e)
                    return(False)
                # record created folder statistics
                foldersCreated += 1
                
    
    ### Generate CSV output from Student Links
    csvHeader.append('StudentURL')
    headerFmtString = '{}, {}, {}\n'.format(csvHeader[headerMap['LastFirst']], csvHeader[headerMap['Student_Number']], 
                    csvHeader[-1])
    csvFmtString = '"{}", {}, "<a href={}>Student Portfolio for {}</a>"\n'
    # update to use passed in output folder
#     studentURLData = os.path.expanduser('~/Desktop/Student_URL_Data.csv')
    studentURLData = os.path.join(os.path.expanduser(outputPath), outputFileName)

    
    logging.info('#'*20)
    logging.info('all records processed')
    logging.info('{} new student folders created on on Google Drive'.format(studentsCreated))
    logging.info('{} grade folders created on Google Drive'.format(foldersCreated))
    logging.info('view student folders at this link: {}'.format(gdBaseFolderURL))
    logging.info('{} failures to create folders'.format(len(studentFailure)))
    
    if len(studentFailure) > 0:
        logging.warn('following students had one or more problems:')
        for each in studentFailure:
            logging.warn(each)
    
    
    logging.info('writing CSV file: {}'.format(studentURLData))
    try:
        with open(studentURLData, 'w') as f:
            f.write(headerFmtString)
            for eachRecord in studentLinks:
                f.write(csvFmtString.format(eachRecord[headerMap['LastFirst']], eachRecord[headerMap['Student_Number']], 
                        eachRecord[-1], eachRecord[headerMap['LastFirst']]))
    except (IOError, OSError) as e:
        print e

    
        


# In[16]:

# foo = gDrivePopulate(gdBaseFolderURL = 'https://drive.google.com/drive/folders/0B9WTleJ1MzaYcmdmTWNNNF9pa1E',
#                     gradeFoldersFile = './gradefolders.txt', 
#                     client_secret = '/Users/aciuffo/.config/portfolioCreator/credentials/portfolioCreator_credentials.json', 
#                     studentInfo = 'student_export.text')


