#!/usr/bin/env python

#inputsFile = "cartaporte_input_parameters.json"
#inputsFile = "manifiesto_input_parameters.json"
inputsFile = "declaracion_input_parameters.json"

import json

inputs = json.load (open (inputsFile))

for key in inputs:
	input = inputs [key]
	input ["x"] = input ["x"] + 0
	input ["y"] = input ["y"] - 0
	input ["width"] = input ["width"] - 0
	input ["height"] = input ["height"] + 1

	inputs [key] = input

outFile = inputsFile.split(".")[0] + "-NEW.json"


json.dump (inputs, open (inputsFile, "w"), indent=4, sort_keys=True)
