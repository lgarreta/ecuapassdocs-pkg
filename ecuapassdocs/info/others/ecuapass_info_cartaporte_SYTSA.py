#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta

from .ecuapass_info_cartaporte_NTA import CartaporteNTA
from .ecuapass_extractor import Extractor
from .ecuapass_data import EcuData
from .ecuapass_utils import Utils

#----------------------------------------------------------
USAGE = "\
Extract information from document fields analized in AZURE\n\
USAGE: ecuapass_info_cartaportes.py <Json fields document>\n"
#----------------------------------------------------------
# Main
#----------------------------------------------------------
def main ():
	args = sys.argv
	fieldsJsonFile = args [1]
	runningDir = os.getcwd ()
	mainFields = CartaporteInfo.getMainFields (fieldsJsonFile, runningDir)
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class CartaporteSytsa (CartaporteNTA):
	def __init__ (self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)
		self.empresa   = EcuData.getEmpresaInfo ("SYTSA")

	#-----------------------------------------------------------
	#-- Get 'total bultos' and 'tipo embalaje' -----------------
	#-----------------------------------------------------------
	def getBultosInfo (self):
		bultosInfo = super().getBultosInfo ()
		bultosInfo ["embalaje"] = bultosInfo ["marcas"]

		return bultosInfo
#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

