
# finding weather extremes 

# task: finding the min and max weather for this weather station 
# 		through out this year 

# data format: comma separated data
# variables used with this task  
# 1. identifier of the weather station
# 2. date, in y-m-d format
# 3. field indicating what the row represents, this includes TMAX that indicates
#	 the max temperature and TMIN that indicates the minimum temperature (for each day)
# 4. temperature, recorded in tenth of a celsius degree e.g. 75 = 7.5 celsius 

from mrjob.job import MRJob 


class MRMinTemperature(MRJob) :

	# convert tenth of celsius of fahrenheit
	def makeFahrenheit( self, tenth_of_celsius ) :
		
		celsius = float(tenth_of_celsius) / 10.0
		fahrenheit = celsius * 1.8 + 32
		return fahrenheit

	# we don't care about x, y, z, w, they are simply read in
	def mapper( self, key, line ) :
		
		( location, date, types, data, x, y, z, w ) = line.split(",")

		# switch the if to TMAX for maximum temperature 
		# if types == "TMIN" :
		if types == "TMAX" :
			temperature = self.makeFahrenheit(data)
			yield location, temperature

	# note that the key value pair's name can be different with what the mapper yield 
	def reducer( self, location, temperature ) :

		# yield location, min(temperature)
		yield location, max(temperature)

# python temperature.py 1800.csv > mintemp.txt
if __name__ == "__main__" :
    MRMinTemperature.run()






