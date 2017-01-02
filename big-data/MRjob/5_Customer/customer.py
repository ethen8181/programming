
# task: how much money each customer spent in total,
# and order them in increasing order   

# data format:
# customer id, item id, how much money they spent 
# on their item 


from mrjob.job import MRJob
from mrjob.step import MRStep

class CustomerTotalSpent(MRJob) :

	def steps(self) : 

		return[

			MRStep( mapper  = self.mapperGetAmounts,
					reducer = self.reducerTotalAmounts ),

			MRStep( mapper  = self.mapperGetTotalAmounts,
					reducer = self.reducerOutputTotal )
		]

	def mapperGetAmounts( self, key, line ) :

		( customer, item, amounts ) = line.split(",")
		yield customer, float(amounts)

	def reducerTotalAmounts( self, customer, amounts ) :

		yield customer, sum(amounts)

	def mapperGetTotalAmounts( self, customer, total ) :

		yield "%04.02f" % total, customer

	def reducerOutputTotal( self, total, customers ) :

		for customer in customers :
			yield customer, total

# python customer.py customer-orders.csv > customer.txt
if __name__ == "__main__" :
    CustomerTotalSpent.run() 







