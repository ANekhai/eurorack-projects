import os, sys

# allow importing local python files
cwd = os.path.dirname(__file__)
if cwd not in sys.path: sys.path.append(cwd)

import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtCore, QtWidgets
import draw_utils # TODO: only import runners from draw_utils

import json

ui_path = os.path.join(cwd, "ui", "panelizer.ui")

### This file consists of the GUI for the panelizer plugin.
### This is the base Macro file to be run, though various other utilities are scattered
### around the other imported files.


# data = extract_veecad_components(path)
# data = format_component_data(data)

class PanelizerTaskPanel:
    def __init__(self):
        # load Qt Designer ui file
        self.form = Gui.PySideUic.loadUi(ui_path)

        # file browser click overwrites
        self.form.InCADFile.clicked.connect(self.open_file_browser)


        if not position_file:
            print()
            return
        
        # I should probably put the preview logic as function calls in here


    def open_file_browser(self):
        # Open standard Qt file browser to pick VeeCAD file
        file_info = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select File", "", "All Files (*.*)"
        )
        # read veecad per file
        user_path = file_info[0]
        # update text box in UI
        self.form.LineEditPath.setText(user_path)

        try:
            # try to open file, run some validation on the fields
            _ = None
        except Exception as e:
            print(e)




    def accept(self):
        name = self.form.PanelName.value()

        # this is where I read in a bunch of stuff and kick off the panelization runners


###########################
### VeeCAD file parsing ###
###########################

def open_veecad_file(path:str):
    # open veecad file and read
    return ""



def extract_veecad_components(per_file_path:str) -> list[dict]:
    try:
        with open(per_file_path, 'r', encoding='utf-8') as file:
            # skip header data, read json block
            file_text = file.readlines()
            
            json_data = ' '.join(file_text[3:])
            json_data = json.loads(json_data)
        
        return json_data['Components']

    except FileNotFoundError:
        print(f"Error: The file '{per_file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON from file '{per_file_path}'")
    except Exception:
        print(f"Encountered Error while parsing {per_file_path}: {Exception}")


def get_footprint_names(data: list[dict]) -> set:
    return {cmp['Outline'] for cmp in data}


def format_component_data(data:list[dict]) -> dict:
    return {cmp['Designator']: [cmp['Outline'], cmp['X1000']/1000, cmp['Y1000']/1000, 
                                get_rotation(cmp['EndDeltaX'], cmp['EndDeltaY'])] 
                for cmp in data}


def extract_veecad_tracks(per_file_path:str) -> list[tuple]:
    return None

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
    
    if __name__ == "__main__":
        return 0