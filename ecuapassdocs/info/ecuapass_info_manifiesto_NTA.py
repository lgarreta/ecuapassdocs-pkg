#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc

from .ecuapass_info_manifiesto import ManifiestoInfo
from .ecuapass_data import EcuData
from .ecuapass_utils import Utils
from .ecuapass_extractor import Extractor  # Extracting basic info from text

#----------------------------------------------------------
USAGE = "\
Extract information from document fields analized in AZURE\n\
USAGE: ecuapass_info_manifiesto.py <Json fields document>\n"
#----------------------------------------------------------
def main ():
	args = sys.argv
	fieldsJsonFile = args [1]
	runningDir = os.getcwd ()
	mainFields = ManifiestoInfo.getMainFields (fieldsJsonFile, runningDir)
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class ManifiestoNTA (ManifiestoInfo):
	def __init__(self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)

	#-- get empresa info
	def getEmpresaInfo (self):
		return EcuData.getEmpresaInfo ("NTA")

	#-- Get tipo vehículo according to remolque info
	def getTipoVehiculo  (self, tipo, remolque):
		if tipo == "VEHICULO" and remolque ["placa"]:
			return "SEMIRREMOLQUE"
		elif tipo == "VEHICULO" and not remolque ["placa"]:
			return "CAMION"
		elif tipo == "REMOLQUE" and remolque ["placa"]:
			return "SEMIRREMOLQUE"
		else:
			return None

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

