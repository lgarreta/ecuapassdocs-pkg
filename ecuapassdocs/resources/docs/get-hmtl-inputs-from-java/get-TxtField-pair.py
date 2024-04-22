#!/usr/bin/env python
"""
Create a Txt : Field JSON file, where Txt is the
name of the input in html form, and Field is the 
name of the field in azure Fields
"""

import sys, json

args = sys.argv 

#inputBoundsFile = "old-cartaporte_inputs.json"
inputBoundsFile = "MANIFIESTO-MCI-NTA-COCO004121-FIELDS.json"

jsonData = json.load (open (inputBoundsFile))

print (jsonData)

dicPairs = {}
keys = jsonData.keys ()
keys.sort()
for key in keys:
	txtKey = "txt" +  key.split ("_")[0]
	if txtKey in dicPairs.keys ():
		txtKey = txtKey + "1"
	dicPairs [txtKey] = key

# For extracting from cartaporte "field" input
#for key in jsonData.keys():
#	dicPairs [key] = jsonData[key] ["field"]

jsonData = json.dumps (dicPairs, indent=4, sort_keys=True)
open ("manifiesto-TxtField-pairs-TMP.json", "w").write(jsonData)
