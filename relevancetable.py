class RelevanceTable:
	def __init__(self, input_length = 0.1):
		self.elements = []
		self.subtable_count = 0
		self.nontable_count = 0
		self.maxweight = 0
		self.connection_length = input_length

	def add(self, element):
		weight = 0

		if isinstance(element, RelevanceTable):
			self.subtable_count+=1
			weight = element.maxweight
		else: 
			self.nontable_count+=1
			weight = element[1]

		if weight>self.maxweight:
			self.maxweight = weight

		self.elements.append(element)

	def __str__(self):
		outstring =  ""

		for e in self.elements:
			if isinstance(e, RelevanceTable): outstring += ("{" + str(e) + "}")
			else: outstring += str(e)
		
		return outstring


	def generate_mapping_string(self, start_coords = [0,0]):
		betweenstr = "|"
		endstr = ";"

		outstring = ""
		coords = iter(self.generate_coordinate_list(start_coords))
		prev_coords = start_coords

		for element in self.elements:
			if isinstance(element, RelevanceTable):
				outstring+= element.generate_mapping_string(prev_coords)
			else:
				point_coords = next(coords)
				prev_coords = point_coords

				marker_text = element[0]
				color = self.color_picker(element[1])
				outstring += str(start_coords) + betweenstr + str(point_coords) + betweenstr + marker_text + betweenstr + color + endstr
		outstring = outstring.replace(" ", "")
		return outstring




	def generate_coordinate_list(self, start_coords = [0,0]):
		coordinate_list = []

		#if self.nontable_count == 1:
		#	return [0.0, self.connection_length]

		#taken from https://stackoverflow.com/questions/33510979/generator-of-evenly-spaced-points-in-a-circle-in-python
		import numpy as np
		#import matplotlib.pyplot as plt

		T = [self.nontable_count]
		R = [self.connection_length]

		def rtpairs(r, n):
		    for i in range(len(r)):
		       for j in range(n[i]):    
		        yield r[i], j*(2 * np.pi / n[i])

		for r, t in rtpairs(R, T):
		    coordinate_list.append([r * np.cos(t) + start_coords[0], r * np.sin(t) + start_coords[1]])
		#plt.show()
		#taken from https://stackoverflow.com/questions/33510979/generator-of-evenly-spaced-points-in-a-circle-in-python

		return coordinate_list


	def color_picker(self, weight):
	    switch = weight/self.maxweight
	    case = 1/7
	    color = ''
	    if switch < case: color = '#2e2e2e' #7
	    elif switch < case*2: color = '#4d4d4d' #6
	    elif switch < case*3: color = '#6b6b6b' #5
	    elif switch < case*4: color = '#7d7d7d' #4
	    elif switch < case*5: color = '#9e9e9e' #3
	    elif switch < case*6: color = '#c9c9c9' #2
	    else: color = '#fcfcfc' #1

	    return color
