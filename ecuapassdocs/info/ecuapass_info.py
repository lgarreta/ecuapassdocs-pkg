
import os, json, re

from ecuapassdocs.info.resourceloader import ResourceLoader 

from .ecuapass_data import EcuData
from .ecuapass_extractor import Extractor
from .ecuapass_utils import Utils

# Base class for all info document clases: CartaporteInfo (CPI), ManifiestoInfo (MCI), EcuDCL (DTAI)
class EcuInfo:

	def __init__ (self, docType, fieldsJsonFile, runningDir):
		self.docType        = docType
		self.fieldsJsonFile = fieldsJsonFile
		self.runningDir     = runningDir

		self.empresa        = self.getEmpresaInfo ()   # Overwritten per 'empresa'
		self.nombreEmpresa  = self.empresa ["id"]

		print (f"-- docType: '{self.docType}'")
		if self.docType == "CARTAPORTE":
			self.inputsParametersFile = "cartaporte_input_parameters.json"
		elif self.docType == "MANIFIESTO":
			self.inputsParametersFile = "manifiesto_input_parameters.json"
		elif self.docType == "DECLARACION":
			self.inputsParametersFile = "declaracion_input_parameters.json"
		else:
			Utils.printx (f"ERROR: Tipo de documento desconocido:", docType)

		self.resourcesPath        = os.path.join (runningDir, "resources", "data_cartaportes") 
		self.fields               = json.load (open (fieldsJsonFile))
		self.fields ["jsonFile"]  = fieldsJsonFile
		self.ecudoc               = {}

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
		procedimientosNTA   = {"CO":"EXPORTACION", "EC":"IMPORTACION"}
		procedimientosBYZA  = {"CO":"IMPORTACION", "EC":"EXPORTACION"}

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
			expression = r"By\s*za\s*soluciones\s*(que\s*)*facilitan\s*tu\s*vida"
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
			if self.docType == "CARTAPORTE":   # Before "---" or CEC####-###
				pattern = r'((---+|CEC).*)$'
				descripcion = re.sub (pattern, "", descripcion, flags=re.DOTALL)

			elif self.docType == "MANIFIESTO": # Before "---" or CPI: ###-###
				pattern = r'((---+|CPI:).*)$'
				descripcion = re.sub (pattern, "", descripcion, flags=re.DOTALL)

		return descripcion

	#----------------------------------------------------------------
	#-- Create CODEBIN fields from document fields using input parameters
	#----------------------------------------------------------------
	def getCodebinFields (self):
		try:
			inputsParams = ResourceLoader.loadJson ("docs", self.inputsParametersFile)
			codebinFields = {}
			for key in inputsParams:
				docField   = inputsParams [key]["field"]
				cbinField  = inputsParams [key]["fieldCodebin"]
				#print ("-- key:", key, " dfield:", docField, "cfield: ", cbinField)
				if cbinField:
					value = self.getDocumentFieldValue (docField, "CODEBIN")
					codebinFields [cbinField] = value

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
				docField   = inputsParams [key]["field"]
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
		if "00_Pais" in docField:
			paises     = {"CO":"CO", "EC":"EC"}
			if appName == "CODEBIN":
				paises     = {"CO":"colombia", "EC":"ecuador"}

			codigoPais = self.fields [docField]["value"]
			value      =  paises [codigoPais]

		elif "Gastos" in docField and self.docType == "CARTAPORTE" :
			fieldName	= docField.split (":")[0]
			rowName		= docField.split (":")[1].split (",")[0]
			colName		= docField.split (":")[1].split (",")[1]
			tablaGastos = self.fields [fieldName]["value"]
			value		= self.getValueTablaGastos (tablaGastos, rowName, colName)

		elif "Carga_Tipo" in docField and not "Descripcion" in docField and self.docType == "MANIFIESTO":
			fieldValue = self.fields [docField]["value"]
			value = 1 if "x" in fieldValue or "X" in fieldValue else 0

		else:
			value = self.fields [docField]["content"]

		return value

