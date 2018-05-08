
# coding: utf-8

# In[1]:

from Tkinter import *
import tkFileDialog
import sys
import ConfigParser
import os
import logging
import re
from datetime import datetime
from gDrivePopulate import *
oldstdout = sys.stdout
APP_SHORT_NAME = 'portfolioCreator'
APP_VERSION = '2017.05.02_18:21'
ABOUT = 'Written by Aaron Ciuffo aciuffo@ash.nl'


# In[2]:

class IORedirector(object):
    '''A general class for redirecting I/O to this Text widget.'''
    def __init__(self,text_area):
        self.text_area = text_area
        
#     def flush(self):
#         pass

class StdoutRedirector(IORedirector):
    '''A class for redirecting stdout to this Text widget.'''

    def write(self,string):
        self.text_area.insert("end", string)
        self.text_area.see(END)

    def flush(self):
        pass


# In[ ]:

def getWorkingPath():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath("__file__"))
    
    return(bundle_dir)


# In[ ]:

class myApp(object):
    def __init__(self, master):
        self.master = master
        self.master.title(APP_SHORT_NAME)
        
        # configuration attributes
        self.configPath = os.path.expanduser('~/.config/'+APP_SHORT_NAME)
        self.configFile = os.path.join(self.configPath, 'config.ini')
        
        # FILES
        #student CSV to import
        self.studentFile = None
        
        #student CSV to export
        self.studentData = None
        
        #default folders to create
        self.gradeFolderFile = os.path.join(getWorkingPath(), 'gradefolders.txt')
        
        #client secret file
        self.clientSecret = os.path.join(getWorkingPath(), 'client_secret_folderPopulate.json')
        
        
        # attributes to pass to the google drive object
        #self.gdBaseFolder = 'https: //drive.google.com/PASTE/LINK/FOR/ASSESSMENT/FOLDER/URL/HERE'
        
        self.getConfig()
        
        
        self.guiInit()
        
        
    def guiInit(self):
        labelURL_text = 'Google Drive URL:'
        inputFile_text = 'Student CSV File:'# ClassOf,Grade_Level,LastFirst,Student_Number'
        inputFile_button = 'Browse...'
        outputFile_text = 'Output CSV File Location:'
        outputFile_button = 'Choose...'
        
        submit_button = 'Start'
        quit_button = 'Quit'        
        
        minColSize = 650
        
        geometry = str(minColSize+300)+'x300+30+30'
        
        self.master.geometry(geometry)
        self.launchWindow()
        
        print 'Initializing...'
        print '\n'*3
        print 'The first time this program is run you will be asked to authroize use of your google drive.'
        print 'It is important to choose "Allow"'
        print '\n'*2
        print 'After pressing "Start", you may see a spinning beach ball for several minutes.'

        
        # add a menu bar
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)
        
        self.filemenu = Menu(self.menubar)
        self.menubar.add_cascade(label='Log Level', menu=self.filemenu)
        
        # lambda explanation here: http://stackoverflow.com/questions/27923347/tkinter-menu-command-targets-function-with-arguments
        self.filemenu.add_command(label='Error', command = lambda: self.setLogLevel('ERROR'))
        self.filemenu.add_command(label='Warnings', command = lambda: self.setLogLevel('WARN'))
        self.filemenu.add_command(label='Info', command = lambda: self.setLogLevel('INFO'))
        self.filemenu.add_command(label='Debug', command = lambda: self.setLogLevel('DEBUG'))
        
        self.windowmenu = Menu(self.menubar)
        self.menubar.add_cascade(label='Window', menu=self.windowmenu)
        
        self.windowmenu.add_command(label = 'Output Window', command = self.launchWindow)
        
        
        stepOne = LabelFrame(self.master, text = "1. Enter URL for Google Drive Assessment Folders:")
        stepOne.grid(row = 0, columnspan = 7, sticky = 'WE', padx = 5, pady = 5, ipadx = 5, ipady = 5)
        stepOne.columnconfigure(1, weight = 1, minsize = minColSize)
        
        labelURL = Label(stepOne, text=labelURL_text, font = "TkDefaultFont 0 bold")
        labelURL.grid(row=0, column=0, sticky=E, padx=5, pady=2)

        self.entryURL = Entry(stepOne)
        self.entryURL.grid(row=0, column=1, columnspan=6, sticky="WE", pady=3)
        self.entryURL.insert(END, self.gdBaseFolder)
        
        stepTwo = LabelFrame(self.master, text = '2. Select Student CSV File:')
        stepTwo.grid(row = 1, columnspan = 7, sticky = 'WE', padx = 5, pady = 5, ipadx = 5, ipady = 5)
        stepTwo.columnconfigure(1, weight = 0, minsize = minColSize)
        
        labelInputFile = Label(stepTwo, text = inputFile_text, font = "TkDefaultFont 0 bold")
        labelInputFile.grid(row = 0, column = 0, sticky = E, padx = 5, pady = 5)

        self.labelInputFileSelection_text = StringVar()
        self.labelInputFileSelection_text.set('None Selected')
        self.labelInputFileSelection = Label(stepTwo, textvariable = self.labelInputFileSelection_text)
        self.labelInputFileSelection.grid(row = 0, column = 1, sticky = W)

        buttonInputFile = Button(stepTwo, text = inputFile_button, command = self.inputFilePicker)
        buttonInputFile.grid(row = 0, column = 2, sticky = 'W', padx = 5, pady = 2)
        
        labelOutputFile = Label(stepTwo, text = outputFile_text, font = "TkDefaultFont 0 bold")
        labelOutputFile.grid(row = 1, column = 0, sticky = E, padx = 5, pady =5)
        
        self.labelOutputFileLocation_text = StringVar()
        self.labelOutputFileLocation_text.set(self.outputFolder)
        self.labelOutFolder = Label(stepTwo, textvariable = self.labelOutputFileLocation_text)
        self.labelOutFolder.grid(row = 1, column = 1, sticky = W)
        
        buttonOutputFileLocation = Button(stepTwo, text = outputFile_button, command = self.outputFolderPicker)
        buttonOutputFileLocation.grid(row = 1, column = 2, sticky = W, padx = 5, pady = 2)
        
        stepThree = LabelFrame(self.master, text = '3. Begin Folder Creation on Google Drive')
        stepThree.grid(row = 2, columnspan = 7, sticky = 'WE', padx = 5, pady = 5, ipadx = 5, ipady = 5)
        stepThree.columnconfigure(1, weight = 1, minsize = minColSize)
        
        buttonSubmit = Button(stepThree, text = submit_button, command = self.submit,  highlightbackground = '#2EFF00')
        buttonSubmit.grid(row = 0, column = 0, sticky = 'WE')
        
        buttonQuit = Button(self.master, text = quit_button, command = self.quit, highlightbackground='#FF2D00')
        buttonQuit.grid(row = 3, column = 0, sticky = 'WE', padx = 5, pady = 5)

    def setLogLevel(self, level):
        self.loglevel = level
        self.rootLogger.setLevel(getattr(logging, level))
        logging.info('Log Level: {}'.format(self.loglevel))
        
    def quit(self):
        self.master.destroy()

    def submit(self):
        if self.studentFile is None:
            logging.error('No Student Information file selected. Please select a file.')
            return(False)
        
        # check for a valid URL format
        urlRegex = re.compile(
            r'^(?:https)://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        logging.debug('checking validity of entered URL')
        if re.match(urlRegex, self.entryURL.get()): 
            self.gdBaseFolder = self.entryURL.get()
            logging.info('URL format OK')
        else:
            logging.error('Google Drive folder is not a valid URL:\n {}'.format(self.entryURL.get()))
            logging.error('Please update the URL and try again.')
            return(False)
            
        logging.debug('writing configuration to file: {}'.format(self.configFile))
        
        # set any changes to the config parser object to be written
        self.parser.set(self.mainSection, 'gdBaseFolder', self.gdBaseFolder)
        self.parser.set(self.mainSection, 'outputFolder', self.outputFolder)
        self.parser.set(self.mainSection, 'loglevel', self.loglevel)
        
        try:
            self.parser.write(open(self.configFile, 'w'))
        except Exception as e:
            logging.error('Error writing configuration file: {}'.format(e))
            
                
        logging.debug('student file: {}'.format(self.studentFile.name))
        logging.debug('grade folder file: {}'.format(self.gradeFolderFile))
        logging.debug('output folder: {}'.format(self.outputFolder))
        
        print 'starting run... this may take a LONG time.'
        gDriveResult = gDrivePopulate(gdBaseFolderURL = self.gdBaseFolder, 
                                      #gradeFoldersFile = './gradefolders.txt',
                                      gradeFoldersFile = self.gradeFolderFile,
                                      client_secret = self.clientSecret,
                                      studentInfo = self.studentFile.name,
                                      outputPath = self.outputFolder)
        
        logging.info('Completed with result: {}'.format(gDriveResult))
        return(gDriveResult)
    
    
    def launchWindow(self):
        '''
        Launch an output window
        '''
        self.redirector('')
        # logging needs to be redirected each time the output window is launched
        self.configLogging()
        logging.info(APP_SHORT_NAME)
        logging.info('Version: {}'.format(APP_VERSION))
    
    def inputFilePicker(self):
        try:
            stuFile = tkFileDialog.askopenfile(mode='r', title='Choose exported student data')
        except (IOError, OSError) as e:
            print e
            return(False)
        
        if stuFile.name:
            self.studentFile = stuFile
            self.labelInputFileSelection_text.set(self.studentFile.name)
        
        
        return(self.studentFile.name)
    
    def outputFolderPicker(self):
        try:
            folder = tkFileDialog.askdirectory(title = 'Choose output folder')

        except (IOError, OSError) as e:
            print e
            return(False)
        if len(folder) > 0:
            self.outputFolder = folder
            self.labelOutputFileLocation_text.set(self.outputFolder)
#             self.labelOutFolder_text.set(self.outputFolder)            

    def redirector(self, inputStr=""):
        wX = 800
        wY = 600
        geometry = '{}x{}+40+350'.format(wX, wY)
        import sys
        root = Toplevel()
        root.geometry(geometry)
        T = Text(root, font = 'Courier 14', foreground='white', width = wX, height = wY)
        T.config(background='black')
        sys.stdout = StdoutRedirector(T)
        T.pack()
        T.insert(END, inputStr)

    def configLogging(self):
        # init the log; this removes any old log handlers (this is particularly useful when testing in an IDE)
        log = logging.getLogger()
        logging.getLogger("googleapiclient").setLevel(logging.ERROR)

        # useful for removing old log handlers when developing from an IDE such as Jupyter
        if len(log.handlers) > 0:
            for each in range(0, len(log.handlers)):
                log.removeHandler(log.handlers[0])


        # set the log format
        #logFormatter = logging.Formatter('[%(levelname)8s %(asctime)s] %(message)s', '%Y-%m-%d %H:%M')
        #consoleFormatter = logging.Formatter('[%(levelname)-8s] %(message)s')
        consoleFormatter = logging.Formatter('[%(levelno)-3s] %(message)s')
        # set root logger
        self.rootLogger = logging.getLogger()       

        # set the logging level for the api discovery service to "ERROR"
        logging.getLogger('discovery').setLevel(logging.ERROR)

        # add a console handler to the root logger
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(consoleFormatter)
        self.rootLogger.addHandler(consoleHandler) 

        # Setlogging level
        self.rootLogger.setLevel(getattr(logging, self.loglevel))
        logging.critical('LogLevel: {}'.format(self.loglevel))
        
    def getConfig(self):
        '''
        Reads configuration file and sets the following attributes:
            self.gdBaseFolder
            self.outputFolder
            self.loglevel'''
        
        self.parser = ConfigParser.SafeConfigParser()
        
        # required options in the 'Main' section
        self.mainSection = 'Main'
        # required key: [method for getting, default value]
        prefs = {'gdBaseFolder': [self.parser.get, 'https: //drive.google.com/PASTE/LINK/FOR/ASSESSMENT/FOLDER/URL/HERE'],
                 'outputFolder': [self.parser.get, os.path.expanduser('~/Desktop/')],
                 'loglevel': [self.parser.get, 'INFO'],
                 'googleCreds': [self.parser.get, os.path.join(self.configPath, 'GDrive-python_creds.json')]}
        
        
        # make sure a configuration path exists
        if len(self.parser.read(self.configFile)) <= 0:
            logging.warn('no configuration files found at: {}'.format(self.configFile))
            logging.debug('creating configuration files')
            try:
                os.makedirs(os.path.expanduser(self.configPath))
            except OSError as e:
                if e.errno != 17:
                    logging.critical(e)
                    sys.exit(1)
        
        # make sure there is a main section
        if not self.parser.has_section(self.mainSection):
            self.parser.add_section(self.mainSection)
        
        preferences = {}
        
        # read search for the expected preferences in the configuration file
        # note which are missing and set to the default values above
        for key in prefs:
            try:
                preferences[key] = prefs[key][0](self.mainSection, key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                self.parser.set(self.mainSection, key, prefs[key][1])
                preferences[key] = prefs[key][1]
        
        # init the proper attributes
        self.gdBaseFolder = preferences['gdBaseFolder']
        self.outputFolder = preferences['outputFolder']
        self.loglevel = preferences['loglevel']
        self.googleCreds = preferences['googleCreds']    
    
    
stdout_default = sys.stdout
root = Tk()
my_gui = myApp(root)
root.mainloop()
#cleanup any stdout redirects
sys.stdout = stdout_default
sys.stdout.flush()

