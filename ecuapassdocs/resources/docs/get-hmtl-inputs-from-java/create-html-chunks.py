#!/usr/bin/python3 

USAGE = "get-html-inputs-from-java.py <input java file> <input json 'Txt-Field' pairs> <prefix for outputs>\n\
\n\
Create initial parameters for HTML input fields:\n\
by creating two files related with input fields bounds:\n\
	- Style lines for each input field\n\
	- Class lines for each input field\n\
"

import re, json, sys
from collections import OrderedDict

#prog = "DocPanelCartaporte.java"
if len (sys.argv) < 2:
	print (USAGE)
	sys.exit (0)

inputBoundsFilename = sys.argv [1]
outputPrefix        = sys.argv [2]

#--------------------------------------------------------------------
# Create HTML lines for style, class, and model
#--------------------------------------------------------------------
styleLines = []
classLines = []
modelLines = []

boundsDic = json.load (open (inputBoundsFilename))
for key in boundsDic:
	print (">>> key: ", key)
	bound = boundsDic [key]
	print (">>> bound: ", bound)
	left        = int (bound ["x"]) + 7
	top         = int (bound ["y"]) + 7
	width       = int (bound ["width"]) - 7
	height      = int (bound ["height"]) - 7
	iclass      = bound ["class"]

	# For styles
	styleLine = f"\t\t#{key} {{ position: absolute; left: {left}px; top: {top}px; width: {width}px; height: {height}px; }}\n"
	styleLines.append (styleLine)

	# For classes
	classLine = f'\t\t\t\t<textarea name="{key}" id="{key}" class="{iclass}"></textarea>\n'
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

