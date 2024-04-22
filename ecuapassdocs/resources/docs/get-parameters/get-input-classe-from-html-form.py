#!/usr/bin/env python3

# Extract class for input fields

import re, json
inFile = "cartaporte-html-form.html"
fp = open (inFile)
lines = fp.readlines ()

classesDic = {}
fieldsDic = {}
for line in lines:
	#print (">>> Line: ", line)
	res = re.search (r'name=\"(\w*)\".*class=\"(.*)\".*', line)
	if res:
		txtKey   = res.groups (1)[0]
		txtClass = res.groups (2)[1]
		fieldsDic [txtKey] = txtClass
		if txtClass in classesDic.keys():
			classesDic [txtClass].append (txtKey)
		else:
			classesDic [txtClass] = [txtKey]
		

print (classesDic)
with (open ("cartaporte-html-form-classes-ByClasses.json", "w")) as fp:
	json.dump (classesDic, fp, indent=4)

with (open ("cartaporte-html-form-classes-ByFields.json", "w")) as fp:
	json.dump (fieldsDic, fp, indent=4)
	
