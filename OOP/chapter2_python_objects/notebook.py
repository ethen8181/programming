import datetime

# Store the next available id for all new notes
last_id = 0

class Note(object):
	"""Represents a Note in the notebook"""

	def __init__( self, memo, tags = '' ):
		"""
		initialize a note with memo and a optional space-separated tags.
		the creation date and a unique id of the note will automatically be set 
		"""
		self.memo = memo
		self.tags = tags
		self.creation_date = datetime.date.today()
		global last_id
		last_id += 1
		self.id = last_id

	def match( self, filter_string ):
		"""
		Determine if the note matches the filter string,
		the filter string is case sensitive and it will
		try to match both text in the memo and tags.
		returns True if matched, False otherwise.
		"""
		return filter_string in self.memo or filter_string in self.tags


class Notebook(object):
	"""
	Represents a collection of Notes, whose tags, notes can be modified
	and can be searched
	"""

	def __init__(self):
		"""initialize a notebook with a list of empty notes"""
		self.notes = []

	def new_note( self, memo, tags = '' ):
		"""creates a new note and add it to the list"""
		self.notes.append( Note( memo, tags ) )

	def _find_note( self, note_id ):
		"""
		locate the note with the given id, 
		used for methods modify_note and modify_tags,
		the user input returns string type, convert to string before comparing
		"""
		for note in self.notes:
			if str(note.id) == str(note_id):
				return note
		return None

	def modify_memo( self, note_id, memo ):
		"""find the note with the given id and change its memo"""
		note = self._find_note(note_id)

		# only add the memo if the note id is not None,
		# None will happen when user input a invalid note id 
		if note:
			note.memo = memo
			return True
		return False

	def modify_tags( self, note_id, tags ):
		"""find the note with the given id and change its tags"""
		note = self._find_note(note_id)
		if note:
			note.tags = tags
			return True
		return False

	def search( self, filter_string ):
		"""find all notes that match the given filter string"""
		return [ note for note in self.notes if note.match(filter_string) ]





