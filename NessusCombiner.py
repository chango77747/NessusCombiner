#!/usr/bin/python
# Evan Pena
# evan.pena@mandiant.com
# Mandiant 2012
#This method was found here: www.rykerexum.com/2012/03/12/how-to-merge-multiple-nessus-files-into-a-single-report/
#I am just automating it so it's easier/faster for people to do.
import getopt
import sys, os, fileinput
import shutil

def description():
	print '''\nNessus Combiner Utility
Will combine multiple .nessus files into one .nessus file.

Author: Evan Pena

Overview:
   This script will combine multiple .nessus files into one .nessus file.
   This will make it easier for consultants to view all the results in 
   one report within Nessus.
   It will also allow consultants to generate finding bloks from one .nessus 
   file instead of multiple.'''

def usage():
    scriptname = sys.argv[0]

    print '''
Usage:
    python %s args
 
Options:
    -h, --help          Will generate this help menu.
     
Examples:
    python %s [filename.nessus] [filename2.nessus] filename3.nessus]    
	
Support:
    evan.pena@mandiant.com    
    ''' % (scriptname, scriptname)

def reportNameReplacer():
	try:
		TAG = '<Report name='
		input = open('file1_temp.nessus')
		output = open('file1.nessus','w')
		for line in input.xreadlines(  ):
			if line.startswith(TAG):				
				output.write(line.replace(line, '<Report name="Concatenated Nessus Reports" xmlns:cm="http://www.nessus.org/cm">\n'))
			else: 
				output.write(line)		
		output.close(  )
		input.close(  )
		os.remove('file1_temp.nessus')
	except Exception, e:
			print e

def combiner( filenames):	
	try:
		TAG = '<Report name='
		newFiles = []
		#Modifies the first file to remove the "end of report tags"
		firstFile = str(filenames[:1])
		firstFile = firstFile.replace("[", "")
		firstFile = firstFile.replace("]", "")
		firstFile = firstFile.replace("'", "")
		
		readFile = open(firstFile)
		lines = readFile.readlines()
		readFile.close()
		w = open('file1_temp.nessus','w')
		w.writelines([item for item in lines[:-2]])
		w.close()
		reportNameReplacer()
		newFiles.append('file1.nessus')
		
		#This is for all the files in between. It will remove the line that starts with "<Report name=" and all the lines before it.
		#It will also remove the last two lines of the file
		#There is an error here when you add more than 3 files. Somethign to do with the for loops. Logic issue
		midFiles = filenames[1:-1]		
		for item in midFiles:						
			fileOutput = item.split('\\')
			fileOutput = fileOutput[len(fileOutput)-1]
			tag_found = False	
			with open(item) as in_file:
				with open(str(fileOutput)+'NEW.nessus', 'w') as out_file:						
					for line in in_file:
						if not tag_found:
							if line.startswith(TAG):
								tag_found = True
						else:
							out_file.write(line)				
			readFile = open(str(fileOutput)+'NEW.nessus')
			lines = readFile.readlines()
			readFile.close()
			w = open(str(fileOutput)+'NEW.nessus','w')
			w.writelines([item for item in lines[:-2]])
			w.close()
			newFiles.append(str(fileOutput)+'NEW.nessus')
				
		#Can also do this:
		#regex2 = '^<Report name=.*xmlns:cm=.*>$' # Variable @name & @xmlns:cm
		#with open(firstFile, "r") as fileInput:
			#listLines = fileInput.readlines()
		# listIndex = [i for i, item in enumerate(listLines) if re.search(regex2, item)]
		#with open("out_" + firstFile, "w") as fileOutput:
			#fileOutput.write("\n".join(lines[listIndex:]))
		
		#For the last file we only remove the line that starts with "<Report name=" and all the lines before it.
		#It will need to keep the end script tags
		tag_found1 = False
		lastFile = str(filenames[-1:])
		lastFile = lastFile.replace("[", "")
		lastFile = lastFile.replace("]", "")
		lastFile = lastFile.replace("'", "")		
		with open(lastFile) as in_file:
			with open('lastfile.nessus', 'w') as out_file:						
				for line in in_file:
					if not tag_found1:
						if line.startswith(TAG):
							tag_found1 = True
					else:
						out_file.write(line)
		newFiles.append('lastfile.nessus')
		
		#Now we must concatenate them all together.
		with open('concat_file.nessus', "w") as concat_file:
			for items in newFiles:
				shutil.copyfileobj(open(items, "r"), concat_file)
				#This will remove the files at the end.
				os.remove(items)
		
				
		print "\nSuccess! You have combined all your nessus files into 1 file." 
		print "Look for the concat_file.nessus in the current working directory."
	except Exception, e:
			print e	
def main():
	try:
		list1 = []
		try:
			opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
		except getopt.GetoptError, err:
			print str(err) #will print something like "option -a not recognized"
			print "Try + " + scriptname + " --help' for more information."
			sys.exit(2)
				
		# Parse command line options
		for o, a in opts:
			print o
			if o in ('-h', '--help'):
				description()
				usage()
				sys.exit()
			else:
				assert False, "invalid arguments"
		
		filenames = sys.argv[1:]
		
		for items in filenames:
			if not items.endswith('.nessus'):
				assert False, "\nThe filename must be a .nessus file."
		
		combiner(filenames)				

	except Exception, e:
			print e

if __name__ == '__main__':
    main()