# fileStreamFolderPopulate

Works only on OS X with a Google Team Drive mounted using the TD FUSE Application
fileStreamPopulate uses a FUSE mounted Team Drive via Google FileStream on OS X to create portfolio folders for students. 
A folder for each student is created in the hiarchy shown below. The folders are created based on a CSV that contains student projected graduation year; LastName, FirstName; Student Number.

#### CSV Format
```
ClassOf,LastFirst,Student_Number
"2005","Dean, James","123456"
"2006","Washington, George","654321
```

#### Folder Hiarchy
```
Class Of-XXXX______ (XXXX - Projected graduation year)
                  |
                  LastName, FirstName - YYYYYY______ (YYYYYY - Student number)
                                                    |
                                                    00-Preschool
                                                    00-Transition Kindergarten
                                                    00-zKingergarten
                                                    01-Grade
                                                    02-Grade
                                                    ...
                                                    12-Grade
```
                                                    

## Prerequisites

Google FileStream: https://dl.google.com/drive-file-stream/GoogleDriveFileStream.dmg
Python 2.7 (installed by default on OS X)

## Installing

### Configure Google Filestream
* Download and Install Google FileStream application - An administrator password is required 
* Locate the Team Drive where student portfolios will be kept
* If it does not exist, create a folder on the Team Drive that will contain student Portfolios
* Open Google FileStream and sign in with a user that can acess the Team Drive specified above

### Setup fileStreamPortfolio_App
* Download fileStreamPortfolio https://github.com/txoof/folderPopulate/blob/master/fileStream/fileStream.tgz
* Double Click fileStream.tgz to unzip
* Move fileStreamPortfolio_App folder to Documents or Application folder

### Test & Demo
* Open the fileStreamPortfolio_App folder and copy ```student_export_demo.text``` to the Downloads folder
* Double click on fileStreamPortfolio.command to launch the program
* Follow the prompts to run the demo
* **The program is menu driven and asks the user to use numeric or text choices to answer questions for the configuration and opperation
```
Welcome to the portfolio creator for Google Team Drive version 18.05.09-2104
This program will create portfolio folders in Google Team Drive for students.
You will need a student_export.text file from PowerSchool with at least the following information:
     ClassOf, FirstLast, Student_Number

The order of the CSV does not matter, but the headers must be on the very first line.
You will also need Google File Stream installed and configured
File Stream can be downloaded here: https://support.google.com/drive/answer/7329379?hl=en
Press Enter to continue..
```

**Choose the appropriate Team Drive**
```
Which Team Drive contains the portfolio folder?
===== Team Drives =====
 1) ASH GDPR 
 2) ASH Medical Care Plans
 3) ASH Medical Information
 4) ASH PowerSchool Learning Resources
 5) ASH Transportation
 6) ES Portfolios
 7) IT Support Internal
 8) ITM-ITCC Internal
 9) PS12 IT Team
Choose from the options listed
 1 - 9 or {'Q': 'Quit'}: 6
```
**Type a portion of the folder name that contains the portfolios**
```
Searching in Team Drive: ES Portfolios
Please enter part of the portfolio folder name (case sensitive search): Student
```

**Choose the appropriate folder from the list**
```
Which folder contains portfolios?
===== Matching Folders =====
 1) /Volumes/GoogleDrive/Team Drives/ES Portfolios/Student Historical Information
 2) /Volumes/GoogleDrive/Team Drives/ES Portfolios/Student Information
 3) /Volumes/GoogleDrive/Team Drives/ES Portfolios/Student List
 4) /Volumes/GoogleDrive/Team Drives/ES Portfolios/Student Portfolios
Choose from the options listed
 1 - 4 or {'Q': 'Quit', 'T': 'Try search with different folder name'}: 4
```

**Choose the location of the the student_export.text file**
The program will only check the Desktop, the Documents folder and the Downloads folders. Please make sure your student_export.text file is in one of those three locations. The program will **only** search for files that end in .text
```
Please specify the location of the student_export.text file
===== student_export file location =====
 1) Desktop
 2) Documents
 3) Downloads
Choose from the options listed
 1 - 3 or {'Q': 'Quit'}: 3
 ```
 
 **Choose the proper student_export.text file**
 ```
 Please choose the student_export text file to use
===== student export files =====
 1) Grade 1.text
 2) Grade 2.text
 3) Grade 3.text
Choose from the options listed
 1 - 3 or {'Q': 'Quit'}: 1
 ```
**Check that the proper folder has been selected and choose 'Yes' to continue or 'No' to try again**
```
Continue with the portfolio folder: /Volumes/GoogleDrive/Team Drives/IT Blabla/c/b/a/Portfolios
===== Continue? =====
 1) Yes
 2) No: Set new team drive and folder
Choose from the options listed
 1 - 2 or {'Q': 'Quit'}: 1
```

**Check the output**
```
Completed creating portfolio folders.
successfully created 4 of 4 student directories
skipped (these already existed): 0
errors: 0
```

## Opperation
Run fileStreamPortfolio_App any time new students need to be added to the portfolio folder. The program will **not** create duplicate folders. It is OK to use a student_export.text file that contains duplicate entries. The first time the program is run it will help the user locate the appropriate folder on a Team Drive and a student_export.text file. 

If folders already exist, no action will be taken and a count of the skipped folders will be shown:
```
Completed creating portfolio folders.
successfully created 0 of 4 student directories
skipped (these already existed): 4
errors: 0
```

### Common Problems
* **Problem:** Google File Stream is not Installed
* **Solution:** Download and install google filestream 
```
Unable to find application named 'Google Drive File Stream'
CRITICAL: Google Drive File Stream does not appear to be installed. Please download from the link below
CRITICAL: https://support.google.com/drive/answer/7329379?hl=en
CRITICAL: exiting
```

* **Problem:** student_export.text file is not formatted properly
* **Solution:** Ensure that the student_export.text file is properly formatted (see example above)
```
CRITICAL: no records found in file: /Users/aciuffo/Downloads/student_export.text.
CRITICAL: please check that the above file is a comma sepparated values file (CSV)
CRITICAL: error reading student file. exiting
```


## Authors

* **Aaron Ciuffo (aaron.ciuffo@gmail.com)** - *Initial work* - [Txoof](https://github.com/txoof)

## License

