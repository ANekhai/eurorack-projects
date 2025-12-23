import FreeCAD as App
import Part


grid_u = 2.54 # mm

###############################################
### Draw functions for my VeeCAD footprints ###
###############################################

def drawVeecadRunner(data:dict[list]):
	footprints_obj = doc.addObject("Part::Feature", "Footprints")
	holes_obj = doc.addObject("Part::Feature", "Holes")
	
	for (name, vals) in data.items():
		# extract and transform formatted data
		outline = vals[0]
		# want to draw the panel holes vertically down, so we make y positions negative 
		# (mirroring veecad)
		position = App.Vector(vals[1]*grid_u, -vals[2]*grid_u, 0)
		rotation = vals[3]
		footprint, hole = drawComponent(outline, position, rotation)
		# draw objects
		if footprints_obj.Shape.isNull():
			footprints_obj.Shape = footprint
			holes_obj.Shape = hole
		else:
			footprints_obj.Shape = Part.makeCompound([footprints_obj.Shape, footprint])
			holes_obj.Shape = Part.makeCompound([holes_obj.Shape, hole])
		
		#fp_obj = doc.addObject("Part::Feature", f"{name}_outline")
		#hole_obj = doc.addObject("Part::Feature", f"{name}_hole")
		#fp_obj.Shape = fp
		#hole_obj.Shape = hole
		
		# fps_obj.Shape = fps_obj.Shape.fuse(fp)
		# holes_obj.Shape = holes_obj.Shape.fuse(hole.toShape())
	
	doc.recompute()


def drawComponent(footprint:str, position, rotation):
	if footprint == "THONK":
		return drawThonkJack(position, rotation)
	elif footprint == "POT6_5":
		return draw65Pot(position, rotation)
	elif footprint == "POT5_5":
		return draw55Pot(position, rotation) 


def drawFootprint(points, position, rotation, radius, offset):
	# position footprint outline
	footprint = Part.makePolygon(formatTuplePoints(points))
	axis = App.Vector(0, 0, 1)
	footprint.rotate(App.Vector(grid_u/2,-grid_u/2,0), axis, rotation)
	# position panel hole
	hole = Part.Circle(offset, axis, radius)
	hole = hole.toShape().rotate(App.Vector(grid_u/2,-grid_u/2,0), axis, rotation)
	
	#rot = App.Rotation(axis, rotation)
	#hole = Part.Circle(rot * offset, axis, radius)
	# translate
	footprint.translate(position)
	hole.translate(position)
	# draw objects
	#fp_obj = doc.addObject("Part::Feature", f"{label}_footprint")
	#h_obj = doc.addObject("Part::Feature", f"{label}_hole")
	#fp_obj.Shape = footprint
	#h_obj.Shape = hole.toShape()
	
	return footprint, hole


def drawThonkJack(origin:App.Vector, rotation:float):
	footprint_points = [ (0,0),(0,-3),(1,-3),(1, -4),
						(2,-4),(2,-3),(3,-3),(3,0),(0,0) ]
	hole_radius = 6.3/2
	hole_offset = App.Vector(1.5*grid_u, -4.92, 0)
	return drawFootprint(footprint_points, origin, rotation, hole_radius, hole_offset)

def draw65Pot(origin:App.Vector, rotation:float):
	footprint_points = [ (0,0),(0,-2),(1,-2),(1,-3),(0,-3),(0,-6),(5,-6),
						(5,-3),(4,-3),(4,-2),(5,-2),(5,0),(0,0) ]
	hole_radius = 6.3/2
	hole_offset = App.Vector(2.5*grid_u, -5*grid_u + 7, 0)
	return drawFootprint(footprint_points, origin, rotation, hole_radius, hole_offset)


def draw55Pot(origin:App.Vector, rotation:float):
	# Outline
	footprint_points = [ (1,0),(1,-1),(0,-1),(0,-2),(1,-2),(1,-5),(4,-5),
						(4,-2),(5,-2),(5,-1),(4,-1),(4,0),(1,0) ]
	hole_radius = 7.1/2
	hole_offset = App.Vector(2.5*grid_u, -4*grid_u + 7.5, 0)
	return drawFootprint(footprint_points, origin, rotation, hole_radius, hole_offset)


def formatTuplePoints(pts:list[tuple[int]]) -> list[App.Vector]:
	# Since panels are a 2d grid, I'd prefer to write points as tuples of grid points
	
	# convert 2d grid coordinates to mm
	pts = list(map(lambda v: (v[0]*grid_u, v[1]*grid_u), pts))
	# return these encapsulated in a vector
	return list(map(lambda v: App.Vector(v[0],v[1],0), pts))
	
	
if __name__ == "__main__":
	
	doc = App.newDocument("Panel")
	
	#import os
	#print(os.getcwd())
	
	path = "D:\\Users\\canof\\Desktop\\dev\\eurorack-projects\\stripboard-layouts\\panelizer-plugin\\rotation_test.per"
	create_panel(path)
	
	#doc = App.newDocument("Panel")
	#fp, h = draw55Pot(App.Vector(3*grid_u,-3*grid_u,0),270)

	doc.recompute()
	
	print("All Done!")

