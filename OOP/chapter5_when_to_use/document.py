
class Document(object):

	def __init__(self):
		self.characters = []
		self.cursor = Cursor(self)
		self.filename = ''

	def insert( self, character ):

		# checks if the character being passed in is a Character or 
		# a str, if it's a string when it is wrapped inside a Character class
		# so that all objects in the characters list are Character objects
		if not hasattr( character, 'character' ):
			character = Character(character)
		self.characters.insert( self.cursor.position, character )
		self.cursor.forward()

	def delete(self):
		del self.characters[self.cursor.position]

	def save(self):
		f = open( self.filename, 'w' )
		f.write( ''.join(self.characters) )
		f.close()

	@property
	def string(self):
		"""
		call the str() on each Character to use to __str__,
		if the method is not a verb, consider using @property 
		"""
		return ''.join( ( str(c) for c in self.characters ) )


class Cursor(object):
	"""separate the cursor to a separate class from the document"""
	def __init__( self, document ):
		self.document = document
		self.position = 0
	
	def forward(self):
		self.position += 1

	def back(self):
		self.position -= 1

	def home(self):
		"""note that home will crash for empty document"""
		while self.document.characters[self.position - 1].character != '\n':
			self.position -= 1
			if self.position == 0:
				break

	def end(self):
		while ( self.position < len(self.document.characters) and 
				self.document.characters[self.position].character != '\n' ):
			self.position += 1


class Character(object):
	"""
	text can have bold, underlined or italic characters
	to do this we'll add information to each character indicating
	what formatting it should have 
	"""

	def __init__( self, character, bold = False, italic = False, underline = False ):
		assert len(character) == 1
		self.character = character
		self.bold = bold
		self.italic = italic
		self.underline = underline

	def __str__(self):
		"""
		works with string manipulation functions such as print,
		it will convert class information into a string instead of printing
		out the default info like the module, class and memory address
		"""
		bold = '*' if self.bold else ''
		italic = '/' if self.italic else ''
		underline = '_' if self.underline else ''
		return bold + italic + underline + self.character



