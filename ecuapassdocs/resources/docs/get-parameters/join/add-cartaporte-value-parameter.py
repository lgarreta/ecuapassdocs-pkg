#!/usr/bin/env python
import json

inputFile = "manifiesto_input_parameters.json"
outputFile = "manifiesto_input_parameters-VALUE.json"

inputs = json.load (open (inputFile))

for key in inputs:
	inputs [key]["value"] = ""

json.dump (inputs, open (outputFile, "w"), indent=4, sort_keys=True)
