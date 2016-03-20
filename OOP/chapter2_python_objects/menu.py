import sys
from notebook import Note
from notebook import Notebook


class Menu(object):
	"""
	display a menu and respond to user choiced to interact 
	with the Note and Notebook when run
	"""

	def __init__(self):
		self.notebook = Notebook()
		self.choices = {
			'1': self.show_notes,
			'2': self.search_notes,
			'3': self.add_notes,
			'4': self.modify_notes,
			'5': self.quit
		}

	def display_menu(self):
		# use triple quotes for managing multiple lines of long printing
		print(
			"""
			Notebook Menu

			1.Show All Notes
			2.Search Notes
			3.Add Notes
			4.Modify Notes
			5.Quit
			"""
		)

	def run(self):
		"""display the menu and respond to choices"""

		while True:
			self.display_menu()
			choice = input('Enter an option: ')
			# .get() allows you to provide a value as the second parameter
			# and return that value if the key is missing, instead of 
			# throwing KeyError
			action = self.choices.get(choice)
			if action:
				action()
			else:
				print( '{0} is not a valid choice'.format(choice) )
	
	def show_notes( self, notes = None ):
		"""
		optional notes parameter. If it's supplied,
		it displays only the filtered notes, but if it's not, it displays all notes
		"""
		if not notes:
			notes = self.notebook.notes

		for note in notes:
			print( '{0}: {1}\n{2}'.format( note.id, note.tags, note.memo ) )

	def search_notes(self):
		filter_string = input('Search For: ')
		notes = self.notebook.search(filter_string)
		self.show_notes(notes)

	def add_note(self):
		memo = input('Enter a memo: ')
		self.notebook.new_note(memo)
		print('Your note has been added.')

	def modify_notes(self):
		id   = input('Enter a note id: ')
		memo = input('Enter a memo: ')
		tags = input('Enter tags: ')
		
		if memo:
			self.notebook.modify_memo( id, memo )
		if tags:
			self.notebook.modify_tags( id, tags )

	def quit(self):
		print('Thank you for using your notebook today.')
		# Exit the interpreter by raising SystemExit(status)
		sys.exit(0)

if __name__ == "__main__":
	Menu().run()




