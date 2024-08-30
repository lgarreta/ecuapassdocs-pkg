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
	mainFields = ManifiestoInfo.extractEcuapassFields (fieldsJsonFile, runningDir)
	Utils.saveFields (mainFields, fieldsJsonFile, "Results")

#----------------------------------------------------------
# Class that gets main info from Ecuapass document 
#----------------------------------------------------------
class ManifiestoLogitrans (ManifiestoInfo):
	def __init__(self, fieldsJsonFile, runningDir):
		super().__init__ (fieldsJsonFile, runningDir)

	#-- Get empresa info
	def getEmpresaInfo (self):
		return EcuData.getEmpresaInfo ("LOGITRANS")

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
	
	#-- Try to convert certificado text to valid certificado string
	#-- CR --> CRU
	def formatCertificadoString (self, text, vehicleType):
		certificadoString = super().formatCertificadoString (text, vehicleType)
		certificadoString = certificadoString.replace ("CR-", "CRU-")
		return certificadoString


	#-- None for BYZA 
	def getCargaDescripcion (self):
			return None

	#-- Just "Originario"
	def getPermisosInfo (self):
		info = EcuData.getEmpresaInfo ("LOGITRANS")
		permisos = {"tipoPermisoCI"    : None,
			        "tipoPermisoPEOTP" : None,
			        "tipoPermisoPO"    : "1", 
			        "permisoOriginario": info ["permisos"]["servicios1"],
			        "permisoServicios1": None
				   }
		return permisos

	#-----------------------------------------------------------
	#-- Search for embalaje in alternate ecufield 11
	#-----------------------------------------------------------
	def getBultosInfoManifiesto (self):
		bultosInfo = super ().getBultosInfoManifiesto ()

		if not bultosInfo ["embalaje"] or bultosInfo ["embalaje"] == "||LOW":
			text = self.fields ["31_Mercancia_Embalaje"]["value"]
			embalaje = Extractor.getTipoEmbalaje ("00 " + text)
			bultosInfo ["embalaje"] = embalaje
			bultosInfo ["marcas"] = "S/M" if embalaje else text
		return bultosInfo

	#-----------------------------------------------------------
	# Remove "DIAN" or "SENAE" from aduana text and call super
	#-----------------------------------------------------------
	def getAduanaInfo (self):
		def removePrefix (text):
			return re.sub (r"^(DIAN|SENAE)[^\w]*", "", text, flags=re.IGNORECASE)

		aduanaCruce   = self.fields ["37_Aduana_Cruce"]["content"]
		aduanaDestino = self.fields ["38_Aduana_Destino"]["content"]

		self.fields ["37_Aduana_Cruce"]["content"]   = removePrefix (aduanaCruce)
		self.fields ["38_Aduana_Destino"]["content"] = removePrefix (aduanaDestino)

		return super().getAduanaInfo ()

	#-----------------------------------------------------------
	#-- Get bultos info: cantidad, embalaje, marcas
	#-- Added a number to embalaje to use Extractor
	#-----------------------------------------------------------

	def old_getBultosInfo (self):
		bultos = Utils.createEmptyDic (["cartaporte", "cantidad", "embalaje", "marcas", "descripcion"])
		text = None
		try:
			bultos ["cartaporte"] = self.getNumeroCartaporte ()

			# Cantidad
			text             = self.fields ["30_Mercancia_Bultos"]["value"]
			bultos ["cantidad"] = Extractor.getNumber (text)

			# Embalaje
			text = self.fields ["31_Mercancia_Embalaje"]["value"]
			bultos ["embalaje"] = Extractor.getTipoEmbalaje ("00 " + text)

			# Marcas 
			bultos ["marcas"] = "SIN MARCAS" 

			# Descripcion
			descripcion = self.fields ["29_Mercancia_Descripcion"]["content"]
			descripcion = self.cleanWaterMark (descripcion)
			bultos ["descripcion"] = self.getMercanciaDescripcion (descripcion)
		except:
			Utils.printException ("Obteniendo información de 'Bultos'", text)

		return bultos
	


#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

