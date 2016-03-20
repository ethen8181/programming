import os
import shutil
import zipfile

class ZipProcessor(object):
	"""
	Define a general ZipProcessor class to deal with zip files,
	the class is not meant to be runned directly. 
	"""
	def __init__( self, zipname ):
		self.zipname = zipname
		self.temp_directory = "unzipped-{}".format(zipname[:-4])

	def _full_filename( self, filename ):
		return os.path.join( self.temp_directory, filename )

	def process_zip(self):
		self.unzip_files()
		self.process_files() # define the process_files() in the subclass
		self.zip_files()
	
	def unzip_files(self):
		"""
		creates a temporary directory that stores all the unzipped files,
		will be destroyed after the process_files action is completed
		"""
		os.mkdir(self.temp_directory)
		zip = zipfile.ZipFile(self.zipname)
		try:
			zip.extractall(self.temp_directory)
		finally:
			zip.close()

	def zip_files(self):
		files = zipfile.ZipFile( self.zipname, 'w' )
		for filename in os.listdir(self.temp_directory):
			files.write( self._full_filename(filename), filename )
		shutil.rmtree(self.temp_directory)


class ZipReplace(ZipProcessor):
	
	def __init__( self, filename, search_string, replace_string ):
		super().__init__(filename)
		self.search_string  = search_string
		self.replace_string = replace_string

	def process_files(self):
		"""
		perform a search and replace on all files
		in the temporary directory
		"""
		for filename in os.listdir(self.temp_directory):
			if filename.lower().endswith('.txt'):
				with open( self._full_filename(filename) ) as f:
					contents = f.read()
				
				contents = contents.replace( self.search_string, self.replace_string )
				
				with open( self._full_filename(filename), 'w' ) as f:
					f.write(contents)




