

# making breadth first search a map reduce problem 
# all the original nodes start out with distance infinite
# and for the nodes that we've already come across
# convert the color from "white" to "gray" 


import sys

# sys.argv is a list of strings representing the arguments
# on the command line, index [0] is the python script
# hence, we'll call our python script with a hero id
# python BFS.py 2548 ( The Hulk ), refer to the marvelnames.txt for names

print "Creating BFS starting input for character " + sys.argv[1]


with open( "bfs-iteration-0.txt", "w" ) as out :

	with open("marvelgraph.txt") as f :
		
		for line in f :
			
			fields  = line.split()
			hero_id = fields[0]
			num_connections = len(fields) - 1

			# store all the other id in a list
			# - starts counting from the back 
			connections = fields[ -num_connections: ]

			# all the nodes that have not yet been seen
			# are initialized with "white" and distance of 99999
			color = "white"
			distance = 99999

			# if the hero id is the one that we're querying 
			if hero_id == sys.argv[1] :
				
				color = "gray"
				distance = 0

			# join the tail of the adjacency list by ","
			# and join the hero id, edges, distance and color by "|"
			if hero_id != "" :
				
				edges  = ",".join(connections)
				string = "|".join( ( hero_id, edges, str(distance), color ) )
				out.write(string)
				out.write("\n")

	f.close()
out.close()









