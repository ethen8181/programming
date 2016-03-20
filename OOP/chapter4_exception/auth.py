import hashlib


class Users(object):
	"""stores the User's username and encrypted password"""
	
	def __init__( self, username, password ):
		self.username = username
		self.password = self._encrypt_pw(password)
		self.is_logged_in = False

	def _encrypt_pw( self, password ):
		"""
		Encrypt the password with the username and return
		the sha digest.
		"""
		hash_string = ( self.username + password )
		# string needs to be encoded before hashed 
		hash_string = hash_string.encode("utf8")
		return hashlib.sha256(hash_string).hexdigest()
	
	def check_password( self, password ):
		"""
		Return True if the password is valid for this
		user, False otherwise
		"""
		encrypted = self._encrypt_pw(password)
		return encrypted == self.password


class Authenticator(object):
	"""User management, e.g. create new user, logging in and out"""
	
	def __init__(self):
		self.users = {}

	def add_user( self, username, password ):
		if username in self.users:
			raise UsernameAlreadyExists(username)
		if len(password) < 6:
			raise PasswordTooShort(username)
		
		self.users[username] = Users( username, password )

	def login( self, username, password ):
		try:
			user = self.users[username]
		except KeyError: # no such key in the dictionary
			# equivalent to : if username not in self.users:
			raise InvalidUsername(username)

		if not user.check_password(password):
			raise InvalidPassword( username, user )

		user.is_logged_in = True
		return True

	def is_logged_in( self, username ):
		"""
		Returns a boolean value indicating whether the 
		user is logged in or not
		"""
		if username in self.users:
			return self.users[username].is_logged_in
		return False


class AuthException(Exception):
	"""
	1. We don't want to add a user if that username already exists 
	   in the dictionary
	2. Exception if the password is too short
	"""
	def __init__( self, username, user = None ):
		super().__init__( username, user )
		self.username = username
		self.user = user


class UsernameAlreadyExists(AuthException):
	pass

class PasswordTooShort(AuthException):
	pass

class InvalidUsername(AuthException):
	pass

class InvalidPassword(AuthException):
	pass


class Authorizor(object):
	"""
	maps a permission dictionary to authenticated users
	each permission key will correspond to a set which stores
	the specific people that are allowed to perform each action
	"""
	
	def __init__( self, authenticator ):
		self.authenticator = authenticator
		self.permissions = {}

	def add_permission( self, perf_name ):
		"""Create a new permission that users can be added to"""

		try:
			perm_set = self.permissions[perf_name]
		except KeyError:
			self.permissions[perf_name] = set()
		else:
			raise PermissionError('Permission Exists')

	def permit_user( self, perm_name, username ):
		"""Grant the given permission to the user"""
		
		try:
			perm_set = self.permissions[perm_name]
		except KeyError:
			raise PermissionError('Permission does not exist')
		else:
			if username not in self.authenticator.users:
				raise InvalidUsername(username)
			perm_set.add(username)

	def check_permission( self, perm_name, username ):
		"""Checks whether a User has a specific permission or not"""
		
		if not self.authenticator.is_logged_in(username):
			raise NotLoggedInError(username)
		try:
			perm_set = self.permissions[perm_name]
		except KeyError:
			raise PermissionError('Permission does not exist')
		else:
			if username not in perm_set:
				raise NotPermittedError(username)
			else:
				return True	


class PermissionError(Exception):
	pass

class NotLoggedInError(AuthException):
	pass

class NotPermittedError(AuthException):
	pass


# add a default authenticator instance to our module so that 
# client code can access it easily using auth.authenticator
authenticator = Authenticator()
authorizor = Authorizor(authenticator)


