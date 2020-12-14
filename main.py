from ppadb.client import Client as AdbClient
from pathlib import Path
import os, shutil

MIN_NO_FOR_FILE_TRANSFER = 10 #the criteria used to determine if a folder should be transfered

#absolute path seemed to keep getting a permission denied error from ppadb when transfering hence the reason for the relative os path
LOCAL_BACKUP_PATH = os.path.join('Backup')

HD_BACKUP_PATH = os.path.join("F:/", "Backups", "Neko") #path to the backup location on the harddrive

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

#----------------------------- CONNECT TO DEVICE -----------------------------
#START
client = AdbClient(host='127.0.0.1', port=5037) #Create the adb deamon server

device = ( client.devices() )[0] #get the connected device

print('Connected to device')

#END
#----------------------------- CONNECT TO DEVICE -----------------------------

#----------------------------- GET FOLDERS THAT MEET CRITERIA -----------------------------
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
#END
#----------------------------- GET FOLDERS THAT MEET CRITERIA -----------------------------

#----------------------------- PRINT FOLDERS THAT MEET CRITERIA -----------------------------
#START
print() #for formating of the prints

if transferList != []:
	print('Found folders that meet criteria:')
	
	for folder in transferList:
		print('\t' + folder)

print() #for formating of the prints
#END
#----------------------------- PRINT FOLDERS THAT MEET CRITERIA -----------------------------

#----------------------------- TRANSFER FOLDERS TO LOCAL BACKUP -----------------------------
#START

#for each folder that met the transfer criteria
for transferFolder in transferList:
    pathTotransferFolder = addToAndroidPath(PATH_TO_SDCARD_NEKO, transferFolder) #create a path to that folder to be used in ppadb operations
    
    insideTransferFolder = device.shell( '{} && ls -1'.format( changeDirCommand(pathTotransferFolder) ) ).splitlines() #get a list of all the folders within the transfer folder
    
	#for each folder within the transfer folder
    for folder in insideTransferFolder:
        imageFolder = addToAndroidPath(pathTotransferFolder, folder) #create a path to the folder to be used in ppadb operations

        images = device.shell( '{} && ls -1'.format( changeDirCommand( imageFolder ) ) ).splitlines() #get a list of the items within the folder

        folderPath = addToOSPath(LOCAL_BACKUP_PATH, transferFolder) #create a folder path in the backup location with the transfer folder name
        imgBackupPath = addToOSPath(folderPath, folder) #create a folder path in the backup transfer folder for the other folders found within the transfer folder
        Path( imgBackupPath ).mkdir(parents=True, exist_ok=True) #create the folders required

        imageFolder = imageFolder[1:] #remove the starting double quote (")
        imageFolder = imageFolder[:-1] #remove the ending double quote (")
        
		#for each file (image) found within the folder inside the transfer folder
        for image in images:
            pathToImage = imageFolder + '/' + image #create a unique path to it
            pathToImageBackup = addToOSPath(imgBackupPath, image) #create a path to its backup location
            device.pull( pathToImage, pathToImageBackup) #use ppadb to transfer from the phone to the backup location

    print('Moved to local: ' + transferFolder) #print that a transfer folder has finished being moved

#END
#----------------------------- TRANSFER FOLDERS TO LOCAL BACKUP -----------------------------

print() #for formating of the prints

#----------------------------- TRANSFER FOLDERS TO HARDDRIVE BACKUP -----------------------------
#START

folders = os.listdir(LOCAL_BACKUP_PATH) #list of all the folders in the local backup path

#for each folder in the local backup
for folder in folders:
	folderPath = addToOSPath(LOCAL_BACKUP_PATH, folder) #create a path to the folder in the local backup
	destFolderPath = addToOSPath(HD_BACKUP_PATH, folder) #create a path to the folder in the harddive backup
	innerFolders = os.listdir(folderPath) #list all the folders found within the folder

	#for each folder found
	for innerFolder in innerFolders:
		innerPath = addToOSPath(folderPath, innerFolder) #create a path to the folder in the local backup
		destInnerPath = addToOSPath(destFolderPath, innerFolder) #create a path to the folder in the harddrive backup
		Path( destInnerPath ).mkdir(parents=True, exist_ok=True) #make the directories in the harddrive backup path
		
		images = os.listdir(innerPath) #list all the images found in the inner folder
		
		for image in images:
			imagePath = addToOSPath(innerPath, image) #create a path to the file in the local backup
			destImagePath = addToOSPath(destInnerPath, image) #create a path to the file in the harddrive backup

			shutil.move(imagePath, destImagePath) #move the image from the local backup to the hardrive backup

	shutil.rmtree(folderPath) #delete the leftover folder of the transfered folder and all its contents
	print('Moved to harddrive: ' + folder) #print that it was moved

#END
#----------------------------- TRANSFER FOLDERS TO HARDDRIVE BACKUP -----------------------------

#print that the script has finished
print('\nDone')

