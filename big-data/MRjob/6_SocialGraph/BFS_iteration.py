
# breadth first search
# start from the nodes that are gray 
# and expand from it to the white node
# nodes that have been explored are colored black 

# since we've don't know how many steps we need 
# thus we can't use step to run it  

from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol

class Node :

	# define the variables inside to be owned by that instance 
	def __init__(self) :
		
		self.characterID = ""
		self.connections = []
		self.distance 	 = 99999
		self.color 		 = "white"

	# obtain a line of the input file and convert it to a node class
	# line's format : ID | Edges | Distance | Color
	def fromLine( self, line ) :

		fields = line.split("|")

		# confirming that it has 4 pip-delimited fields
		if( len(fields) == 4 ) :

			self.characterID = fields[0]
			self.connections = fields[1].split(",")
			self.distance 	 = int(fields[2])
			self.color 		 = fields[3]

	# convert the node back to the original line 
	def getLine(self):

		connections = ",".join( self.connections )

		return "|".join( ( self.characterID, connections, str(self.distance), self.color ) )


class MRBFSIteration(MRJob) :

	# setting protocol to raw value protocol
	# the input and the output will be un-touched
	# e.g. wrapping quotes around strings 
	# that way we can use the output and feed it to the next input
	# without having to undergo another preprocessing 
	INPUT_PROTOCOL  = RawValueProtocol
	OUTPUT_PROTOCOL = RawValueProtocol


	# add the target variable that we want to identify
	# @add_passthrough_option is used when we want to pass a parameter
	# to every cluster 
	def configure_options(self) :

		super( MRBFSIteration, self ).configure_options()
		self.add_passthrough_option( "--target", help = "character id we're searching for" )


	def mapper( self, key, line ) :

		node = Node()
		node.fromLine(line)

		# if the node is gray meaning that it needs to be expanded
		# loop through its connections  
		if node.color == "gray" :

			for connection in node.connections :

				vnode = Node()
				vnode.characterID = connection
				vnode.distance = int(node.distance) + 1
				vnode.color = "gray"

				# self.options matches with the add_passthrough_option
				# in this case .target 
				# thus it stores the value that you've passed from the command line  
				if self.options.target == connection :

					counter_name = ( "target id" + connection + 
									 "was hit with distance" + str(vnode.distance) )

					self.increment_counter( "degree of separation", counter_name, 1 )

					yield connection, vnode.getLine()

			# we've processed this node; color it black 
			node.color = "black"

		yield node.characterID, node.getLine()


	def reducer( self, key, values ) :

		edges = []
		distance = 9999
		color = "white"

		for value in values : 

			node = Node()
			node.fromLine(value)

			# extend to the list instead of append
			# extend will split the list's element separately 
			# instead of directly appending the whole list as one element 
			if len(node.connections) > 0 :
				edges.extend(node.connections)
			
			if node.distance < distance :
				distance = node.distance 

			if node.color == "black" :
				color = "black"

			if node.color == "gray" and color == "white" :
				color = "gray"

		node = Node()
		node.characterID = key
		node.distance = distance
		node.color = color
		node.connections = edges

		yield key, node.getLine()



# pipe the result to a new text file 

# python BFS_iteration.py --target=100 bfs-iteration-0.txt > bfs-iteration-1.txt
# python BFS_iteration.py --target=100 bfs-iteration-1.txt > bfs-iteration-2.txt
if __name__ == "__main__" :
	MRBFSIteration.run()



