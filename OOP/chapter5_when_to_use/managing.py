import sys
import os
import shutil
import zipfile
# some examples using zipfile
# http://effbot.org/librarybook/zipfile.htm

# entensibility :
# if a subclass wants to compressed other types of files
# we could override the zip and unzip method without having to duplicate
# the find_replace method

class ZipReplace(object):
	"""
	unzip a zip file, find and replace the specified string,
	and convert it back to zip file, this class only searches the top-level
	files in a zip file
	"""
	def __init__( self, foldername, search_string, replace_string ):
		"""creates a temporary directory to store the unzipped files in"""
		self.foldername = foldername
		self.search_string  = search_string
		self.replace_string = replace_string
		self.temp_directory = 'unzipped-{}'.format(foldername)

	def _full_filename( self, filename ):
		return os.path.join( self.temp_directory, filename )

	def zip_find_replace(self):
		self.unzip_files()
		self.find_replace()
		self.zip_files()

	def unzip_files(self):
		"""create the directory and extract all the content to the directory"""

		os.mkdir(self.temp_directory)
		zipped = zipfile.ZipFile(self.foldername)
		try:
			zipped.extractall( path = self.temp_directory )
		finally:
			zipped.close()

	def find_replace(self):
		# os.listdir list out the names of the entries in the directory
		# given the filepath
		
		for filename in os.listdir(self.temp_directory):
			# check for multiple file type
			# m.lower().endswith(('.png', '.jpg', '.jpeg'))
			if filename.lower().endswith('.txt'):

				with open( self._full_filename(filename) ) as f:
					# .read() reads in all the context, while .readline()
					# reads each line
					contents = f.read()

				contents = contents.replace( self.search_string, self.replace_string )

				with open( self._full_filename(filename), 'w' ) as f:
					f.write(contents)

	def zip_files(self):
		files = zipfile.ZipFile( self.foldername, 'w' )
		for filename in os.listdir(self.temp_directory):
			files.write( self._full_filename(filename), filename )
		# removes the temporary created directory 
		shutil.rmtree(self.temp_directory)

"""
if __name__ == "__main__":
	ZipReplace(*sys.argv[1:4]).zip_find_replace()

python zipsearch.py hello.zip hello hi
"""
