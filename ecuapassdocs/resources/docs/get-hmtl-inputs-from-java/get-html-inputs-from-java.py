#!/usr/bin/python3 

USAGE = "get-html-inputs-from-java.py <input java file> <input json 'Txt-Field' pairs> <prefix for outputs>\n\
\n\
Create initial parameters for HTML input fields:\n\
by creating three files related with input fields bounds:\n\
	- JSON with 'txtXX': [top, left, width, height]\n\
	- Style lines for each input field\n\
	- Class lines for each input field\n\
"

import re, json, sys
from collections import OrderedDict

#prog = "DocPanelCartaporte.java"
if len (sys.argv) < 3:
	print (USAGE)
	sys.exit (0)

inputFilename = sys.argv [1]
inputTxtFieldFile  = sys.argv [2]
outputPrefix  = sys.argv [3]

#--------------------------------------------------------------------
# Read lines of file
#--------------------------------------------------------------------
lines = open (inputFilename).readlines ()


#--------------------------------------------------------------------
# Extract bounds: x, y, width, height 
#--------------------------------------------------------------------
boundsDic = OrderedDict ()
txtFieldPairsDic = json.load (open (inputTxtFieldFile))
for line in lines:
	if "txt" in line and "Bounds" in line:
		print (">>>", line)
		key = line.split (".")[0].strip()
		res = [int (x) for x in re.findall (r"\b(\d+)\b", line)]
		boundsDic [key] = {"x":res [0], "y": res[1], "width":res[2], "height":res [3],
		                   "nlines":1, "nChars":100, "font":"normal", "align":"left"}
		boundsDic [key]["field"] = txtFieldPairsDic [key]


#--------------------------------------------------------------------
# Extracts restrictions: nLines, nChars, font, align
#--------------------------------------------------------------------
for line in lines:
	if "this.txt" in line and "setParameters" in line:
		print (">>> Line:", line.strip())
		key   = line.split (".")[1].strip()       # this.txt18.setParameters (2, 70, "normal");
		text   = line.split (".")[2].strip()       # this.txt18.setParameters (2, 70, "normal");
		params = re.split (r",\s*", re.search (r"\((.*)\)", text).group(1))
		
		params = {"nlines": int (params [0]), "nChars": int (params [1]), "font": params [2].split('"')[1]}
		params ["align"] = "left" if len (params) <= 3 else params [3]

		boundsDic [key].update (params)

with (open (f"{outputPrefix}_html_bounds.json", "w")) as fp:
	json.dump (boundsDic, fp, indent=4)

#--------------------------------------------------------------------
# Create HTML lines for style, class, and model
#--------------------------------------------------------------------
styleLines = []
classLines = []
modelLines = []
for key in boundsDic:
	print (">>> key: ", key)
	bound = boundsDic [key]
	print (">>> bound: ", bound)
	left        = int (bound ["x"]) + 7
	top         = int (bound ["y"]) + 7
	width       = int (bound ["width"]) - 7
	height      = int (bound ["height"]) - 7
	iclass  = int (bound ["class"])

	# For styles
	styleLine = f"\t\t#{key} {{ position: absolute; left: {left}px; top: {top}px; width: {width}px; height: {height}px; }}\n"
	styleLines.append (styleLine)

	# For classes
	classLine = f'\t\t\t\t<textarea name="{key}" id="{key}" class "{iclass}" placeholder="Texto {key.split("txt")[1]}"></textarea>\n'
	classLines.append (classLine)

	# For model
	modelLine = f"\t{key} = models.CharField (max_length=200)\n"
	modelLines.append (modelLine)

with (open (f"{outputPrefix}_html_styles.html", "w")) as fp:
	fp.writelines (styleLines)

with (open (f"{outputPrefix}_html_classes.html", "w")) as fp:
	fp.writelines (classLines)

with (open (f"{outputPrefix}_python_model_fields.html", "w")) as fp:
	fp.writelines (modelLines)

