
# coding: utf-8

# In[158]:

import re


# In[159]:

class menu(object):
    '''Generate a simple menu of options'''
    
    def __init__(self, name = '', items=[]):
        self.name = name
        self.items = items
        self.size = len(self.items)
        
    def addItem(self, item):
        '''add a single item to the menu list'''
        if item in self.items:
            pass
        else:
            self.items.append(item)
            self.size = len(self.items)
            
    def removeItem(self, item):
        '''remove a single item from the menu list'''
        if item in self.items:
            self.items.remove(item)
            self.size = len(self.items)
        
    def sortMenu(self, reverse = False):
        '''
        sort the list alpha-numericaly
            args:
                reverse (bool): True = reverse sort
        '''
        self.items = sorted(self.items, reverse = reverse)
        
    def printMenu(self):
        '''print the menu items with numbers; 0+1 indexed'''
        for item in range (0, self.size):
            print '{0:2d}) {1}'.format(item+1, self.items[item])
            
    def returnChoice(self, choice):
        '''
        return a list item referenced by index
            args:
                choice (string)
                
            returns:
                list item or False'''
        try:
            self.lastChoice = int(re.search('(\d+)', choice).group(1))
            if self.lastChoice < 1:
                return(False)
        except Exception as e:
            self.lastChoice = False
            
        if 1 <= self.lastChoice <= self.size:
            try:
                return(self.items[self.lastChoice-1])
            except Exception as e:
                pass
        else:
            print 'invalid choice: {0}'.format(choice)
            return(False)
    
    def promptChoice(self, optional = False, optchoices = {'Q': 'Quit'}, message = False):
        '''
        prompt user to make a choice from a list decorated with title
            args:
                optional (bool): provide additional optional choices
                optchoices (dictionary): dictionary of optional choices {'Q': 'Quit', 'Y': 'Yes', 'M': 'Maybe'}
                message (string): optional message to include above menu
            returns:
                valid choice from menu or optional list or False'''
        if message:
            print message
        if self.name:
            print '='*5, self.name, '='*5
        self.printMenu()
        print 'Choose from the options listed'
        if optional:
            choice = raw_input('{0:2d} - {1:-1d} or {2}: '.format(1, self.size, optchoices))
        else:
            choice = raw_input('{0:2d} - {1:-1d}: '.format(1, self.size))
        if choice in optchoices:
            return(choice)
        else:
            return(self.returnChoice(choice))
        
        
    def loopChoice(self, optional = False, optchoices = {'Q': 'Quit'}, exit = 'Q', message = False):
        '''
        indefinitely prompt user to make a choice until a valid option is selected
            args:
                optional (bool): provide additional optional choices
                optchoices (dictionary): dictionary of optional choices {'Q': 'Quit', 'Y': 'Yes', 'M': 'Maybe'}
                message (string): optional message to include above menu
                exit (string): optional exit string to exit loop without making a valid choice
            returns:
                valid choice from menu or optional list or False'''
        choice = self.promptChoice(optional = optional, optchoices = optchoices, message = message)
        print ''
                
        while choice is False:
            choice = self.promptChoice(optional = optional, optchoices = optchoices, message = message)
        
        return(choice)
        
        
        
        


# In[163]:

# driveMenu = menu(name = "Team Drives", items = ["q", "tea", "a", "b", "dog", "ES Important Information"])
# driveMenu.addItem('spam')
# driveMenu.addItem('spam')
# driveMenu.removeItem('spam')
# driveMenu.sortMenu()
# foo = driveMenu.loopChoice(optchoices = {'Y': 'Yes', 'Q': 'Quit'}, optional = True, message = 'Choose a Team Drive from the list below')
# print 'your choice: ', foo
# if foo is 'Q':
#     print "I QUIT!"


