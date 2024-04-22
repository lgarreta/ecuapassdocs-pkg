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
class ManifiestoByza (ManifiestoInfo):
	def __init__(self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)

	#-- Get empresa info
	def getEmpresaInfo (self):
		return EcuData.getEmpresaInfo ("BYZA")

	def __str__(self):
		return f"{self.numero}"

	#-- Get tipo vehículo (VEHICULO/REMOLQUE) according to remolque info
	def getTipoVehiculo  (self, tipo, remolque):
		if tipo == "VEHICULO" and remolque ["placa"]:
			return "TRACTOCAMION"
		elif tipo == "VEHICULO" and not remolque ["placa"]:
			return "CAMION"
		else:
			return None

	#-- None for BYZA
	def getCheckCertificadoRemolque (self, key):
		return None

	#-- None for BYZA 
	def getCargaDescripcion (self):
			return None

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

