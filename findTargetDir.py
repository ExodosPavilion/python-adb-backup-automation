from ppadb.client import Client as AdbClient
from pathlib import Path
from pick import pick
import os, shutil

MIN_NO_FOR_FILE_TRANSFER = 10 #the criteria used to determine if a folder should be transfered

#absolute path seemed to keep getting a permission denied error from ppadb when transfering hence the reason for the relative os path
LOCAL_BACKUP_PATH = os.path.join('Backup')

HD_BACKUP_PATH = os.path.join("F:/", "Backups", "Neko") #path to the backup location on the harddrive

PATH_TO_SDCARD_NEKO = '"/storage/8533-17ED/Neko/MangaDex (EN)"' #where neko manga is stored

#----------------------------- PATH METHODS -----------------------------
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


def genPreviousFolderPath(path):
	pathSplit = path.split('/') #split the path into by th forward slashes ('/')

	del pathSplit[ len(pathSplit) - 1 ] #delete the last item in the list we got from the split
	#generally the last item is the folder we were at, remove that and its the previous one

	prevPath = '/'.join( pathSplit ) #join the strings in the list with a forward slash ('/')

	return prevPath + '"' #return the path to the previous folder

#END
#----------------------------- PATH METHODS -----------------------------


#----------------------------- PICK SIMPLIFIED -----------------------------
#START

def optionSelector(title, options, multi=False, minimumSelection=1, outputOption=0):
	'''
        outputOptions:
                0: returns both the index / indexes and the selected option name(s)
                1: returns only the index / indexes
                2: returns only the selected option name(s)
	'''
	#Use the pick (curses) module to make the user select from preset set of options
	
	#Used when multi (multi-selection) is set to True
	selectedOptionNames = [] 
	selectedIndexes = []
	
	#Used when multi (multi-selection) is set to False
	selectedOption = None
	selectedIndex = None
	
	#if there are no problems with the data being passes in
	if type(title) != str or type(options) != list or type(multi) != bool or type(minimumSelection) != int or type(outputOption) != int:
		raise TypeError
	else:
		#ask the user to choose an option
		selected = pick(options, title, multiselect=multi, min_selection_count=minimumSelection)
		
		if multi:
			for i in selected:
				selectedOptionNames.append(i[0])
				selectedIndexes.append(i[1])
		else:
			selectedOption = selected[0]
			selectedIndex = selected[1]
		
		if outputOption == 1:
			if multi:
				return selectedIndexes
			else:
				return selectedIndex
		elif outputOption == 2:
			if multi:
				return selectedOptionNames
			else:
				return selectedOption
		else:
			if multi:
				return selectedOptionNames, selectedIndexes
			else:
				return selectedOption, selectedIndex

#END
#----------------------------- PICK SIMPLIFIED -----------------------------

#----------------------------- CONNECT TO DEVICE -----------------------------
#START
client = AdbClient(host='127.0.0.1', port=5037) #Create the adb deamon server

device = ( client.devices() )[0] #get the connected device

print('Connected to device')

#END
#----------------------------- CONNECT TO DEVICE -----------------------------

#----------------------------- GET FOLDERS AND LIST THEM TO GET PATH -----------------------------
#START

path = '""' #the starting path (Base)

foldersString = device.shell( 'ls -1' )
#get a list of all the items in the location in one line per item format

foldersList = foldersString.splitlines()
#split the string from the newline char

selectedFolder = optionSelector('Please select a folder', foldersList, outputOption=2) 
#use the pick module to make the user select only one folder

path = addToAndroidPath(path, selectedFolder) #add that folder to the path

#while we have not found the right directory
while True:
	foldersString = device.shell( f'{changeDirCommand(path)} && ls -1' ) #go to the selected folder
	
	foldersList = foldersString.splitlines()
	#split the string from the newline char
	
	foldersList.append( '\n' ) #formating option
	foldersList.append( 'At the desired folder' ) #if selected exit loop
	foldersList.append( 'Go back' ) #if selected go the previous folder

	selectedFolder = optionSelector('Please select a folder', foldersList, outputOption=2)
	#use the pick module to make the user select only one folder
	
	#if the user has found the desired folder
	if selectedFolder == 'At the desired folder':
		break #exit while loop
	
	#else if the user wants to go to the previous folder
	elif selectedFolder == 'Go back':
		#if the path is not the starting path (if not Base path)
		if path != '""':
			path = genPreviousFolderPath(path) #change path to the previous folder

	#else if the user has selected the formating option
	elif selectedFolder == '\n':
		pass #do nothing

	#else if the user has selected a folder
	else:
		path = addToAndroidPath(path, selectedFolder) #Add the folder to the path

print('\n' + path) #user is done print out the path that he needs

#END
#----------------------------- GET FOLDERS AND LIST THEM TO GET PATH -----------------------------

#print that the script has finished
print('\nDone')

