#!/usr/bin/env python
import json

pairsFile    = "cartaporte-html-form-classes-ByFields.json"
fieldsFile   = "cartaporte_parameters_for_fields.json"
inputsFile   = "cartaporte_parameters_for_inputs.json"
outFile      = "cartaporte_input_parameters.json"

pairs = json.load (open (pairsFile))
fields  = json.load (open (fieldsFile))
inputs   = json.load (open (inputsFile))

allInputs = {}

for key in inputs.keys():
	input = inputs [key]

	newInput  = {}

	newInput ["value"]  = ""
	newInput ["x"]      = input ["x"]
	newInput ["y"]      = input ["y"]
	newInput ["width"]  = input ["width"]
	newInput ["height"] = input ["height"]
	newInput ["align"]  = input ["align"]
	newInput ["field"]  = input ["field"]
	newInput ["font"]  = input ["font"]

	iclass = pairs [key]
	field  = fields [iclass]

	newInput ["maxLines"] = field ["maxLines"]
	newInput ["maxChars"] = field ["maxChars"]
	newInput ["fontSize"] = field ["fontSize"]

	newInput ["class"]    = iclass

	allInputs [key] = newInput


print (allInputs)
json.dump (allInputs, open (outFile, "w"), indent=4, sort_keys=True)



