from ppadb.client import Client as AdbClient
from pathlib import Path
import os, shutil

MIN_NO_FOR_FILE_TRANSFER = 10 #the criteria used to determine if a folder should be transfered

#absolute path seemed to keep getting a permission denied error from ppadb when transfering hence the reason for the relative os path
BACKUP_PATH = os.path.join('Backup') 

PATH_TO_SDCARD_NEKO = '"/storage/8533-17ED/Neko/MangaDex (EN)"' #where neko manga is stored

#----------------------------- METHODS -----------------------------
#START

def changeDirCommand(path):
	'''
	Create a string that can be used to tell the adb shell that we want to move the "path" directory

	parameters:
		path = the path we need to go to

	returns:
		the change directory command with the path given
	'''
    return 'cd {}'.format(path) #command to change the directory to the specified one


def addToAndroidPath(path, folderToAdd):
	'''
	Create a string that can be used in the ppadb module operations (mainly the shell commands)

	parameters:
		path = the path we need to concanate the new folder to
		folderToAdd = the new folder we need to concanate to the path

	returns:
		a path to the specified folder
	'''
    return path[:-1] + '/' + folderToAdd + '"'


def addToOSPath(path, folderToAdd):
	'''
	Create a string that can be used in os module operations

	parameters:
		path = the path we need to concanate the new folder to
		folderToAdd = the new folder we need to concanate to the path

	returns:
		a path to the specified folder
	'''
    return os.path.join(path, folderToAdd)

#END
#----------------------------- METHODS -----------------------------

client = AdbClient(host='127.0.0.1', port=5037) #Create the adb deamon server

device = ( client.devices() )[0] #get the connected device

foldersString = device.shell( '{} && ls -1'.format( changeDirCommand(PATH_TO_SDCARD_NEKO) ))
#get a list of all the items in the location in one line per item format

foldersList = foldersString.splitlines()
#split the string from the newline char

transferList = [] #list of folders that pass the criteria to transfer

#for all the folders in the found folders
for folder in foldersList:
    data = [folder]
    
    inFolderString = device.shell('{} && ls -1'.format( changeDirCommand( PATH_TO_SDCARD_NEKO + '/"' + folder + '"' ) ))
    #get a list of all the items in the location in one line per item format

    inFolderList = inFolderString.splitlines()

    data.append( len(inFolderList) )

    #if the number of folders in the dir is greater than or equal to the transfer criteria
    if data[1] >= MIN_NO_FOR_FILE_TRANSFER:
        transferList.append(folder) #add the folder to transfer


#for each folder that met the transfer criteria
for transferFolder in transferList:
    pathTotransferFolder = addToAndroidPath(PATH_TO_SDCARD_NEKO, transferFolder) #create a path to that folder to be used in ppadb operations
    
    insideTransferFolder = device.shell( '{} && ls -1'.format( changeDirCommand(pathTotransferFolder) ) ).splitlines() #get a list of all the folders within the transfer folder
    
	#for each folder within the transfer folder
    for folder in insideTransferFolder:
        imageFolder = addToAndroidPath(pathTotransferFolder, folder) #create a path to the folder to be used in ppadb operations

        images = device.shell( '{} && ls -1'.format( changeDirCommand( imageFolder ) ) ).splitlines() #get a list of the items within the folder

        folderPath = addToOSPath(BACKUP_PATH, transferFolder) #create a folder path in the backup location with the transfer folder name
        imgBackupPath = addToOSPath(folderPath, folder) #create a folder path in the backup transfer folder for the other folders found within the transfer folder
        Path( imgBackupPath ).mkdir(parents=True, exist_ok=True) #create the folders required

        imageFolder = imageFolder[1:] #remove the starting double quote (")
        imageFolder = imageFolder[:-1] #remove the ending double quote (")
        
		#for each file (image) found within the folder inside the transfer folder
        for image in images:
            pathToImage = imageFolder + '/' + image #create a unique path to it
            pathToImageBackup = addToOSPath(imgBackupPath, image) #create a path to its backup location
            device.pull( pathToImage, pathToImageBackup) #use ppadb to transfer from the phone to the backup location

    print('Done ' + transferFolder) #print that a transfer folder has finished being moved



source = os.path.join("Backup")
destination = os.path.join("F:/", "Backups", "Neko")

#for zip file in the source directory
for zFile in os.listdir(source):
    #with the zipfile module open the zipfile( (join the source path with the zipfile name to get zipfile path) in read only mode ) as zip_reference
    with zipfile.ZipFile( os.path.join(source, zFile), 'r') as zip_ref:
	#extract the zipfile contents to the destiantion folder
        zip_ref.extractall(destination)
    #print that the script extracted the particular zip file
    print('Extracxted ' + zFile[:-4])

#print that the script is finished
print('\nDone')

