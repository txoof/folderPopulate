
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


# In[ ]:

# This looks great!
# http://stackoverflow.com/questions/36604900/redirect-stdout-to-tkinter-text-widget

# also this:
# https://www.blog.pythonlibrary.org/2014/07/14/tkinter-redirecting-stdout-stderr/


# http://stackoverflow.com/questions/14883648/redirect-output-from-python-logger-to-tkinter-widget


# In[2]:

# http://stackoverflow.com/questions/36604900/redirect-stdout-to-tkinter-text-widget
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


# In[3]:

def getWorkingPath():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath("__file__"))
    
    return(bundle_dir)


# In[6]:

class myApp(object):
    def __init__(self, master):
        self.master = master
        master.title('Student Portfolio Populator')

        # get the configuration
        # Path to configuration files
        self.configPath = os.path.expanduser('~/.config/'+APP_SHORT_NAME)
        self.configFile = os.path.join(self.configPath, 'config.ini')
        
        # student CSV to import
        self.studentFile = None
        # student CSV to export
        self.studentData = None
        
        # folders to create for each student
        
        # consider setting this in the get config...
        self.gradeFolderFile = os.path.join(getWorkingPath(), 'gradefolders.txt')
        self.clientSecret = os.path.join(getWorkingPath(), 'client_secret_folderPopulate.json')
        
        # read in the configuration file
        self.getConfig()
        
        self.outputFile = datetime.now().strftime('Student_Data_Output_%Y%m%d-%H.%M.csv')
        
        self.msgReqURL = 'Paste Google Drive URL for Student Portfolio below:'
        self.msgOKURL = 'Student Portfolio URL accepted:'
        self.msgBadURL = 'Invalid URL format, please try again'
        self.message = self.msgReqURL        
        
        # launch the GUI interface
        self.guiInit()
        # configure the logging (needs to be after the gui init to handle the redirect of stdout)
        #self.configLogging()
        
        logging.debug('starting up...')
        logging.debug('current attributes:')
        displayAttr = ['gradeFolderFile',
                       'clientSecret',
                       'studentFile',
                       'studentData']
        
        for each in displayAttr:
            logging.debug('{:>5}{}: {}'.format('',each, eval('self.'+each)))
        
        
    def launchWindow(self):
        self.redirector('')
        self.configLogging()

        
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
        #self.rootLogger.setLevel(logging.DEBUG)
        #rootLogger.setLevel(logging.WARNING)
        #rootLogger.setLevel(logging.INFO)

    def guiInit(self):
        # initiate the output window 
        self.launchWindow()
#         self.redirector('Student Import Messages:\n')

        # set window size
        self.master.geometry('950x300+30+30')

        self.labelURL_text = StringVar()
        self.labelURL_text.set(self.message)
        self.labelURL = Label(self.master, textvariable = self.labelURL_text, font = "TkDefaultFont 0 bold")

        self.labelStuFileRow_text = StringVar()
        self.labelStuFileRow_text.set('PowerSchool student information (student_export.text): ')
        self.labelStuFileRow = Label(self.master, textvariable = self.labelStuFileRow_text, 
                                     font = "TkDefaultFont 0 bold")

        self.labelStuFile_text = StringVar()
        self.labelStuFile_text.set('None selected')
        self.labelStuFile = Label(self.master, textvariable = self.labelStuFile_text)

        self.labelOutpathRow_text = StringVar()
        self.labelOutpathRow_text.set('Location to Output Portfolio URLs:')
        self.labelOutpathRow = Label(self.master, textvariable = self.labelOutpathRow_text,
                                 font = "TkDefaultFont 0 bold")
        
        self.labelOutFolder_text = StringVar()
        self.labelOutFolder_text.set(self.outputFolder)
        self.labelOutFolder = Label(self.master, textvariable = self.labelOutFolder_text)
        
        self.submit_button = Button(self.master, text = 'BEGIN FOLDER CREATION', command = self.submit, highlightbackground = '#2EFF00')
        self.quit_button = Button(self.master, text = 'Quit', command = self.quit, highlightbackground='#FF2D00')
        self.buttonStFile = Button(self.master, text = 'Set Student Information File', command = self.studentFilePicker)
        self.buttonOutFolder = Button(self.master, text = 'Set Output Folder', command = self.outputFolderPicker)
        
        
        self.entryURL = Entry(self.master, width = 60, validate='key') #, validatecommand=(vcmd, '%P'))
        self.entryURL.insert(END, self.gdBaseFolder)

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

        
        ############ organize the grid
        
        self.labelURL.grid(row = 0, columnspan = 2, sticky=W)        
       
        self.entryURL.grid(row = 2, column = 0, columnspan = 2, sticky = W)
        
        self.labelStuFileRow.grid(row = 4, column =1, sticky = E)
        self.labelStuFile.grid(row = 4, column = 2, sticky = W)        
        self.buttonStFile.grid(row = 4, column = 0, sticky = W)
        
        self.labelOutpathRow.grid(row = 5, column = 1, sticky = W)
        self.labelOutFolder.grid(row = 5, column = 2, sticky = W)
        self.buttonOutFolder.grid(row = 5, column = 0, sticky = W+E)
        
        
        
        
        self.submit_button.grid(row = 8, column = 0, sticky = W+E)
        
        self.quit_button.grid(row = 9, column = 0, sticky = W)  
        
    def setLogLevel(self, level):
        self.loglevel = level
        self.rootLogger.setLevel(getattr(logging, level))
        pass
    
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
        prefs = {'gdBaseFolder': [self.parser.get, 'https://drive.google.com/SAMPLE/URL/abc123zyx987'],
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
        
        self.preferences = {}
        
        # read search for the expected preferences in the configuration file
        # note which are missing and set to the default values above
        for key in prefs:
            try:
                self.preferences[key] = prefs[key][0](self.mainSection, key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                self.parser.set(self.mainSection, key, prefs[key][1])
                self.preferences[key] = prefs[key][1]
        
        # init the proper attributes
        self.gdBaseFolder = self.preferences['gdBaseFolder']
        self.outputFolder = self.preferences['outputFolder']
        self.loglevel = self.preferences['loglevel']
        self.googleCreds = self.preferences['googleCreds']
        
        
    def outputFolderPicker(self):
        try:
            folder = tkFileDialog.askdirectory(title = 'Choose output folder')

        except (IOError, OSError) as e:
            print e
            return(False)
        if len(folder) > 0:
            self.outputFolder = folder
            self.labelOutFolder_text.set(self.outputFolder)        
    
    def studentFilePicker(self):
        try:
            stuFile = tkFileDialog.askopenfile(mode='r', title='Choose exported student data')
        except (IOError, OSError) as e:
            print e
            return(False)
        
        if stuFile.name:
            self.studentFile = stuFile
            self.labelStuFile_text.set(self.studentFile.name)
        
        
#         try:
#             self.studentData = self.studentFile.read()
#             self.labelStuFile_text.set(self.studentFile.name)
#             print self.studentData
#         except AttributeError as e:
#             logging.error('failed to read file please try again')
#             logging.error('error: {}'.format(e))
        
        return(True)

    
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
        
    def submit(self):
        if self.studentFile is None:
            logging.error('No Student Information file selected. Please select a file.')
            return(False)
        logging.info('Starting work. This could take several minutes (you will see a beachball spinning...)')
        # check for a valid URL format
        urlRegex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # spawn a text window for output
        logging.debug('checking validity of entered URL')
        if re.match(urlRegex, self.entryURL.get()): 
            self.gdBaseFolder = self.entryURL.get()
            
            self.message = self.msgOKURL
        else: 
            self.gdBaseFolder = ''
            self.message = self.msgBadURL        
        
        self.labelURL_text.set(self.message)
        
        self.parser.set(self.mainSection, 'gdBaseFolder', self.gdBaseFolder)
        self.parser.set(self.mainSection, 'outputFolder', self.outputFolder)   
        
        # write configuration file
        logging.debug('writing configuration to file: {}'.format(self.configFile))
        try:
            self.parser.write(open(self.configFile, 'w'))
        except Exception as e:
            logging.error('Error writing configuration file: {}'.format(e))
        
        
        # kick off actual task 
        # gDrivePopulate(base folder url, path to credentials etc.)
#         foo = gDrivePopulate(gdBaseFolderURL = 'https://drive.google.com/drive/folders/0B9WTleJ1MzaYcmdmTWNNNF9pa1E',
#                     gradeFoldersFile = './gradefolders.txt', 
#                     client_secret = '~/.config/populate/populate-credentials.json', 
#                     studentInfo = 'student_export.text')
        logging.debug('student file: {}'.format(self.studentFile))
        gDriveResult = gDrivePopulate(gdBaseFolderURL = self.gdBaseFolder, 
                                      #gradeFoldersFile = './gradefolders.txt',
                                      gradeFoldersFile = self.gradeFolderFile,
                                      client_secret = self.clientSecret,
                                      studentInfo = self.studentFile.name,
                                      outputPath = self.outputFolder)
            
        
    
        
    def quit(self):
        self.master.destroy()

# reserve the pointer to sys.stdout to restore
stdout_default = sys.stdout
root = Tk()
my_gui = myApp(root)
root.mainloop()
# reset sys.stdout when done - useful when running in an IDE
sys.stdout = stdout_default
sys.stdout.flush()

