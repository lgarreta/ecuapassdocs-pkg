
import os, json, re

from .resourceloader import ResourceLoader 
from .ecuapass_data import EcuData
from .ecuapass_extractor import Extractor
from .ecuapass_utils import Utils

# Base class for all info document clases: CartaporteInfo (CPI), ManifiestoInfo (MCI), EcuDCL (DTAI)
class EcuInfo:

	def __init__ (self, docType, fieldsJsonFile, runningDir):
		self.docType              = docType
		self.inputsParametersFile = Utils.getInputsParametersFile (docType)

		self.fieldsJsonFile = fieldsJsonFile
		self.runningDir     = runningDir

		self.empresa        = self.getEmpresaInfo ()   # Overwritten per 'empresa'

		self.resourcesPath  = os.path.join (runningDir, "resources", "data_cartaportes") 
		self.fields         = json.load (open (fieldsJsonFile))
		self.ecudoc         = {}

		#-- Basic fields
		self.numero         = self.getNumeroDocumento () # From docFields
		self.pais           = self.getPaisDocumento ()   # From docFields

	#------------------------------------------------------------------
	# Update fields that depends of other fields
	#------------------------------------------------------------------
	def updateExtractedEcuapassFields (self):
		#self.numero = self.getNumeroDocumento ()
		#self.pais   = Utils.getPaisFromDocNumber (self.numero)
		self.updateTipoProcedimientoFromFiels ()
		self.updateDistritoFromFields ()

	#-- Update tipo procedimiento (EXPO|INPO|TRANSITO) after knowing "Destino"
	#-- Update fecha entrega (when transito)
	def updateTipoProcedimientoFromFiels (self):
		tipoProcedimiento = self.getTipoProcedimiento ()

		procKeys = {
			"CARTAPORTE": "05_TipoProcedimiento", 
			"MANIFIESTO": "01_TipoProcedimiento", 
			"DECLARACION": "03_TipoProcedimiento"
		}
		self.ecudoc [procKeys [self.docType]] = tipoProcedimiento

		if self.docType == "CARTAPORTE":
			self.ecudoc ["37_FechaEntrega"]   = self.getFechaEntrega ()


	#-- Update distrito after knowing paisDestinatario
	def updateDistritoFromFields (self):
		try:
			distrito      = "TULCAN||LOW"
			paisDestino   = self.getPaisDestinoDocumento ()

			docKeys = {
				"CARTAPORTE":  "01_Distrito",
				"MANIFIESTO":  "04_Distrito",
				"DECLARACION": "01_Distrito"
			}
			ecuapassField = docKeys [self.docType]

			# Set distrito
			if self.pais == "PERU":
				self.ecudoc [ecuapassField] = "HUAQUILLAS"
			elif self.pais == "COLOMBIA":
				self.ecudoc [ecuapassField] = "TULCAN"
			elif "PERU" in paisDestino:
				self.ecudoc [ecuapassField] = "HUAQUILLAS"
			else:
				self.ecudoc [ecuapassField] = "TULCAN"
		except Exception as ex:
			Utils.printx ("EXCEPCION actualizando distrito: '{ex}'")
	
	#-- Implemented in subclasses
	def getEmpresaInfo (self):
		return None

	#------------------------------------------------------
	#-- Get doc number from docFields (azrFields)
	#-- For all types of docs (fixed for NTA and BYZA, check the others)
	#------------------------------------------------------
	def getNumeroDocumento (self):
		#print (f"+++ DEBUG: getNumeroDocumento: '{self.fields}'")
		text        = Utils.getValue (self.fields, "00b_Numero")
		numero      = Extractor.getNumeroDocumento (text)

		codigo = Utils.getCodigoPais (numero)
		self.fields ["00_Pais"] = {"value":codigo, "content":codigo}
		return numero

	#-- Return the document "pais" from docFields
	def getPaisDocumento (self):
		numero = self.getNumeroDocumento ()
		pais = Utils.getPaisFromDocNumber (numero)
		return pais

	#-- Return updated PDF document fields
	def getDocFields (self):
		return self.fields

	#-- Get id (short name: NTA, BYZA, LOGITRANS)
	def getIdEmpresa (self):
		return self.empresa ["id"]

	def getIdNumeroEmpresa (self):
		id = self.empresa ["idNumero"]
		return id

	#-- Get full name (e.g. N.T.A Nuevo Transporte ....)
	def getNombreEmpresa (self): 
		return self.empresa ["nombre"]

	#-- For NTA there are two directions: Tulcan and Huaquillas
	def getDireccionEmpresa (self):
		try:
			numero            = self.getNumeroDocumento ()
			codigoPais        = Utils.getCodigoPais (numero)
			idEmpresa         = self.getIdEmpresa ()

			if idEmpresa == "NTA" and codigoPais == "PE":
				return self.empresa ["direccion02"]
			else:
				return self.empresa ["direccion"]
		except:
			Utils.printException ("No se pudo determinar dirección empresa")
			return None

	#-----------------------------------------------------------
	#-- IMPORTACION or EXPORTACION or TRANSITO (after paisDestino)
	#-----------------------------------------------------------
	def getTipoProcedimiento (self):
		tipoProcedimiento = None
		paisDestino = self.getPaisDestinoDocumento ()
		try:
			if self.pais == "COLOMBIA" and paisDestino == "PERU":
				return "TRANSITO"
			else:
				procedimientos    = {"CO":"IMPORTACION", "EC":"EXPORTACION", "PE":"IMPORTACION"}
				numero            = self.getNumeroDocumento ()
				codigoPais        = Utils.getCodigoPais (numero)
				return procedimientos [codigoPais]

		except:
			Utils.printException ("No se pudo determinar procedimiento (IMPO/EXPO/TRANSITO)")

		return "IMPORTACION||LOW"


	#-----------------------------------------------------------
	# Get distrito according to 'empresa'
	#-----------------------------------------------------------
	def getDistrito (self):
		distrito = None
		try:
			numero            = self.getNumeroDocumento ()
			codigoPais        = Utils.getCodigoPais (numero)
			idEmpresa         = self.getIdEmpresa ()
			if idEmpresa == "NTA" and codigoPais == "PE":
				distrito = "HUAQUILLAS"
			else: # For NTA, BYZA, LOGITRANS
				distrito = "TULCAN" + "||LOW"

			return distrito
		except:
			Utils.printException ("No se pudo determinar el distrito (Importación/Exportación)")

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
			ciudad, pais   = Extractor.getCiudadPais (text, self.resourcesPath) 

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
	# Return Ecuapass docFields {key : {value:XXX, content:YYY}}
	#-- Create ECUAPASSDOCS fields from document fields using input parameters
	#----------------------------------------------------------------
	def getEcuapassFormFields (self):
		try:
			inputsParams = ResourceLoader.loadJson ("docs", self.inputsParametersFile)
			formFields = {}
			for key in inputsParams:
				docField   = inputsParams [key]["ecudocsField"]
				if docField == "" or "OriginalCopia" in docField:
					continue
				else:
					value = self.getDocumentFieldValue (docField)
					formFields [key] = value

			return formFields
		except Exception as e:
			Utils.printException ("Creando campos de ECUAPASSDOCS")
			return None

	#-----------------------------------------------------------
	# Get value for document field in azure format (id:{content:XX,value:XX})
	#-----------------------------------------------------------
	def getDocumentFieldValue (self, docField, appName=None):
		value = None
		# For ecudocs is "CO" but for codebin is "colombia"
		if "00_Pais" in docField:
			paises     = {"CO":"CO", "EC":"EC", "PE":"PE"}
			if appName == "CODEBIN":
				paises     = {"CO":"colombia", "EC":"ecuador", "PE":"peru"}

			codigoPais = self.fields [docField]["value"]
			value      =  paises [codigoPais]

		# In PDF docs, it is a check box marker with "X"
		elif "Carga_Tipo" in docField and not "Descripcion" in docField and self.docType == "MANIFIESTO":
			fieldValue = self.fields [docField]["value"]
			value = "X" if "X" in fieldValue.upper() else ""

		else:
			value = self.fields [docField]["content"]

		return value

	#------------------------------------------------------------------
	#-- get MRN according to empresa and docField
	#------------------------------------------------------------------
	def getMRN (self):
		text = None
		if self.empresa ["id"] == "NTA" and self.docType == "CARTAPORTE":
			text = Utils.getValue (self.fields, "22_Observaciones")

		elif self.empresa ["id"] == "NTA" and self.docType == "MANIFIESTO":
			text = Utils.getValue (self.fields, "29_Mercancia_Descripcion")

		elif self.empresa ["id"] == "BYZA" and self.docType == "CARTAPORTE":
			text = Utils.getValue (self.fields, "12_Descripcion_Bultos")

		elif self.empresa ["id"] == "BYZA" and self.docType == "MANIFIESTO":
			text = Utils.getValue (self.fields, "29_Mercancia_Descripcion")

		elif self.empresa ["id"] == "LOGITRANS" and self.docType == "CARTAPORTE":
			text = Utils.getValue (self.fields, "21_Instrucciones")
			if not "MRN" in text:
				text = Utils.getValue (self.fields, "22_Observaciones")

		elif self.empresa ["id"] == "LOGITRANS" and self.docType == "MANIFIESTO":
			text = Utils.getValue (self.fields, "29_Mercancia_Descripcion")

		MRN    = Extractor.getMRNFromText (text)
		return Utils.checkLow (MRN)


	#------------------------------------------------------------------
	# Get bultos info for CPI and MCI with differnte ecuapass fields
	#------------------------------------------------------------------
	def getBultosInfo (self, ecuapassFields):
		bultosInfo = Utils.createEmptyDic (["cantidad", "embalaje", "marcas", "descripcion"])
		cantidadField    = ecuapassFields ["cantidad"]
		marcasField      = ecuapassFields ["marcas"]
		descripcionField = ecuapassFields ["descripcion"]
		try:
			# Cantidad
			text             = self.fields [cantidadField]["value"]
			bultosInfo ["cantidad"] = Extractor.getNumber (text)
			bultosInfo ["embalaje"] = Extractor.getTipoEmbalaje (text)

			# Marcas 
			text = self.fields [marcasField]["value"]
			bultosInfo ["marcas"] = "SIN MARCAS" if text == "" else text

			# Descripcion
			descripcion = self.fields [descripcionField]["content"]
			descripcion = self.cleanWaterMark (descripcion)
			bultosInfo ["descripcion"] = self.getMercanciaDescripcion (descripcion)
		except:
			Utils.printException ("Obteniendo información de 'Bultos'", text)
		return bultosInfo


		
