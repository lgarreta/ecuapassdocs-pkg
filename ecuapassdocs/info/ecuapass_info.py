
import os, json, re

from ecuapassdocs.info.resourceloader import ResourceLoader 

from .ecuapass_data import EcuData
from .ecuapass_extractor import Extractor
from .ecuapass_utils import Utils

# Base class for all info document clases: CartaporteInfo (CPI), ManifiestoInfo (MCI), EcuDCL (DTAI)
class EcuInfo:

	def __init__ (self, docType, fieldsJsonFile, runningDir):
		self.docType        = docType
		self.inputsParametersFile = Utils.getInputsParametersFile (docType)

		self.fieldsJsonFile = fieldsJsonFile
		self.runningDir     = runningDir

		self.empresa        = self.getEmpresaInfo ()   # Overwritten per 'empresa'
		#self.nombreEmpresa  = self.empresa ["id"]

		self.resourcesPath  = os.path.join (runningDir, "resources", "data_cartaportes") 
		self.fields         = json.load (open (fieldsJsonFile))
		#self.fields ["jsonFile"]  = fieldsJsonFile
		self.ecudoc         = {}

	#-- Implemented in subclasses
	def getEmpresaInfo (self):
		return None

	#-- Updated Ecuapass document fields with values ready to transmit
	#-- Change names to codes for additional presition
	def updateEcuapassFile (self, ecuJsonFile):
		print ("-- Updating Ecuapass fields...")
		ecudoc = json.load (open (ecuJsonFile))
		for key in ecudoc:
			if ecudoc [key] is None:
				continue

			# Vehiculo
			if "Tipo_Vehiculo" in key:
				vehiculos    = {"SEMIRREMOLQUE":"SR", "TRACTOCAMION":"TC", "CAMION":"CA"}
				ecudoc [key] = vehiculos [ecudoc[key]]

			# Embalaje
			if "Embalaje" in key: 
				embalaje = ecudoc [key].upper()
				if "PALLETS" in embalaje:
					embalaje = "152" # "[152] PALETAS"
				elif "SACO" in embalaje:
					embalaje = "104" # "[104] SACO"
				elif "CAJA" in embalaje:
					embalaje = "035" # "[035] CAJA"
				ecudoc [key] = embalaje

			# Moneda
			if "Moneda" in key:
				ecudoc [key] = "USD"

			# Remove confidence string ("||LOW")
			value        = ecudoc [key] 
			value        = value.split ("||")[0] if value else None
			ecudoc [key] = value if value != "" else None

		ecuJsonFileUpd = Utils.saveFields (ecudoc, ecuJsonFile, "UPDATE")
		return ecudoc


	#-- For all types of documents (fixed fro NTA and BYZA, check the others)
	def getNumeroDocumento (self):
		text   = Utils.getValue (self.fields, "00b_Numero")
		numero = Extractor.getNumeroDocumento (text)

		codigo = self.getCodigoPais (numero)
		self.fields ["00_Pais"] = {"value":codigo, "content":codigo}
		return numero

	#-- Returns the first two letters from document number
	def getCodigoPais (self, numero):
		try:
			if numero.startswith ("CO"): 
				return "CO"
			elif numero.startswith ("EC"): 
				return "EC"
		except:
			print (f"ALERTA: No se pudo determinar código del pais desde el número: '{numero}'")
		return ""

	#-- Return updated PDF document fields
	def getDocFields (self):
		return self.fields

	#-- Get id (short name)
	def getIdEmpresa (self):
		return self.empresa ["id"]

	#-- Get data and value from document main fields"""
	def getNombreEmpresa (self):
		return self.empresa ["nombre"]

	def getDireccionEmpresa (self):
		return self.empresa ["direccion"]

	#-----------------------------------------------------------
	#-- Return IMPORTACION or EXPORTACION
	#-----------------------------------------------------------
	def getTipoProcedimiento (self):
		tipoProcedimiento = None
		#procedimientosNTA   = {"CO":"EXPORTACION", "EC":"IMPORTACION"}
		procedimientosBYZA  = {"CO":"IMPORTACION", "EC":"EXPORTACION"}
		procedimientosNTA   = procedimientosBYZA

		try:
			if self.empresa ["id"] == "NTA":
				procedimientos = procedimientosNTA
			elif self.empresa ["id"] == "BYZA":
				procedimientos = procedimientosBYZA

			numero            = self.getNumeroDocumento ()
			codigoPais        = self.getCodigoPais (numero)
			tipoProcedimiento = procedimientos [codigoPais]
		except:
			Utils.printException ("No se pudo determinar tipo de procedimiento (Importación/Exportación)")
			tipoProcedimiento = "IMPORTACION||LOW"

		return tipoProcedimiento

	#-----------------------------------------------------------
	# Get info from mercancia: INCONTERM, Ciudad, Precio, Tipo Moneda
	#-----------------------------------------------------------
	def getIncotermInfo (self, text):
		info = {"incoterm":None, "precio":None, "moneda":None, "pais":None, "ciudad":None}

		try:
			text = text.replace ("\n", " ")

			# Precio
			text, precio    = Extractor.getRemoveNumber (text)
			info ["precio"] = Utils.checkLow (Utils.convertToAmericanFormat (precio))
			text = text.replace (precio, "") if precio else text

			# Incoterm
			termsString = Extractor.getDataString ("tipos_incoterm.txt", 
			                                        self.resourcesPath, From="keys")
			reTerms = rf"\b({termsString})\b" # RE for incoterm
			incoterm = Utils.getValueRE (reTerms, text)
			info ["incoterm"] = Utils.checkLow (incoterm)
			text = text.replace (incoterm, "") if incoterm else text

			# Moneda
			info ["moneda"] = "USD"
			text = text.replace ("USD", "")
			text = text.replace ("$", "")

			# Get ciudad from text and Search 'pais' in previos boxes
			ciudadPais   = Extractor.extractCiudadPais (text, self.resourcesPath) 
			ciudad, pais = ciudadPais ["ciudad"], ciudadPais ["pais"]

			info ["ciudad"], info ["pais"] = self.searchPaisPreviousBoxes (ciudad, pais)
			if not info ["pais"]:
				info ["pais"]   = Utils.checkLow (info["pais"])
				info ["ciudad"] = Utils.addLow (info ["ciudad"])
			elif info ["pais"] and not info ["ciudad"]:
				info ["ciudad"] = Utils.addLow (info ["ciudad"])

		except:
			Utils.printException ("Obteniendo informacion de 'mercancía'")

		return info

	#-----------------------------------------------------------
	# Clean watermark: depending for each "company" class
	#-----------------------------------------------------------
	def cleanWaterMark (self, text):
		if self.empresa ['id'] == "NTA":
			w1, w2, w3, w4 = "N\.T\.A\.", "CIA\.", "LTDA.", "N\.I\.A\."
			expression = rf'(?:{w1}\s+{w2}\s+{w3}|{w2}\s+{w3}\s+{w1}|{w3}\s+{w1}\s+{w2}|{w4}\s+{w2}\s+{w3}|{w2}\s+{w3}\s+{w4}|{w3}\s+{w4}\s+{w2}|{w1}\s+{w2}\s+{w3}|{w2}\s+{w3}\s+{w1}|{w3}\s+{w1}\s+{w2}|{w4}\s+{w2}\s+{w3}|{w2}\s+{w3}\s+{w4}|{w3}\s+{w4}\s+{w2})'

		elif self.empresa ['id'] == 'BYZA':
			expression = r"(Byza)|(By\s*za\s*soluciones\s*(que\s*)*facilitan\s*tu\s*vida)"
		else:
			return text

		pattern = re.compile (expression)
		text = re.sub (pattern, '', text)

		return text.strip()

	#-----------------------------------------------------------
	#-- Extract only the needed info from text for each 'empresa'
	#-----------------------------------------------------------
	def getMercanciaDescripcion (self, descripcion):
		if self.empresa ['id'] == "BYZA":
			if self.docType == "CARTAPORTE":   # Before "---" or CEC##### or "\n"
				pattern = r'((---+|CEC|\n\n).*)$'
				descripcion = re.sub (pattern, "", descripcion, flags=re.DOTALL)

			elif self.docType == "MANIFIESTO": # Before "---" or CPI: ###-###
				pattern = r'((---+|CPI:|CPIC:|\n\n).*)$'
				descripcion = re.sub (pattern, "", descripcion, flags=re.DOTALL)

		return descripcion.strip()

	#----------------------------------------------------------------
	#-- Create CODEBIN fields from document fields using input parameters
	#----------------------------------------------------------------
	def getCodebinFields (self):
		try:
			inputsParams = ResourceLoader.loadJson ("docs", self.inputsParametersFile)
			codebinFields = {}
			for key in inputsParams:
				ecudocsField  = inputsParams [key]["ecudocsField"]
				codebinField  = inputsParams [key]["codebinField"]
				#print ("-- key:", key, " dfield:", ecudocsField, "cfield: ", codebinField)
				if codebinField:
					value = self.getDocumentFieldValue (ecudocsField, "CODEBIN")
					codebinFields [codebinField] = value

			return codebinFields
		except Exception as e:
			Utils.printException ("Creando campos de CODEBIN")
			return None

	#----------------------------------------------------------------
	#-- Create ECUAPASSDOCS fields from document fields using input parameters
	#----------------------------------------------------------------
	def getEcuapassdocsFields (self):
		try:
			inputsParams = ResourceLoader.loadJson ("docs", self.inputsParametersFile)
			docFieldsAll = {}
			for key in inputsParams:
				docField   = inputsParams [key]["ecudocsField"]
				if docField == "" or "OriginalCopia" in docField:
					continue
				else:
					value = self.getDocumentFieldValue (docField)
					docFieldsAll [key] = value

			return docFieldsAll
		except Exception as e:
			Utils.printException ("Creando campos de ECUAPASSDOCS")
			return None

	#-----------------------------------------------------------
	# Implemented for each class: get the document field value
	#-----------------------------------------------------------
	def getDocumentFieldValue (self, docField, appName=None):
		value = None
		# For ecudocs is "CO" for codebin is "colombia"
		if "00_Pais" in docField:
			paises     = {"CO":"CO", "EC":"EC"}
			if appName == "CODEBIN":
				paises     = {"CO":"colombia", "EC":"ecuador"}

			codigoPais = self.fields [docField]["value"]
			value      =  paises [codigoPais]

		# In PDF docs, it is a check box marker with "X"
		elif "Carga_Tipo" in docField and not "Descripcion" in docField and self.docType == "MANIFIESTO":
			fieldValue = self.fields [docField]["value"]
			value = "X" if "X" in fieldValue.upper() else ""

		else:
			value = self.fields [docField]["content"]

		return value

