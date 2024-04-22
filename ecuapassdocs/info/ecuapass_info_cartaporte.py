#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta

from .ecuapass_info import EcuInfo
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
class CartaporteInfo (EcuInfo):

	def __init__ (self, fieldsJsonFile, runningDir):
		super().__init__ ("CARTAPORTE", fieldsJsonFile, runningDir)

	#-- Get data and value from document main fields"""
	def getMainFields (self):
		try:
			#--------------------------------------------------------------
			# print ("\n>>>>>> Carta de Porte Internacional por Carretera <<<")
			#--------------------------------------------------------------
			self.ecudoc ["01_Distrito"]	         = self.getDistrito ()
			self.ecudoc ["02_NumeroCPIC"]        = self.getNumeroDocumento ()
			self.ecudoc ["03_MRN"]               = self.getMRN ()
			self.ecudoc ["04_MSN"]               = self.getMSN () 
			self.ecudoc ["05_TipoProcedimiento"] = self.getTipoProcedimiento ()

			#-- Empresa
			self.ecudoc ["06_EmpresaTransporte"] = self.getNombreEmpresa ()
			self.ecudoc ["07_DepositoMercancia"] = self.getDepositoMercancia ()
			self.ecudoc ["08_DirTransportista"]	 = self.getDireccionEmpresa ()
			self.ecudoc ["09_NroIdentificacion"] = self.getIdEmpresa ()

			#--------------------------------------------------------------
			# print ("\n>>>>>> Datos Generales de la CPIC: Sujetos <<<<<<<<")
			#--------------------------------------------------------------
			#-- Remitente 
			remitente                             = Utils.checkLow (self.getSubjectInfo ("02_Remitente"))
			self.ecudoc ["10_PaisRemitente"]      = remitente ["pais"]
			self.ecudoc ["11_TipoIdRemitente"]    = remitente ["tipoId"]
			self.ecudoc ["12_NroIdRemitente"]	  = remitente ["numeroId"]
			self.ecudoc ["13_NroCertSanitario"]	  = None
			self.ecudoc ["14_NombreRemitente"]    = remitente ["nombre"]
			self.ecudoc ["15_DireccionRemitente"] = remitente ["direccion"]

			#-- Destinatario 
			destinatario                             = Utils.checkLow (self.getSubjectInfo ("03_Destinatario"))
			self.ecudoc ["16_PaisDestinatario"]	     = destinatario ["pais"] 
			self.ecudoc ["17_TipoIdDestinatario"]    = destinatario ["tipoId"] 
			self.ecudoc ["18_NroIdDestinatario"]     = destinatario ["numeroId"] 
			self.ecudoc ["19_NombreDestinatario"]    = destinatario ["nombre"] 
			self.ecudoc ["20_DireccionDestinatario"] = destinatario ["direccion"] 

			#-- Consignatario 
			consignatario                             = Utils.checkLow (self.getSubjectInfo ("04_Consignatario"))
			self.ecudoc ["21_PaisConsignatario"]      = consignatario ["pais"] 
			self.ecudoc ["22_TipoIdConsignatario"]    = consignatario ["tipoId"] 
			self.ecudoc ["23_NroIdConsignatario"]     = consignatario ["numeroId"] 
			self.ecudoc ["24_NombreConsignatario"]    = consignatario ["nombre"] 
			self.ecudoc ["25_DireccionConsignatario"] = consignatario ["direccion"] 

			#-- Notificado 
			notificado                                = self.getSubjectInfo ("05_Notificado")
			self.ecudoc ["26_NombreNotificado"]	      = notificado ["nombre"] 
			self.ecudoc ["27_DireccionNotificado"]    = notificado ["direccion"] 
			self.ecudoc ["28_PaisNotificado"]         = notificado ["pais"] 

			#--------------------------------------------------------------
			# print ("\n>>>>>> Datos Generales de la CPIC: Locaciones <<<<<<<<")
			#--------------------------------------------------------------
			#-- Recepcion 
			recepcion                           = self.getLocationInfo ("06_Recepcion")
			self.ecudoc ["29_PaisRecepcion"]    = recepcion ["pais"] 
			self.ecudoc ["30_CiudadRecepcion"]  = recepcion ["ciudad"] 
			self.ecudoc ["31_FechaRecepcion"]   = recepcion ["fecha"] 

			#-- Embarque location box
			embarque                           = self.getLocationInfo ("07_Embarque")
			self.ecudoc ["32_PaisEmbarque"]    = embarque ["pais"] 
			self.ecudoc ["33_CiudadEmbarque"]  = embarque ["ciudad"] 
			self.ecudoc ["34_FechaEmbarque"]   = embarque ["fecha"] 

			#-- Entrega location box
			entrega	                          = self.getEntregaLocation ("08_Entrega")
			self.ecudoc ["35_PaisEntrega"]    = entrega ["pais"] 
			self.ecudoc ["36_CiudadEntrega"]  = entrega ["ciudad"] 
			self.ecudoc ["37_FechaEntrega"]   = entrega ["fecha"] 

			#--------------------------------------------------------------
			# print ("\n>>>>>> Datos Generales de la CPIC: Condiciones <<<<<<<<")
			#--------------------------------------------------------------
			condiciones                              = Utils.checkLow (self.getCondiciones ())
			self.ecudoc ["38_CondicionesTransporte"] = condiciones ["transporte"]
			self.ecudoc ["39_CondicionesPago"]       = condiciones ["pago"]

			unidades                       = self.getUnidadesMedidaInfo ()
			bultosInfo                         = self.getBultosInfo ()
			self.ecudoc ["40_PesoNeto"]	   = unidades ["pesoNeto"]
			self.ecudoc ["41_PesoBruto"]   = unidades ["pesoBruto"]
			self.ecudoc ["42_TotalBultos"] = bultosInfo ["cantidad"]
			self.ecudoc ["43_Volumen"]	   = unidades ["volumen"]
			self.ecudoc ["44_OtraUnidad"]  = unidades ["otraUnidad"]

			# Incoterm
			text                                = self.fields ["16_Incoterms"]["value"]
			incoterms                           = self.getIncotermInfo (text)
			self.ecudoc ["45_PrecioMercancias"]	= incoterms ["precio"]
			self.ecudoc ["46_INCOTERM"]	        = incoterms ["incoterm"] 
			self.ecudoc ["47_TipoMoneda"]       = incoterms ["moneda"] 
			self.ecudoc ["48_PaisMercancia"]    = incoterms ["pais"] 
			self.ecudoc ["49_CiudadMercancia"]	= incoterms ["ciudad"] 

			# Gastos
			gastos                                     = self.getGastosInfo ()
			self.ecudoc ["50_GastosRemitente"]         = gastos ["fleteRemi"] 
			self.ecudoc ["51_MonedaRemitente"]	       = gastos ["monedaRemi"] 
			self.ecudoc ["52_GastosDestinatario"]      = gastos ["fleteDest"] 
			self.ecudoc ["53_MonedaDestinatario"]      = gastos ["monedaDest"] 
			self.ecudoc ["54_OtrosGastosRemitente"]    = gastos ["otrosGastosRemi"] 
			self.ecudoc ["55_OtrosMonedaRemitente"]    = gastos ["otrosMonedaRemi"] 
			self.ecudoc ["56_OtrosGastosDestinatario"] = gastos ["otrosGastosDest"] 
			self.ecudoc ["57_OtrosMonedaDestinataio"]  = gastos ["otrosMonedaDest"] 
			self.ecudoc ["58_TotalRemitente"]          = gastos ["totalGastosRemi"] 
			self.ecudoc ["59_TotalDestinatario"]       = gastos ["totalGastosDest"] 

			# Documentos remitente
			self.ecudoc ["60_DocsRemitente"]   = self.getDocsRemitente ()

			# Emision location box
			emision	                           = self.getLocationInfo ("19_Emision")
			self.ecudoc ["61_FechaEmision"]    = emision ["fecha"] 
			self.ecudoc ["62_PaisEmision"]     = emision ["pais"] 
			self.ecudoc ["63_CiudadEmision"]   = emision ["ciudad"] 
			
			# Instrucciones y Observaciones
			#instObs	                           = self.getInstruccionesObservaciones ()
			#self.ecudoc ["64_Instrucciones"]   = instObs ["instrucciones"]
			#self.ecudoc ["65_Observaciones"]   = instObs ["observaciones"]
			self.ecudoc ["64_Instrucciones"]   = None
			self.ecudoc ["65_Observaciones"]   = None

			# Detalles
			self.ecudoc ["66_Secuencia"]      = "1"
			self.ecudoc ["67_TotalBultos"]    = self.ecudoc ["42_TotalBultos"]
			self.ecudoc ["68_Embalaje"]       = bultosInfo ["embalaje"]
			self.ecudoc ["69_Marcas"]         = bultosInfo ["marcas"]
			self.ecudoc ["70_PesoNeto"]	      = self.ecudoc ["40_PesoNeto"]
			self.ecudoc ["71_PesoBruto"]      = self.ecudoc ["41_PesoBruto"]
			self.ecudoc ["72_Volumen"]	      = self.ecudoc ["43_Volumen"]
			self.ecudoc ["73_OtraUnidad"]     = self.ecudoc ["44_OtraUnidad"]

			# IMOs
			self.ecudoc ["74_Subpartida"]       = None
			self.ecudoc ["75_IMO1"]             = None
			self.ecudoc ["76_IMO2"]             = None
			self.ecudoc ["77_IMO2"]             = None
			self.ecudoc ["78_NroCertSanitario"] = self.ecudoc ["13_NroCertSanitario"]
			self.ecudoc ["79_DescripcionCarga"] = bultosInfo ["descripcion"]

		except:
			Utils.printx (f"ALERTA: Problemas extrayendo información del documento '{self.fieldsJsonFile}'")
			Utils.printx (traceback_format_exc())
			raise

		#CartaporteInfo.printFieldsValues (ecudoc)
		return (self.ecudoc)

	#------------------------------------------------------------------
	#-- Updated document fields with processed ecufields
	#------------------------------------------------------------------
	def updateFields (self):
			# Update fields
			self.fields ["12_Descripcion_Bultos"]["content"] = self.ecudoc ["79_DescripcionCarga"]
			return self.fields

	#------------------------------------------------------------------
	#-- First level functions for each Ecuapass field
	#------------------------------------------------------------------
	def getDistrito (self):
		return "TULCAN" + "||LOW"

	def getMRN (self):
		MRN = self.empresa ["MRN"]
		return MRN if MRN else "||LOW"

	def getMSN (self):
		MSN = self.empresa ["MSN"]
		return MSN if MSN else "||LOW"

	def getNombreEmpresa (self):
		return self.empresa ["nombre"]

	#------------------------------------------------------------
	# Return the code number from the text matching a "deposito"
	#-- BOTERO-SOTO en casilla 21 o 22, NTA en la 22 ------------
	#------------------------------------------------------------
	def getDepositoMercancia (self):
		for casilla in ["21_Instrucciones", "22_Observaciones"]:
			text = ""
			try:
				text        = Utils.getValue (self.fields, casilla)
				reBodega    = r'BODEGA[S]?\s+\b(\w*)\b'
				bodegaText  = Extractor.getValueRE (reBodega, text)
				Utils.printx (f"Extrayendo código para el deposito '{bodegaText}'")

				depositosDic = Extractor.getDataDic ("depositos_tulcan.txt", self.resourcesPath)

				for id in depositosDic:
					if bodegaText in depositosDic [id]:
						Utils.printx (f"...Encontrado código '{id}' para '{depositosDic [id]}'")
						return id
			except:
				Utils.printException (f"EXCEPCION: Obteniendo bodega desde texto '{text}'")
		return "||LOW"

	def old_getDepositoMercancia (self):
		for casilla in ["21_Instrucciones", "22_Observaciones"]:
			try:
				text        = Utils.getValue (self.fields, casilla)
				reBodega    = r'BODEGA[S]?\s+\b(\w*)\b'
				bodegaText  = Extractor.getValueRE (reBodega, text)

				bodegasString = Extractor.getDataString ("depositos_tulcan.txt", self.resourcesPath)
				for bodegaFullname in bodegasString.split ("|"):
					#Utils.printx (f"Bodega texto: '{bodegaText}', BodegaFullname: '{bodegaFullname}'")
					if bodegaText in bodegaFullname:
						return bodegaFullname
			except:
				Utils.printx (f"EXCEPCION: Obteniendo bodega desde texto '{text}'")
		return "||LOW"

	def getDireccionEmpresa (self):
		return self.empresa ["direccion"]

	def getIdEmpresa (self):
		id = Utils.convertToEcuapassId (self.empresa ["idNumero"])
		return id
	#-------------------------------------------------------------------
	#-- Get location info: ciudad, pais, fecha -------------------------
	#-- Boxes: Recepcion, Embarque, Entrega ----------------------------
	#-------------------------------------------------------------------
	def getLocationInfo (self, key):
		location = {"ciudad":"||LOW", "pais":"||LOW", "fecha":"||LOW"}
		try:
			text   = Utils.getValue (self.fields, key)
			text   = text.replace ("\n", " ")
			# Fecha
			fecha = Extractor.getDate (text, self.resourcesPath)
			location ["fecha"] = fecha if fecha else "||LOW"
			# Pais
			text, location = Extractor.removeSubjectCiudadPais (text, location, self.resourcesPath, key)
		except:
			Utils.printException (f"Obteniendo datos de lo localización: '{key}' en el texto", text)

		return (location)

	#-----------------------------------------------------------
	# Get "Entrega" location and suggest a date if it is None
	#-----------------------------------------------------------
	def getEntregaLocation (self, key):
		location = self.getLocationInfo (key)
		try:
			# Add a week to 'entrega' from 'embarque' date
			if location ["fecha"] == "||LOW":
				fechaEmbarque      = self.ecudoc ["34_FechaEmbarque"]
				print (fechaEmbarque)
				date_obj           = datetime.strptime (fechaEmbarque, "%d-%m-%Y")
				new_date_obj       = date_obj  # Fecha actual

				if "BYZA" in self.getNombreEmpresa().upper():
					new_date_obj       = date_obj + timedelta(weeks=2)   # 15 días

				location ["fecha"] = new_date_obj.strftime("%d-%m-%Y") + "||LOW"
		except:
			Utils.printException ("Obteniendo información de 'entrega'")

		return location
	#-----------------------------------------------------------
	# Get "transporte" and "pago" conditions
	#-----------------------------------------------------------
	def getCondiciones (self):
		conditions = {'pago':None, 'transporte':None}
		# Condiciones transporte
		try:
			text = self.fields ["09_Condiciones"]["value"]
			if "SIN CAMBIO" in text.upper():
				conditions ["transporte"] = "DIRECTO, SIN CAMBIO DEL CAMION"
			elif "CON CAMBIO" in text.upper():
				conditions ["transporte"] = "DIRECTO, CON CAMBIO DEL TRACTO-CAMION"
			elif "TRANSBORDO" in text.upper():
				conditions ["transporte"] = "TRANSBORDO"
		except:
			Utils.printException ("Extrayendo informacion de condiciones de transporte", text)

		# Condiciones pago
		try:
			if "CREDITO" in text:
				conditions ["pago"] = "POR COBRAR||LOW"
			elif "ANTICIPADO" in text:
				conditions ["pago"] = "PAGO ANTICIPADO||LOW"
			elif "CONTADO" in text:
				conditions ["pago"] = "PAGO ANTICIPADO||LOW"
			else:
				pagoString = Extractor.getDataString ("condiciones_pago.txt", self.resourcesPath)
				rePagos    = rf"\b({pagoString})\b" # RE to find a match string
				pago       = Extractor.getValueRE (rePagos, text)
				conditions ["pago"] = pago if pago else "POR COBRAR||LOW"
		except:
			Utils.printException ("Extrayendo informacion de condiciones de pago en el texto:", text)

		return (conditions)

	#-----------------------------------------------------------
	# Get info from unidades de medida:"peso neto, volumente, otras
	#-----------------------------------------------------------
	def getUnidadesMedidaInfo (self):
		unidades = {"pesoNeto":None, "pesoBruto": None, "volumen":None, "otraUnidad":None}
		try:
			unidades ["pesoNeto"]   = Extractor.getNumber (self.fields ["13a_Peso_Neto"]["value"])
			unidades ["pesoBruto"]  = Extractor.getNumber (self.fields ["13b_Peso_Bruto"]["value"])
			unidades ["volumen"]	  = Extractor.getNumber (self.fields ["14_Volumen"]["value"])
			unidades ["otraUnidad"] = Extractor.getNumber (self.fields ["15_Otras_Unidades"]["value"])

			for k in unidades.keys():
				unidades [k] = Utils.convertToAmericanFormat (unidades [k])
		except:
			Utils.printException ("Obteniendo información de 'Unidades de Medida'")
		return unidades

	#-----------------------------------------------------------
	#-- Get 'total bultos' and 'tipo embalaje' -----------------
	#-----------------------------------------------------------
	def getBultosInfo (self):
		bultosInfo = Utils.createEmptyDic (["cantidad", "embalaje", "marcas", "descripcion"])
		try:
			# Cantidad
			text             = self.fields ["10_CantidadClase_Bultos"]["value"]
			bultosInfo ["cantidad"] = Extractor.getNumber (text)
			bultosInfo ["embalaje"] = Extractor.getTipoEmbalaje (text, self.fieldsJsonFile)

			# Marcas 
			text = self.fields ["11_MarcasNumeros_Bultos"]["value"]
			bultosInfo ["marcas"] = "SIN MARCAS" if text == None else text

			# Descripcion
			descripcion = self.fields ["12_Descripcion_Bultos"]["content"]
			descripcion = self.cleanWaterMark (descripcion)
			bultosInfo ["descripcion"] = self.getMercanciaDescripcion (descripcion)

		except:
			Utils.printException ("Obteniendo información de 'Bultos'", text)

		return bultosInfo

	#--------------------------------------------------------------------
	#-- Search "pais" for "ciudad" in previous document boxes
	#--------------------------------------------------------------------
	def searchPaisPreviousBoxes (self, ciudad, pais):
		try:
			# Search 'pais' in previos boxes
			if (ciudad != None and pais == None):
				if self.ecudoc ["30_CiudadRecepcion"] and ciudad in self.ecudoc ["30_CiudadRecepcion"]:
					pais = self.ecudoc ["29_PaisRecepcion"]
				elif self.ecudoc ["33_CiudadEmbarque"] and ciudad in self.ecudoc ["33_CiudadEmbarque"]:
					pais = self.ecudoc ["32_PaisEmbarque"]
				elif self.ecudoc ["36_CiudadEntrega"] and ciudad in self.ecudoc ["36_CiudadEntrega"]:
					pais = self.ecudoc ["35_PaisEntrega"]

		except:
			Utils.printException ("Obteniendo informacion de 'mercancía'")
		return ciudad, pais

	#-----------------------------------------------------------
	# Get info from 'documentos recibidos remitente'
	#-----------------------------------------------------------
	def getDocsRemitente (self):
		docs = None
		try:
			docs = self.fields ["18_Documentos"]["value"]
		except:
			Utils.printException("Obteniendo valores 'DocsRemitente'")
		return docs

	#-----------------------------------------------------------
	#-- Get instrucciones y observaciones ----------------------
	#-----------------------------------------------------------
	def getInstruccionesObservaciones (self):
		instObs = {"instrucciones":None, "observaciones":None}
		try:
			instObs ["instrucciones"] = self.fields ["21_Instrucciones"]["content"]
			instObs ["observaciones"] = self.fields ["22_Observaciones"]["content"]
		except:
			Utils.printException ("Obteniendo informacion de 'Instrucciones y Observaciones'")
		return instObs

	#-----------------------------------------------------------
	# Get 'gastos' info: monto, moneda, otros gastos
	#-----------------------------------------------------------
	def getGastosInfo (self):
		gastos = {"fleteRemi":None, "monedaRemi":None,       "fleteDest":None,       "monedaDest":None,
			"otrosGastosRemi":None, "otrosMonedaRemi":None, "otrosGastosDest":None, "otrosMonedaDest": None,
			"totalGastosRemi":None, "totalMonedaRemi": None, "totalGastosDest":None, "totalMonedaDest":None}
		try:
			tabla = self.fields ["17_Gastos"]["value"]

			# DESTINATARIO:
			USD = "USD"
			gastos ["fleteDest"]	   = self.getValueTablaGastos (tabla, "ValorFlete", "MontoDestinatario")
			gastos ["monedaDest"]      = USD if gastos ["fleteDest"] else None
			gastos ["otrosGastosDest"] = self.getValueTablaGastos (tabla, "OtrosGastos", "MontoDestinatario")
			gastos ["otrosMonedaDest"] = USD if gastos ["otrosGastosDest"] else None
			gastos ["totalGastosDest"] = self.getValueTablaGastos (tabla, "Total", "MontoDestinatario")
			gastos ["totalMonedaDest"] = USD if gastos ["totalGastosDest"] else None

			# REMITENTE: 
			gastos ["fleteRemi"]       = self.getValueTablaGastos (tabla, "ValorFlete", "MontoRemitente")
			gastos ["monedaRemi"]      = USD if gastos ["fleteRemi"] else None
			gastos ["otrosGastosRemi"] = self.getValueTablaGastos (tabla, "OtrosGastos", "MontoRemitente")
			gastos ["otrosMonedaRemi"] = USD if gastos ["otrosGastosRemi"] else None
			gastos ["totalGastosRemi"] = self.getValueTablaGastos (tabla, "Total", "MontoRemitente")
			gastos ["totalMonedaRemi"] = USD if gastos ["totalGastosRemi"] else None

			for k in gastos.keys ():
				if not "moneda" in k.lower ():
					gastos [k] = Utils.convertToAmericanFormat (gastos [k])
		except:
			Utils.printException ("Obteniendo valores de 'gastos'")

		return gastos

	#-- Get value from Cartaporte Gastos table
	def getValueTablaGastos (self, tabla, firstKey, secondKey):
		try:
			text = tabla [firstKey]["value"][secondKey]["value"]
			value = Utils.getNumber (text)
			return value
		except:
			#print (f"Sin valor en '{firstKey}'-'{secondKey}')")
			#printx (traceback_format_exc())
			return None
	#-------------------------------------------------------------------
	#-- For NTA and BYZA:
	#   Get subject info: nombre, dir, pais, ciudad, id, idNro ---------
	#-- BYZA format: <Nombre>\n<Direccion>\n<PaisCiudad><TipoID:ID> -----
	#-------------------------------------------------------------------
	#-- Get subject info: nombre, dir, pais, ciudad, id, idNro
	def getSubjectInfo (self, key):
		subject = {"nombre":None, "direccion":None, "pais": None, 
		           "ciudad":None, "tipoId":None, "numeroId": None}
		try:
			text	= Utils.getValue (self.fields, key)
			lines   = text.split ("\n")

			if len (lines) == 3:
				nameDirLines = lines [0:2]
				idPaisLine   = lines [2]
			elif len (lines) == 4:
				nameDirLines = lines [0:3]
				idPaisLine   = lines [3]
			elif len (lines) < 3:
				print (f">>> Alerta:  Pocas líneas de texto en '{key}' para extraer la información.")
				return subject

			text, subject        = Extractor.removeSubjectId (idPaisLine, subject, key)
			text, subject        = Extractor.removeSubjectCiudadPais (text, subject, self.resourcesPath, key)
			text, subject        = Extractor.removeSubjectCiudadPais (text, subject, self.resourcesPath, key)
			nameDirText          = "\n".join (nameDirLines)
			text, subject        = Extractor.removeSubjectNombreDireccion (nameDirText, subject, key)
			subject ["numeroId"] = Utils.convertToEcuapassId (subject ["numeroId"])
		except:
			Utils.printException (f"Obteniendo datos del sujeto: '{key}' en el texto: '{text}'")

		print ("--text:", text)
		print (subject)
		return (subject)

#	#-- Overwritten: Get value from document field
#	def getDocumentFieldValue (self, docField):
#		if "Gastos" in docField:
#			fieldName	= docField.split (":")[0]
#			rowName		= docField.split (":")[1].split (",")[0]
#			colName		= docField.split (":")[1].split (",")[1]
#			tablaGastos = self.fields [fieldName]["value"]
#			value		= self.getValueTablaGastos (tablaGastos, rowName, colName)
#		else:
#			value		= super ().getDocumentFieldValue (docField)
#			
#		return value
	
#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

