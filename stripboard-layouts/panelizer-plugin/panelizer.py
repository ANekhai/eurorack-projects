import os, sys
import json

# # allow importing local python files
# cwd = os.path.dirname(__file__)
# if cwd not in sys.path: sys.path.append(cwd)

import FreeCAD as App
import Part
import FreeCADGui as Gui
from PySide2 import QtCore, QtWidgets

cwd = os.path.dirname(__file__)
ui_path = os.path.join(cwd, "ui", "form.ui")


###########################################################
################ PANELIZER MACRO UI #######################
###########################################################

class PanelizerTaskPanel:
    def __init__(self):
        # load Qt Designer ui file
        self.form = Gui.PySideUic.loadUi(ui_path)

        # file browser click overwrites
        self.form.pushButton.clicked.connect(self.open_file_browser)


    def open_file_browser(self):
        # Open standard Qt file browser to pick VeeCAD file
        file_info = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select File", "", "All Files (*.*)"
        )
        # read veecad per file
        user_path = file_info[0]
        # update text box in UI if user chose a path
        if user_path: self.form.FilePath.setText(user_path)


    def accept(self):
        name = self.form.Name.text()
        file_path = self.form.FilePath.text()

        # basic validation
        if not os.path.isfile(file_path):
            print("Must provide a valid file")
            return
        elif not name:
            name = "Panel"

        # draw the panel
        print("I'll make the panel now!")
        drawer = VeeCADHandler(file_path, panel_name=name)
        drawer.drawPanel()
		
        # close dialog window
        Gui.Control.closeDialog()


###########################################################
################ VEECAD DRAW UTILITIES ####################
###########################################################

grid_u = 2.54 # mm

# Draw functions for custom footprints

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


def drawComponent(footprint:str, position, rotation):
	if footprint == "THONK":
		return drawThonkJack(position, rotation)
	elif footprint == "POT6_5":
		return draw65Pot(position, rotation)
	elif footprint == "POT5_5":
		return draw55Pot(position, rotation) 

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

# draw functions for stripboard tracks

def drawTrack(start: App.Vector, end: App.Vector):
	width = 0.8 * grid_u
	track_points = [(start[0]- width, start[1]), (start[0] + width, start[1]), (end[0] + width, end[1]), (end[0] - width, end[1]), (start[0] - width, start[1])]
	return Part.makePolygon(track_points)

# utilities used to parse files and streamline drawing

def parse_veecad_file(per_file_path:str):
	# Open a VeeCAD *.per file.
	try:
		with open(per_file_path, 'r', encoding='utf-8') as file:
			file_text = file.readlines()
			# First three lines of the file are non-json formatted metadata; throw them away
			json_text = ' '.join(file_text[3:])
			return json.loads(json_text)
	except FileNotFoundError:
		print(f"Error: The file '{per_file_path}' was not found.")
	except json.JSONDecodeError:
		print(f"Error: Malformed JSON from file '{per_file_path}'")
	except Exception:
		print(f"Encountered Error while parsing {per_file_path}: {Exception}")


def formatTuplePoints(pts:list[tuple[int]]) -> list[App.Vector]:
    # Since VeeCAD boards are a 2d grid, I'd prefer to write points as tuples of grid points
    # convert 2d grid coordinates to mm
    pts = list(map(lambda v: (v[0]*grid_u, v[1]*grid_u), pts))
    # return these encapsulated in a vector
    return list(map(lambda v: App.Vector(v[0],v[1],0), pts))


def get_rotation(x, y) -> int:
    # converts veecad file format rotation to a 90-degree equivalent
    # (0,1):0	(1,0):90	(0,-1):180	(-1,0):270 
    if y:
        if y > 0: return 0
        else: return 180
    elif x > 0:
        return 90
    else:
        return 270


class VeeCADHandler:
    def __init__(self, per_file_path, panel_name:str="Panel"):
        self.doc = App.newDocument(panel_name)
        data = parse_veecad_file(per_file_path)
        self.panel_footprints = {"THONK", "POT6_5", "POT5_5", "SW3"}
        self.components = self.format_component_data(data['Components'])
        self.tracks = data['Board']['Strips']
		

    def drawPanel(self):
        footprints_obj = self.doc.addObject("Part::Feature", "Footprints")
        holes_obj = self.doc.addObject("Part::Feature", "Holes")

        for vals in self.components.values():
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

        self.doc.recompute()

    # def drawTracks(self):
    #     return None
	
	### Helpers
    def format_component_data(self, data:list[dict]) -> dict:
        return {cmp['Designator']: [cmp['Outline'], cmp['X1000']/1000, cmp['Y1000']/1000, 
                                    get_rotation(cmp['EndDeltaX'], cmp['EndDeltaY'])] 
                for cmp in data if cmp['Outline'] in self.panel_footprints}

    def get_footprint_names(self) -> set:
        return {cmp['Outline'] for cmp in self.components} 


###########################################################
################## PANEL DRAW UTILITIES ###################
###########################################################

# add functions to draw a eurorack panel of a given hp
# think about mounting hole placement and how to center the veecad panel

###########################################################
################ GRAPHICS DRAW UTILITIES ##################
###########################################################

# create graphics around jacks, add text below (or above?) pots
# think about jack graphics sizing, and how outputs have an inverted area
# --> may want to do a diff between the panel shape and the text vs. a line around the jack and the text below
# can I include the fonts I use?


if __name__ == "__main__":
    panel = PanelizerTaskPanel()
    Gui.Control.showDialog(panel)
    print("All done!")