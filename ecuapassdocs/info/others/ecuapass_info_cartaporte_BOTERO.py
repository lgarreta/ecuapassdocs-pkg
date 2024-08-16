#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta

from .ecuapass_info_cartaporte import CartaporteInfo
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
class CartaporteBotero (CartaporteInfo):
	def __init__ (self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)
		self.empresa   = EcuData.getEmpresaInfo ("BOTERO")

	#-------------------------------------------------------------------
	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro ---------
	#-- BOTERO-SOTO format: <Nombre> <Id> <Direccion> <PaisCiudad> -----
	#-------------------------------------------------------------------
	def getSubjectInfo (self, key):
		subject = {"nombre":None, "direccion":None, "pais": None, 
		           "ciudad":None, "tipoId":None, "numeroId": None}
		text	= Utils.getValue (self.fields, key)
		text  = text.replace ("\n", " ")
		try:
			text    = re.sub ("\s*//\s*", "", text)   # For SILOG "//" separator cartaportes
			text, subject = Extractor.getReplaceSubjectId (text, subject, "|", key)
			subject ["numeroId"] = Utils.convertToEcuapassId (subject ["numeroId"])
			text, subject = Extractor.removeSubjectCiudadPais (text, subject, self.resourcesPath, key)
			subject ["nombre"]    = text.split ("|")[0].strip()
			subject ["direccion"] = text.split ("|")[1].strip()
		except:
			Utils.printException (f"Obteniendo datos del sujeto: '{key}' en el texto", text)

		return (subject)

	def getNumeroCPIC (self):
		text   = Utils.getValue (self.fields, "00b_Numero_Documento")
		numero = Extractor.getNumeroDocumento (text)
		return numero
#	#-------------------------------------------------------------------
#	#-- Get location info: ciudad, pais, fecha -------------------------
#	#-- Boxes: Recepcion, Embarque, Entrega ----------------------------
#	#-------------------------------------------------------------------
#	def getLocationInfo (self, key):
#		location = {"ciudad":"||LOW", "pais":"||LOW", "fecha":"||LOW"}
#		try:
#			text   = Utils.getValue (self.fields, key)
#			text   = text.replace ("\n", " ")
#			# Fecha
#			fecha = Extractor.getDate (text, self.resourcesPath)
#			location ["fecha"] = fecha if fecha else "||LOW"
#			# Pais
#			text, location = Extractor.removeSubjectCiudadPais (text, location, self.resourcesPath, key)
#		except:
#			Utils.printException (f"Obteniendo datos de lo localización: '{key}' en el texto", text)
#
#		return (location)

#	#-----------------------------------------------------------
#	# Get "Entrega" location and suggest a date if it is None
#	#-----------------------------------------------------------
#	def getEntregaLocation (self, key):
#		location = self.getLocationInfo (key)
#		try:
#			# Add a week to 'embarque' date
#			if location ["fecha"] == "||LOW":
#				fechaEmbarque      = self.ecudoc ["34_FechaEmbarque"]
#				date_obj           = datetime.strptime (fechaEmbarque, "%d-%m-%Y")
#				new_date_obj       = date_obj + timedelta(weeks=1)
#				location ["fecha"] = new_date_obj.strftime("%d-%m-%Y") + "||LOW"
#		except:
#			Utils.printException ("Obteniendo información de 'entrega'")
#
#		return location

#	#-----------------------------------------------------------
#	# Get "transporte" and "pago" conditions
#	#-----------------------------------------------------------
#	def getCondiciones (self):
#		conditions = {'pago':None, 'transporte':None}
#		# Condiciones transporte
#		try:
#			text = self.fields ["09_Condiciones"]["value"]
#			if "SIN CAMBIO" in text.upper():
#				conditions ["transporte"] = "DIRECTO, SIN CAMBIO DEL CAMION"
#			elif "CON CAMBIO" in text.upper():
#				conditions ["transporte"] = "DIRECTO, CON CAMBIO DEL TRACTO-CAMION"
#			elif "TRANSBORDO" in text.upper():
#				conditions ["transporte"] = "TRANSBORDO"
#		except:
#			Utils.printException ("Extrayendo informacion de condiciones de transporte", text)
#
#		# Condiciones pago
#		try:
#			if "CREDITO" in text:
#				conditions ["pago"] = "POR COBRAR||LOW"
#			elif "ANTICIPADO" in text:
#				conditions ["pago"] = "PAGO ANTICIPADO||LOW"
#			elif "CONTADO" in text:
#				conditions ["pago"] = "PAGO ANTICIPADO||LOW"
#			else:
#				pagoString = Extractor.getDataString ("condiciones_pago.txt", self.resourcesPath)
#				rePagos    = rf"\b({pagoString})\b" # RE to find a match string
#				pago       = Extractor.getValueRE (rePagos, text)
#				conditions ["pago"] = pago if pago else None 
#		except:
#			Utils.printException ("Extrayendo informacion de condiciones de pago en el texto:", text)
#
#		return conditions

#	#-----------------------------------------------------------
#	# Get info from unidades de medida:"peso neto, volumente, otras
#	#-----------------------------------------------------------
#	def getUnidadesMedidaInfo (self):
#		unidades = {"pesoNeto":None, "pesoBruto": None, "volumen":None, "otraUnidad":None}
#		try:
#			unidades ["pesoNeto"]   = Extractor.getNumber (self.fields ["13a_Peso_Neto"]["value"])
#			unidades ["pesoBruto"]  = Extractor.getNumber (self.fields ["13b_Peso_Bruto"]["value"])
#			unidades ["volumen"]	  = Extractor.getNumber (self.fields ["14_Volumen"]["value"])
#			unidades ["otraUnidad"] = Extractor.getNumber (self.fields ["15_Otras_Unidades"]["value"])
#
#			for k in unidades.keys():
#				unidades [k] = Utils.convertToAmericanFormat (unidades [k])
#		except:
#			Utils.printException ("Obteniendo información de 'Unidades de Medida'")
#		return unidades

#	#-----------------------------------------------------------
#	#-- Get 'total bultos' and 'tipo embalaje' -----------------
#	#-----------------------------------------------------------
#	def getBultosInfo (self):
#		bultos = Utils.createEmptyDic (["cantidad", "embalaje", "marcas", "descripcion"])
#		try:
#			# Cantidad
#			text             = self.fields ["10_CantidadClase_Bultos"]["value"]
#			bultos ["cantidad"] = Utils.convertToAmericanFormat (Extractor.getNumber (text))
#			bultos ["embalaje"] = Extractor.getTipoEmbalaje (text)
#
#			# Marcas 
#			text = self.fields ["11_MarcasNumeros_Bultos"]["value"]
#			bultos ["marcas"] = "SIN MARCAS" if text == None else text
#
#			# Descripcion
#			bultos ["descripcion"] = self.fields ["12_Descripcion_Bultos"]["content"]
#		except:
#			Utils.printException ("Obteniendo información de 'Bultos'", text)
#
#		return bultos

#	#--------------------------------------------------------------------
#	#-- Search "pais" for "ciudad" in previous document boxes
#	#--------------------------------------------------------------------
#	def searchPaisPreviousBoxes (self, ciudad, pais):
#		try:
#			# Search 'pais' in previos boxes
#			if (ciudad != None and pais == None):
#				if self.ecudoc ["30_CiudadRecepcion"] and ciudad in self.ecudoc ["30_CiudadRecepcion"]:
#					pais = self.ecudoc ["29_PaisRecepcion"]
#				elif self.ecudoc ["33_CiudadEmbarque"] and ciudad in self.ecudoc ["33_CiudadEmbarque"]:
#					pais = self.ecudoc ["32_PaisEmbarque"]
#				elif self.ecudoc ["36_CiudadEntrega"] and ciudad in self.ecudoc ["36_CiudadEntrega"]:
#					pais = self.ecudoc ["35_PaisEntrega"]
#
#		except:
#			Utils.printException ("Obteniendo informacion de 'mercancía'")
#		return ciudad, pais
#
#	#-----------------------------------------------------------
#	# Get info from 'documentos recibidos remitente'
#	#-----------------------------------------------------------
#	def getDocsRemitente (self):
#		docs = None
#		try:
#			docs = self.fields ["18_Documentos"]["value"]
#		except:
#			Utils.printException("Obteniendo valores 'DocsRemitente'")
#		return docs

#	#-----------------------------------------------------------
#	#-- Get instrucciones y observaciones ----------------------
#	#-----------------------------------------------------------
#	def getInstruccionesObservaciones (self):
#		instObs = {"instrucciones":None, "observaciones":None}
#		try:
#			instObs ["instrucciones"] = self.fields ["21_Instrucciones"]["content"]
#			instObs ["observaciones"] = self.fields ["22_Observaciones"]["content"]
#		except:
#			Utils.printException ("Obteniendo informacion de 'Instrucciones y Observaciones'")
#		return instObs
	
#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

