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

## Opperation
Run fileStreamPortfolio_App any time new students need to be added to the portfolio folder. The program will **not** create duplicate folders. It is OK to use a student_export.text file that contains duplicate entries. The first time the program is run it will help the user locate the appropriate folder on a Team Drive and a student_export.text file. 

## Authors

* **Aaron Ciuffo (aaron.ciuffo@gmail.com)** - *Initial work* - [Txoof](https://github.com/txoof)

## License

