#!/usr/bin/env python3

import re, os, json, sys
from traceback import format_exc as traceback_format_exc

from .ecuapass_info import EcuInfo
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
class ManifiestoInfo (EcuInfo):
	def __init__(self, fieldsJsonFile, runningDir):
		super().__init__ ("MANIFIESTO", fieldsJsonFile, runningDir)

	#-- Get data and value from document main fields
	def getMainFields (self):
		Utils.runningDir   = self.runningDir      # Dir to copy and get images and data

		try:
			#print ("\n>>>>>> Identificacion del Transportista Autorizado <<<")
			transportista                         = self.getTransportistaInfo ()
			self.ecudoc ["01_Tipo_Procedimiento"] = transportista ["procedimiento"]
			self.ecudoc ["02_Sector"]             = transportista ["sector"]
			self.ecudoc ["03_Fecha_Emision"]      = transportista ["fechaEmision"]
			self.ecudoc ["04_Distrito"]           = transportista ["distrito"]
			self.ecudoc ["05_MCI"]                = transportista ["MCI"]
			self.ecudoc ["06_Empresa"]            = transportista ["empresa"]

			#print ("\n>>> Identificación Permisos")
			permisos                              = self.getPermisosInfo ()
			self.ecudoc ["07_TipoPermiso_CI"]     = permisos ["tipoPermisoCI"]
			self.ecudoc ["08_TipoPermiso_PEOTP"]  = permisos ["tipoPermisoPEOTP"]
			self.ecudoc ["09_TipoPermiso_PO"]     = permisos ["tipoPermisoPO"]
			self.ecudoc ["10_PermisoOriginario"]  = permisos ["permisoOriginario"]
			self.ecudoc ["11_PermisoServicios1"]  = permisos ["permisoServicios"]
			self.ecudoc ["12_PermisoServicios2"]   = None
			self.ecudoc ["13_PermisoServicios3"]   = None
			self.ecudoc ["14_PermisoServicios4"]   = None

			# Empresa
			self.ecudoc ["15_NombreTransportista"] = self.getNombreEmpresa ()
			self.ecudoc ["16_DirTransportista"]    = self.getDireccionEmpresa ()

			#print ("\n>>>>>> Identificacion de la Unidad de Carga (Remolque) <<<")
			remolque                             = self.getRemolqueInfo ()
			self.ecudoc ["24_Marca_remolque"]    = remolque ["marca"]
			self.ecudoc ["25_Ano_Fabricacion"]   = remolque ["anho"]
			self.ecudoc ["26_Placa_remolque"]    = remolque ["placa"]
			self.ecudoc ["27_Pais_remolque"]     = remolque ["pais"]
			self.ecudoc ["28_Nro_Certificado"]   = remolque ["certificado"]
			self.ecudoc ["29_Otra_Unidad"]       = remolque ["tipo"]

			#print ("\n>>>>>> Identificacion del Vehículo Habilitado <<<")
			vehiculo                             = self.getVehiculoInfo (remolque)
			self.ecudoc ["17_Marca_Vehiculo"]    = vehiculo ["marca"]
			self.ecudoc ["18_Ano_Fabricacion"]   = vehiculo ["anho"]
			self.ecudoc ["19_Pais_Vehiculo"]     = vehiculo ["pais"]
			self.ecudoc ["20_Placa_Vehiculo"]    = vehiculo ["placa"]
			self.ecudoc ["21_Nro_Chasis"]        = vehiculo ["chasis"]
			self.ecudoc ["22_Nro_Certificado"]   = vehiculo ["certificado"]
			self.ecudoc ["23_Tipo_Vehiculo"]     = vehiculo ["tipo"]

			#print ("\n>>>>>> Identificacion de la Tripulacion <<<")
			conductor                             = self.getConductorInfo ()
			self.ecudoc ["30_Pais_Conductor"]     = conductor ["pais"]
			self.ecudoc ["31_TipoId_Conductor"]   = conductor ["tipoId"]
			self.ecudoc ["32_Id_Conductor"]       = conductor ["id"]
			self.ecudoc ["33_Sexo_Conductor"]     = conductor ["sexo"]
			self.ecudoc ["34_Fecha_Conductor"]    = conductor ["fechaNacimiento"]
			self.ecudoc ["35_Nombre_Conductor"]   = conductor ["nombre"]
			self.ecudoc ["36_Licencia_Conductor"] = conductor ["licencia"]
			self.ecudoc ["37_Libreta_Conductor"]  = None

			# Auxiliar
			self.ecudoc ["38_Pais_Auxiliar"]     = None
			self.ecudoc ["39_TipoId_Auxiliar"]   = None
			self.ecudoc ["40_Id_Auxiliar"]       = None
			self.ecudoc ["41_Sexo_Auxiliar"]     = None
			self.ecudoc ["42_Fecha_Auxiliar"]    = None
			self.ecudoc ["43_Nombre_Auxiliar"]   = None
			self.ecudoc ["44_Apellido_Auxiliar"] = None
			self.ecudoc ["45_Licencia_Auxiliar"] = None
			self.ecudoc ["46_Libreta_Auxiliar"]  = None

			#print ("\n>>>>>> Datos sobre la carga <<<")
			text                                 = Utils.getValue (self.fields, "23_Carga_CiudadPais")
			embarque                             = Extractor.extractCiudadPais (text, self.resourcesPath)
			self.ecudoc ["47_Pais_Carga"]        = Utils.checkLow (embarque ["pais"])
			self.ecudoc ["48_Ciudad_Carga"]      = Utils.checkLow (embarque ["ciudad"])

			text                                 = Utils.getValue (self.fields, "24_Descarga_CiudadPais")
			descarga                             = Extractor.extractCiudadPais (text, self.resourcesPath)
			self.ecudoc ["49_Pais_Descarga"]     = Utils.checkLow (descarga ["pais"])
			self.ecudoc ["50_Ciudad_Descarga"]   = Utils.checkLow (descarga ["ciudad"])

			cargaInfo                            = self.getCargaInfo ()
			self.ecudoc ["51_Tipo_Carga"]        = cargaInfo ["tipo"]
			self.ecudoc ["52_Descripcion_Carga"] = cargaInfo ["descripcion"]

			#print ("\n>>>>>> Datos sobre la mercancia (Incoterm) <<<")
			text                                 = Utils.getValue (self.fields, "34_Precio_Incoterm_Moneda")
			incoterm                             = self.getIncotermInfo (text)
			self.ecudoc ["53_Precio_Mercancias"] = incoterm ["precio"]
			self.ecudoc ["54_Incoterm"]          = incoterm ["incoterm"]
			self.ecudoc ["55_Moneda"]            = incoterm ["moneda"]
			self.ecudoc ["56_Pais_Moneda"]       = incoterm ["pais"]
			self.ecudoc ["57_Ciudad_Moneda"]     = incoterm ["ciudad"]

			#print ("\n>>>>>> Datos de las aduanas <<<")
			aduana                                = self.getAduanaInfo ()
			self.ecudoc ["58_AduanaDest_Pais"]    = aduana ["paisDestino"]
			self.ecudoc ["59_AduanaDest_Ciudad"]  = aduana ["ciudadDestino"]

			#print ("\n>>>>>> Datos sobre las unidades) <<<")
			unidades = self.getUnidadesMedidaInfo ()
			self.ecudoc ["60_Peso_NetoTotal"]     = unidades ["pesoNetoTotal"]
			self.ecudoc ["61_Peso_BrutoTotal"]    = unidades ["pesoBrutoTotal"]
			self.ecudoc ["62_Volumen"]            = None
			self.ecudoc ["63_OtraUnidad"]         = unidades ["otraUnidadTotal"]

			## Aduana Cruce
			self.ecudoc ["64_AduanaCruce_Pais"]   = aduana ["paisCruce"]
			self.ecudoc ["65_AduanaCruce_Ciudad"] = aduana ["ciudadCruce"]

			#print ("\n>>>>>> Detalles finales <<<")
			self.ecudoc ["66_Secuencia"]         = Utils.addLow (self.getSecuencia ())
			self.ecudoc ["67_MRN"]               = Utils.addLow (self.getMRN ())
			self.ecudoc ["68_MSN"]               = Utils.addLow (self.getMSN ())

			bultos                         = self.getBultosInfo ()
			self.ecudoc ["69_CPIC"]        = Utils.checkLow (bultos ["cartaporte"])
			self.ecudoc ["70_TotalBultos"] = Utils.checkLow (bultos ["cantidad"])
			self.ecudoc ["71_Embalaje"]	   = Utils.addLow (bultos ["embalaje"])
			self.ecudoc ["72_Marcas"]      = Utils.checkLow (bultos ["marcas"])

			# Unidades
			self.ecudoc ["73_Peso_Neto"]        = unidades ["pesoNetoTotal"]
			self.ecudoc ["74_Peso_Bruto"]       = unidades ["pesoBrutoTotal"]
			self.ecudoc ["75_Volumen"]          = None
			self.ecudoc ["76_OtraUnidad"]       = unidades ["otraUnidadTotal"]

			#print ("\n>>>>>> Detalles finales <<<")
			self.ecudoc ["77_Nro_UnidadCarga"]  = None
			self.ecudoc ["78_Tipo_UnidadCarga"] = None
			self.ecudoc ["79_Cond_UnidadCarga"] = None
			self.ecudoc ["80_Tara"]             = None
			self.ecudoc ["81_Descripcion"]      = bultos ['descripcion']
			self.ecudoc ["82_Precinto"]         = Utils.getValue (self.fields, "27_Carga_Precintos")

		except:
			Utils.printx (f"ALERTA: Problemas extrayendo información del documento '{self.fieldsJsonFile}'")
			Utils.printx (traceback_format_exc())
			raise

		#self.printFieldsValues (self.ecudoc)
		#self.updateFields ()
		return (self.ecudoc)

	#------------------------------------------------------------------
	#-- Updated document fields with processed ecufields
	#------------------------------------------------------------------
	def updateFields (self):
		# 01a 01b Transportista to 01_Transportista
		#transpInfo = "%s\n%s" % (self.fields ["01a_Transportista_Nombre"]["value"],
        #                                self.fields ["01b_Transportista_Id"]["value"])
		#del self.fields ["01a_Transportista_Nombre"]
		#del self.fields ["01b_Transportista_Id"]
		#self.fields ["01_Transportista"] = {"content":transpInfo, "value":transpInfo}

		## 28_Mercancia_Cartaporte to 28_Cartaporte
		#cartaporte = self.fields ["28_Mercancia_Cartaporte"]
		#self.fields ["28_Cartaporte"] = {"content" : cartaporte["content"], "value": cartaporte["value"]}
		#del self.fields ["28_Mercancia_Cartaporte"]

		## 29_Mercancia_Descripcion to 28_Descripcion
		#descripcion = self.fields ["29_Mercancia_Descripcion"]
		#self.fields ["29_Descripcion"] = {"content" : descripcion["content"], "value": descripcion["value"]}
		#del self.fields ["29_Mercancia_Descripcion"]

		## 30_Mercancia_Bultos to 30_Cantidad_Bultos
		#old, new = "30_Mercancia_Bultos", "30_Cantidad_Bultos"
		#info = self.fields [old]
		#self.fields [new] = {"content" : info ["content"], "value": info ["value"]}
		#del self.fields [old]

		## 29_Mercancia_Descripcion to 28_Descripcion
		#old, new = "31_Mercancia_Embalaje", "31_Marca_Bultos"
		#info = self.fields [old]
		#self.fields [new] = {"content" : info ["content"], "value": info ["value"]}
		#del self.fields [old]

		return self.fields

		
	#------------------------------------------------------------------
	# Transportista information 
	#------------------------------------------------------------------
	def getTransportistaInfo (self):
		transportista = Utils.createEmptyDic (["procedimiento", "sector", "fechaEmision", "distrito", "MCI", "empresa"])
		try:	
			transportista ["procedimiento"]     = self.getTipoProcedimiento ()
			transportista ["sector"]            = "NORMAL||LOW"

			text                                = Utils.getValue (self.fields, "40_Fecha_Emision")
			transportista ["fechaEmision"]      = Extractor.getDate (text, self.resourcesPath)
			transportista ["distrito"]          = "TULCAN||LOW"
			transportista ["MCI"]               = self.getNumeroDocumento ()
			transportista ["empresa"]           = None    # Bot select the only first one
		except:
			Utils.printException ("Obteniendo información del transportista")
		return (transportista)

	#------------------------------------------------------------------
	# Permisos info
	#------------------------------------------------------------------
	def getPermisosInfo (self):
		permisos = Utils.createEmptyDic (["tipoPermisoCI", "tipoPermisoPEOTP", "tipoPermisoPO", "permisoOriginario", "permisoServicios"])
		try:
			permisos ["permisoOriginario"] = self.getPermiso_PerEmpresa ("ORIGINARIO")
			permisos ["permisoServicios"]  = self.getPermiso_PerEmpresa ("SERVICIOS")
			#permisos ["permisoOriginario"] = self.getPermiso ("02_Permiso_Originario")
			#permisos ["permisoServicios"]  = self.getPermiso ("03_Permiso_Servicios").replace ("-","")

			tipoPermiso = permisos ["permisoOriginario"].split ("-")[0]
			tipoPermiso = re.sub (r"[^A-Za-z0-9]+", "", tipoPermiso).upper()  # re for removing symbols
			if (tipoPermiso == "CI"):
				permisos ["tipoPermisoCI"]     = "1"
			elif (tipoPermiso == "POETP"):
				permisos ["tipoPermisoPOETP"]  = "1"
			elif (tipoPermiso == "PO"):
				permisos ["tipoPermisoPO"]     = "1"
			else:
				Utils.printException (f"Tipo permiso desconocido en el texto: '{text}'")
		except:
			Utils.printException ("Obteniendo información del permisos")

		return (permisos)

	#------------------------------------------------------------------
	# 'Servicios" permission is None for BYZA
	#------------------------------------------------------------------
	def getPermiso_PerEmpresa (self, tipoPermiso):
		outPermiso = None
		#----------------------------------------------------------
		def getPermiso (key):
			"""May contain one or two numbers. First is returned"""
			permiso = Utils.getValue (self.fields, key)
			return permiso.split ("\n")[0]
		#----------------------------------------------------
		if tipoPermiso == "ORIGINARIO":
			outPermiso =  getPermiso ("02_Permiso_Originario")
		elif tipoPermiso == "SERVICIOS":
			if self.nombreEmpresa == "BYZA":
				outPermiso = None
			else:
				outPermiso = getPermiso ("03_Permiso_Servicios").replace ("-","")

		return outPermiso
		
	#------------------------------------------------------------------
	# Vehiculo/Remolque information 
	#------------------------------------------------------------------
	def getValidValue (self, value):
		if value == None:
			return None
		elif value.upper().startswith ("XX") or value.upper () == "N/A" or value is None:
			return None
		else: 
			return value

	#------------------------------------------------------------------
	# Vehiculo/Remolque information 
	#------------------------------------------------------------------
	def getVehiculoInfo (self, remolque):
		keys = {"marca":"04_Camion_Marca", "anho":"05_Camion_AnoFabricacion", 
		        "placaPais":"06_Camion_PlacaPais", "chasis":"07_Camion_Chasis", 
				"certificado":"08_Certificado_Habilitacion"}
		vehiculo = {key:None for key in ["marca","anho","pais","placa","chasis","certificado","tipo"]}
		try:
			vehiculo ["marca"]       = self.getValidValue (Utils.getValue (self.fields, keys ["marca"]))
			vehiculo ["anho"]        = self.getValidValue (Utils.getValue (self.fields, keys ["anho"]))
			placaPaisText            = self.getValidValue (Utils.getValue (self.fields, keys ["placaPais"]))
			if placaPaisText:
				placaPais            = Extractor.getPlacaPais (placaPaisText) if placaPaisText else None
				vehiculo ["pais"]    = self.getValidValue (placaPais ["pais"])
				vehiculo ["placa"]   = self.getValidValue (placaPais ["placa"])
			vehiculo ["chasis"]      = self.getValidValue (Utils.getValue (self.fields, keys ["chasis"]))
			vehiculo ["certificado"] = self.getCheckCertificadoVehiculo (keys ["certificado"])
			vehiculo ["tipo"]        = self.getTipoVehiculo ("VEHICULO", remolque)
		except Exception as e:
			Utils.printException (f"Extrayendo información del vehículo", e)
		return vehiculo

	#------------------------------------------------------------------
	# Vehiculo/Remolque information 
	#------------------------------------------------------------------
	def getRemolqueInfo (self):
		keys = {"marca":"09_Remolque_Marca", "anho":"10_Remolque_AnoFabricacion",
		        "placaPais":"11_Remolque_PlacaPais", "chasis": "12_Remolque_Otro", 
				"certificado": "08_Certificado_Habilitacion"}
		vehiculo = {key:None for key in ["marca","anho","pais","placa","chasis","certificado","tipo"]}
		try:
			vehiculo ["marca"]       = self.getValidValue (Utils.getValue (self.fields, keys ["marca"]))
			vehiculo ["anho"]        = self.getValidValue (Utils.getValue (self.fields, keys ["anho"]))
			placaPaisText            = self.getValidValue (Utils.getValue (self.fields, keys ["placaPais"]))
			if placaPaisText:
				placaPais            = Extractor.getPlacaPais (placaPaisText) if placaPaisText else None
				vehiculo ["pais"]    = self.getValidValue (placaPais ["pais"])
				vehiculo ["placa"]   = self.getValidValue (placaPais ["placa"])
			vehiculo ["chasis"]      = self.getValidValue (Utils.getValue (self.fields, keys ["chasis"]))
			vehiculo ["certificado"] = self.getCheckCertificadoRemolque (keys ["certificado"])
			vehiculo ["tipo"]        = self.getTipoVehiculo ("REMOLQUE", vehiculo)
		except Exception as e:
			Utils.printException (f"Extrayendo información del vehículo", e)
		return vehiculo


	#-- Overwriten in subclases: Get tipo vehículo 
	def getTipoVehiculo  (self, tipo, remolque=None):
		if tipo == "VEHICULO": 
			return "TRACTOCAMION"
		elif tipo == "REMOLQUE": 
			return "SEMIREMOLQUE"
		else:
			return NONE

	#-- Return certificadoString if it is valid (e.g. CH-CO-XXXX-YY, RUC-CO-XXX-YY), else None
	def getCheckCertificadoVehiculo (self, key):
		return self.getCheckCertificado (key, "VEHICULO")

	def getCheckCertificadoRemolque (self, key):
		return self.getCheckCertificado (key, "REMOLQUE")

	def getCheckCertificado (self, key, vehicleType):
		try:
			textCertificado  = Utils.getValue (self.fields, key)
			if vehicleType == "VEHICULO":
				text    = Extractor.getFirstString (textCertificado)
				pattern = re.compile (r'^CH-(CO|EC)-\d{4,5}-\d{2}')
			elif vehicleType == "REMOLQUE":
				text    = Extractor.getLastString (textCertificado)
				pattern = re.compile (r'^(CRU|CR)-(CO|EC)-\d{4,5}-\d{2}')

			if (text == None):
				return "||LOW"

			certificadoString = self.formatCertificadoString (text, vehicleType)
			if bool (pattern.match (certificadoString)) == False:
				Utils.printx (f"Error validando certificado de <{vehicleType}> en texto: '{certificadoString}'")
				certificadoString = "||LOW"
		except:
			Utils.printException (f"Obteniendo/Verificando certificado '{certificadoString}' para '{vehicleType}'")

		return certificadoString;

	#-- Try to convert certificado text to valid certificado string
	def formatCertificadoString (self, text, vehicleType):
		try:
			if (text in [None, ""]):
				return None

			text = text.replace ("-","") 
			text = text.replace (".", "") 
 
			if vehicleType == "VEHICULO":
				first  = text [0:2]; text = text [2:]   # CH
			elif vehicleType == "REMOLQUE":
				if text [0:3] == "CRU":
					first  = "CRU"; text = text [3:]   # CRU
				elif text [0:2] == "CR":
					first  = "CR"; text = text [2:]   # CR

			second = text [0:2]; text = text [2:]       # CO|EC
			last   = text [-2:]; text = text [:-2]      # 23|23|XX
			middle = text                               # XXXX|YYYYY

			certificadoString = f"{first}-{second}-{middle}-{last}"
		except:
			Utils.printException (f"Excepción formateando certificado para '{vehicleType}' desde el texto '{text}'")
			certificadoString = ""

		return certificadoString
		

	def is_valid_colombian_value(value_str):
		# Use regular expression to check if the input value matches the Colombian format
		pattern = re.compile(r'^\d{1,3}(\.\d{3})*(,\d{1,2})?')
		return bool(pattern.match (value_str))

	def is_valid_american_value(value_str):
		# Use regular expression to check if the input value matches the American format
		pattern1 = re.compile(r'^\d{1,3}(,\d{3})*(\.\d{1,2})?$')
		pattern2 = re.compile(r'^\d{3,}(\.\d{1,2})?$')
		return bool (pattern1.match(value_str) or pattern2.match (value_str))

	def convertToAmericanFormat (value_str):
		if value_str == None:
			return value_str
		
	#------------------------------------------------------------------
	# Conductor/Auxiliar informacion
	#------------------------------------------------------------------
	def getConductorInfo (self):
		conductor = Utils.createEmptyDic (["pais", "tipoId", "id", "sexo", "fechaNacimiento", "nombre", "licencia"])
		try:
			conductor ["pais"]            = Extractor.getPaisFromSubstring (Utils.getValue (self.fields, "15_Conductor_Nacionalidad"))  
			conductor ["tipoId"]          = "CEDULA DE IDENTIDAD"
			conductor ["id"]              = Utils.getValue (self.fields, "14_Conductor_Id")
			conductor ["sexo"]            = "Hombre"

			text                          = Utils.getValue (self.fields, "13_Conductor_Nombre")
			fechaNacimiento               = Extractor.getDate (text, self.resourcesPath)
			conductor ["fechaNacimiento"] = fechaNacimiento if fechaNacimiento else "06-01-1985"
			conductor ["nombre"]          = Extractor.extractNames (text)
			conductor ["licencia"]        = Utils.getValue (self.fields, "16_Conductor_Licencia")
		except:
			Utils.printException ("Obteniendo informacion del conductor")
		return conductor

	#------------------------------------------------------------------
	# Info carga: type and descripcion
	#------------------------------------------------------------------
	def getCargaInfo (self):
		info = {"tipo": None, "descripcion": None}
		try:
			info ["tipo"]           = "CARGA SUELTA||LOW"
			info ["descripcion"]    = self.getCargaDescripcion ()
		except:
			Utils.printException ("Obteniendo inforamcion de la carga en texto:")
		return info

	#-- Overwritten in companies (BYZA:None)
	def getCargaDescripcion (self):
		return Utils.getValue (self.fields, "25e_Carga_TipoDescripcion")

	#--------------------------------------------------------------------
	#-- Search "pais" for "ciudad" in previous document boxes
	#--------------------------------------------------------------------
	def searchPaisPreviousBoxes (self, ciudad, pais):
		try:
			if (ciudad != None and pais == None):
				if self.ecudoc ["48_Ciudad_Carga"] and ciudad in self.ecudoc ["48_Ciudad_Carga"]:
					pais	 = self.ecudoc ["47_Pais_Carga"]
				elif self.ecudoc ["50_Ciudad_Descarga"] and ciudad in self.ecudoc ["50_Ciudad_Descarga"]:
					pais	 = self.ecudoc ["49_Pais_Descarga"]

		except Exception as e:
			Utils.printException (f"Obteniendo informacion de 'mercancía' en texto: '{text}'", e)
		return ciudad, pais

	#-----------------------------------------------------------
	# Get info from unidades de medida:"peso neto, volumente, otras
	#-----------------------------------------------------------
	def getUnidadesMedidaInfo (self):
		info = {"pesoNetoTotal":None, "pesoBrutoTotal":None, "otraUnidadTotal":None}
		try:
			info ["pesoBrutoTotal"]  = Extractor.getNumber (self.fields ["32a_Peso_BrutoTotal"]["value"])
			info ["pesoNetoTotal"]   = Extractor.getNumber (self.fields ["32b_Peso_NetoTotal"]["value"])
			info ["otraUnidadTotal"] = Extractor.getNumber (self.fields ["33_Otra_MedidaTotal"]["value"])
		except:
			Utils.printException ("Obteniendo información de 'Unidades de Medida'")
		return info

	#--------------------------------------------------------------------
	# Aduana info: extract ciudad and pais for "cruce" and "destino" aduanas
	#--------------------------------------------------------------------
	def getAduanaInfo (self):
		info = Utils.createEmptyDic (["paisCruce", "ciudadCruce", "paisDestino", "ciudadDestino"])
		text = ""
		try:
			reWithSeparador = r'(\b\w+[\s\w]*\b)\s*?[-.,]?\s*(\w+)'
			reWithParentesis = r'(\b\w+[\s\w]*\b)\s*?\s*[(](\w+)[)]'

			aduanas = {}
			aduanas ["37_Aduana_Cruce"]   = {"ciudad":"ciudadCruce", "pais": "paisCruce"}
			aduanas ["38_Aduana_Destino"] = {"ciudad":"ciudadDestino", "pais": "paisDestino"}

			for key in ["37_Aduana_Cruce", "38_Aduana_Destino"]:
				text = Utils.getValue (self.fields, key)
				results = [re.search (x, text) for x in [reWithSeparador, reWithParentesis]]

				if results [0] or results [1]:
					result = results [0] if results [0] else results [1]
					info [aduanas [key]["ciudad"]] = result.group (1).strip()
					pais = result.group (2)
					info [aduanas [key]["pais"]] = Extractor.getPaisFromSubstring (pais).strip()

		except Exception as e:
			Utils.printException (f"Extrayendo pais-ciudad desde aduanas en texto: '{text}'", e)
		return info

	#------------------------------------------------------------------
	# Secuencia, MRN, MSN, NumeroCPIC for BOTERO-SOTO
	#------------------------------------------------------------------
	def getSecuencia (self):
		return "1"

	def getMRN (self):
		text = Utils.getValue (self.fields, "29_Mercancia_Descripcion")
		MRN  = Extractor.getMRN (text)
		return MRN

	def getMSN (self):
		return "0001" + "||LOW"

	def getNumeroCartaporte (self):
		text   = Utils.getValue (self.fields, "28_Mercancia_Cartaporte")
		text   = text.replace ("\n", "")
		numero = Extractor.getNumeroDocumento (text)
		return numero

	#-----------------------------------------------------------
	#-- Get bultos info: cantidad, embalaje, marcas
	#-----------------------------------------------------------
	def getBultosInfo (self):
		bultos = Utils.createEmptyDic (["cartaporte", "cantidad", "embalaje", "marcas", "descripcion"])
		text = None
		try:
			bultos ["cartaporte"] = self.getNumeroCartaporte ()

			# Cantidad
			text             = self.fields ["30_Mercancia_Bultos"]["value"]
			bultos ["cantidad"] = Extractor.getNumber (text)
			bultos ["embalaje"] = Extractor.getTipoEmbalaje (text, self.resourcesPath)

			# Marcas 
			text = self.fields ["31_Mercancia_Embalaje"]["value"]
			bultos ["marcas"] = "SIN MARCAS" if text == None else text

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


#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()

