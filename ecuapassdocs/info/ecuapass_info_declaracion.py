#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc

from .ecuapass_utils import Utils
from .ecuapass_extractor import Extractor  # Extracting basic info from text

#----------------------------------------------------------
#----------------------------------------------------------
def main ():
	args = sys.argv
	fieldsJsonFile = args [1]
	runningDir = os.getcwd ()
	mainFields = Declaracion.getMainFields (fieldsJsonFile, runningDir)
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class Declaracion:
	resourcesPath = None

	#-- Get data and value from document main fields
	def getMainFields (fieldsJsonFile, runningDir):
		Utils.runningDir    = runningDir      # Dir to copy and get images and data
		Declaracion.resourcesPath = os.path.join (runningDir,"resources", "data_declaracion") 
		ecudoc = {}		                     # Dic for Ecuappass document info

		try:
			fields = json.load (open (fieldsJsonFile))
			fields ["jsonFile"] = fieldsJsonFile

			ecudoc ["01_Distrito"]      = "TULCAN||LOW"
			
			ecudoc ["02_Fecha_Emision"] = Declaracion.getFechaEmision (fields, "23_Fecha_Emision")
			ecudoc ["03_Procedimiento"] = "IMPORTACION||LOW"
			ecudoc ["04_Numero_DTAI"]    = Declaracion.getNumeroDocumento (fields, "00b_Numero")
			ecudoc ["05_Pais_Origen"]   = Declaracion.getPaisMercancia (fields, "09_Pais_Mercancia")

			aduanaCarga                 = Declaracion.getAduanaCiudadPais (fields, "06_Aduana_Carga")
			ecudoc ["06_Pais_Carga"]     = aduanaCarga ["pais"]
			ecudoc ["07_Aduana_Carga"]   = aduanaCarga ["ciudad"]

			aduanaPartida               = Declaracion.getAduanaCiudadPais (fields, "07_Aduana_Partida")
			ecudoc ["08_Pais_Partida"]   = aduanaPartida ["pais"]
			ecudoc ["09_Aduana_Partida"] = aduanaPartida ["ciudad"]

			aduanaDestino               = Declaracion.getAduanaCiudadPais (fields, "08_Aduana_Destino")
			ecudoc ["10_Pais_Destino"]   = aduanaDestino ["pais"]
			ecudoc ["11_Aduana_Destino"] = aduanaDestino ["ciudad"]

		except:
			printx (f"ALERTA: Problemas extrayendo información del documento '{fieldsJsonFile}'")
			printx (traceback_format_exc())
			raise

		#Declaracion.printFieldsValues (ecudoc)
		return (ecudoc)


	#-- Get fecha de emisión ----------------------------------------
	def getFechaEmision (fields, key):
		text = getValue (fields, key) 
		
		fecha      = Extractor.getDate (text, Declaracion.resourcesPath)
		return (fecha)
	
	#-- Get "numero documento" --------------------------------------
	def getNumeroDocumento (fields, key):
		text     = getValue (fields, key) 
		reNumber = r'(?:No\.\s*)?([A-Za-z0-9]+)'
		number   = Extractor.getValueRE (reNumber, text)
		return number

	#-- Pais origen mercancia ---------------------------------------
	def getPaisMercancia (fields, key):
		text     = getValue (fields, key) 
		pais     = Extractor.getPais (text, Declaracion.resourcesPath)
		pais     = pais if pais else "||LOW"
		return pais

	#-- Aduana info: ciudad + pais ----------------------------------
	def getAduanaCiudadPais (fields, key):
		aduana = {"pais": "||LOW", "ciudad": "||LOW"}
		text = getValue (fields, key)
		info = Extractor.extractCiudadPais (text, Declaracion.resourcesPath)
		aduana ["pais"]   = info ["pais"] if info ["pais"] else "||LOW"
		aduana ["ciudad"] = info ["ciudad"] if info ["ciudad"] else "||LOW"

		return aduana


#-------------------------------------------------------------------
# Global utility functions
#-------------------------------------------------------------------
def printx (*args, flush=True, end="\n", plain=False):
	print ("SERVER:", *args, flush=flush, end=end)

def printException (message, e=None):
	#printx ("EXCEPCION: ", message) 
	printx (traceback_format_exc())
	exc_type = type(e).__name__
	exc_msg = str(e)
	printx (f"EXCEPCION: {message}. {exc_type} : '{exc_msg}'")

#-- Get value from fields [key] dict
def getValue (fields, key):
	try:
		return fields [key]["content"]
	except:
		printException ("EXEPCION: Obteniendo valor para la llave:", key)
		return None

def createEmptyDic (keys):
	emptyDic = {}
	for key in keys:
		emptyDic [key] = None
	return emptyDic

def checkLow (value):
	return value if value !=None else "||LOW"
		


#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

