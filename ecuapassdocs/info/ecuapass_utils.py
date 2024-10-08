import os, json, re, sys, tempfile, datetime

from traceback import format_exc as traceback_format_exc
import traceback

from .resourceloader import ResourceLoader 

#--------------------------------------------------------------------
# Utility function used in EcuBot class
#--------------------------------------------------------------------
class Utils:
	runningDir = None
	message = ""   # Message sent by 'checkError' function

	#------------------------------------------------------
	# Format date string "DD-MM-YYYY" to Postgres "YYYY-MM-DD"
	#------------------------------------------------------
	def formatDateStringToPGDate (date_string):
		if type (date_string) == datetime.datetime:
			date_string = date_string.strftime ("%d-%m-%Y")

		date_object    = datetime.datetime.strptime (date_string, "%d-%m-%Y").date()
		formatted_date = date_object.strftime("%Y-%m-%d")
		return formatted_date

	#------------------------------------------------------
	#-- Redirect stdout output to file
	#------------------------------------------------------
	def redirectOutput (logFilename, logFile=None, stdoutOrg=None):
		if logFile == None and stdoutOrg == None:
			logFile    = open (logFilename, "w")
			stdoutOrg  = sys.stdout
			sys.stdout = logFile
		else:
			logFile.close ()
			sys.stdout = stdoutOrg

		return logFile, stdoutOrg

	#------------------------------------------------------
  	#-- Remove text added with confidence value ("wwww||dd")
	#------------------------------------------------------
	def removeConfidenceString (fieldsConfidence):
		fields = {}
		for k in fieldsConfidence:
			confidenceStr = fieldsConfidence [k] 
			fields [k] = confidenceStr.split ("||")[0] if confidenceStr else None
			if fields [k] == "":
				fields [k] = None
		return fields

	#-- Get file/files for imageFilename 
	def imagePath (imageFilename):
		imagesDir = os.path.join (Utils.runningDir, "resources", "images")
		path = os.path.join (imagesDir, imageFilename)
		if os.path.isfile (path):
			return path
		elif os.path.isdir (path):
			pathList = []
			for file in sorted ([os.path.join (path, x) for x in os.listdir (path) if ".png" in x]):
				pathList.append (file)

			return pathList
		else:
			print (f">>> Error: in 'imagePath' function. Not valid filename or dirname:'{imageFilename}'") 
			return None
			
	#-- Read JSON file
	def readJsonFile (jsonFilepath):
		Utils.printx (f"Leyendo archivo de datos JSON '{jsonFilepath}'...")
		data = json.load (open (jsonFilepath, encoding="utf-8")) 
		return (data)

	#-- Check if 'resultado' has values or is None
	def checkError (resultado, message):
		if resultado == None:
			Utils.message = f"ERROR: '{message}'"
			if "ALERTA" in message:
				Utils.printx (message)
			raise Exception (message)
		return False

	def printx (*args, flush=True, end="\n"):
		print ("SERVER:", *args, flush=flush, end=end)
		message = "SERVER: " + " ".join ([str(x) for x in args])
		return message

	def printException (message=None, text=None):
		if message:
			Utils.printx ("EXCEPCION: ", message) 
		if text:
			Utils.printx ("TEXT:", text) 
		Utils.printx (traceback_format_exc())

	#-- Get value from dict fields [key] 
	def getValue (fields, key):
		try:
			return fields [key]["content"]
		except:
			Utils.printException ("EXEPCION: Obteniendo valor para la llave:", key)
			#traceback.print_exception ()

			return None

	#-----------------------------------------------------------
	# Using "search" extracts first group from regular expresion. 
	# Using "findall" extracts last item from regular expresion. 
	#-----------------------------------------------------------
	def getValueRE (RE, text, flags=re.I, function="search"):
		if text != None:
			if function == "search":
				result = re.search (RE, text, flags=flags)
				return result.group(1) if result else None
			elif function == "findall":
				resultList = re.findall (RE, text, flags=flags)
				return resultList [-1] if resultList else None
		return None

	def getNumber (text):
		reNumber = r'\d+(?:[.,]?\d*)+' # RE for extracting a float number 
		number = Utils.getValueRE (reNumber, text, function="findall")
		return (number)


	#-- Save fields dict in JSON 
	def saveFields (fieldsDict, filename, suffixName):
		prefixName	= filename.split(".")[0]
		outFilename = f"{prefixName}-{suffixName}.json"
		print (f"+++ DEBUG: saveFields '{outFilename}'")
		with open (outFilename, "w") as fp:
			json.dump (fieldsDict, fp, indent=4, default=str)
		return outFilename

	def initDicToValue (dic, value):
		keys = dic.keys ()
		for k in keys:
			dic [k] = value
		return dic

	#-- Create empty dic from keys
	def createEmptyDic (keys):
		emptyDic = {}
		for key in keys:
			emptyDic [key] = None
		return emptyDic

	#-- If None return "||LOW"
	def checkLow (value):
		if type (value) == dict:
			for k in value.keys ():
				value [k] = value [k] if value [k] else "||LOW"
		else:
			 value = value if value else "||LOW"

		return value


	#-- Add "||LOW" to value(s) taking into account None
	def addLow (value):
		if type (value) == dict:
			for k in value.keys ():
			 	value [k] = value [k] + "||LOW" if value [k] else "||LOW"
		else:
			value = value + "||LOW" if value else "||LOW"
		return value

	#-----------------------------------------------------------
	# Convert from Colombian/Ecuadorian values to American values
	#-----------------------------------------------------------
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
		
		#print (">>> Input value str: ", value_str)
		if Utils.is_valid_american_value (value_str):
			#print (f"Value '{value_str}' in american format")
			return value_str

		# Validate if it is a valid Colombian value
		if not Utils.is_valid_colombian_value(value_str):
			Utils.printx (f"ALERTA: valores en formato invalido: '{value_str}'")
			return value_str + "||LOW"

		# Replace dots with empty strings
		newValue = ""
		for c in value_str:
			if c.isdigit():
				nc = c
			else:
				nc = "." if c=="," else ","
			newValue += nc
				
		#print (">>> Output value str: ", newValue)

		return newValue

	#----------------------------------------------------------------
	# Return fields ({02_Remitente:"XXXX"} from codebin values
	# Info is embedded according to Azure format
	#----------------------------------------------------------------
	def getAzureValuesFromCodebinValues (docType, codebinValues, docNumber):
		pdfTitle = ""
		if docType == "CARTAPORTE":
			pdfTitle      = "Carta de Porte Internacional por Carretera (CPIC)"
		elif docType == "MANIFIESTO":
			pdfTitle      = "Manifiesto de Carga Internacional (MCI)"
		else:
			printx (f"Tipo de documento desconocido: '{docType}'")

		pais, codigoPais  = Utils.getPaisCodigoFromDocNumber (docNumber)
		inputsParametersFile = Utils.getInputsParametersFile (docType)
		azureValues = {}
		# Load parameters from package
		inputParameters = ResourceLoader.loadJson ("docs", inputsParametersFile)
		for key, item in inputParameters.items():
			try:
				ecudocsField = item ["ecudocsField"]
				if not ecudocsField:
					continue
				codebinField = item ["codebinField"]
				value = codebinValues [codebinField] if codebinField else ""
				azureValues [ecudocsField] = {"value": value, "content": value}
			except KeyError as ex:
				print (f"Llave '{codebinField}' no encontrada")
				#Utils.printException (f"EXCEPCION: con campo '{codebinField}'")

		# Azure fields not existing in CODEBIN fields
		azureValues ["00_Pais"]    = {"value": codigoPais, "content": codigoPais}
		azureValues ["00a_Tipo"]   = {"value": pdfTitle, "content": pdfTitle}
		azureValues ["00b_Numero"] = {"value": docNumber, "content": docNumber}
		return azureValues
	#----------------------------------------------------------------
	# Return fields ({02_Remitente:"XXXX"} from inputs (ej. txt00 :{....}) 
	# Info is embedded according to Azure format
	#----------------------------------------------------------------
	def getAzureValuesFromInputsValues (docType, inputValues):
		inputsParametersFile = Utils.getInputsParametersFile (docType)
		azureValues = {}
		# Load parameters from package
		inputParameters = ResourceLoader.loadJson ("docs", inputsParametersFile)
		for key, item in inputParameters.items():
			ecudocsField = item ["ecudocsField"]
			if ecudocsField:
				value                      = inputValues [key]
				azureValues [ecudocsField] = {"value": value, "content": value}

		return azureValues

	#-------------------------------------------------------------------
	# Get document (CPI, MCI) fields values. Format: key:value
	#-------------------------------------------------------------------
	def getAzureValuesFromParamsFile (docType, paramsFile):
		paramsValues = json.load (open (paramsFile))

		azureValues = {}
		# Load parameters from package
		for key, item in paramsValues.items():
			ecudocsField = item ["ecudocsField"]
			value = item ["value"]
			azureValues [ecudocsField] = {"value": value, "content": value}
		return azureValues
	#-------------------------------------------------------------------
	# Load values and filter inputs not used in DB models
	# Format: key : value
	#-------------------------------------------------------------------
	def getInputValuesFromParamsFile (paramsFile):
		# Document class (ej. CartaporteDoc, ManifiestoDoc)
		inputsParams = json.load (open (paramsFile))
		inputsValues = Utils.getInputsValuesFromInputsParams (inputsParams)
		return inputsParams

	def getInputValuesFromInputParams (inputsParams):
		# Document class (ej. CartaporteDoc, ManifiestoDoc)
		#inputsParams.pop ("id")
		#inputsParams.pop ("fecha_creacion")
		#inputsParams.pop ("referencia")

		inputsValues = {}
		for key in inputsParams:
			inputsValues [key] = inputsParams [key]["value"]

		return inputsValues

	def setInputValuesToInputParams (inputValues, inputParams):
		for key in inputValues:
			try:
				inputParams [key]["value"] = inputValues [key]
			except KeyError as ex:
				print (f"Llave '{key}' no encontrada")


		return inputParams
		
	#-------------------------------------------------------------------
	# Get the number (ej. CO00902, EC03455) from the filename
	#-------------------------------------------------------------------
	def getDocumentNumberFromFilename (filename):
		numbers = re.findall (r"\w+\d+", filename)
		return numbers [-1]

	#-------------------------------------------------------------------
	# Return CARTAPORTE or MANIFIESTO
	#-------------------------------------------------------------------
	def getDocumentTypeFromFilename (filename):
		if "CPI" in filename:
			return "CARTAPORTE"
		elif "MCI" in filename:
			return "MANIFIESTO"
		elif "DTI" in filename or "DCL" in filename:
			return "DECLARACION"
		else:
			raise Exception (f"Tipo de documento desconocido para: '{filename}'")

	#-------------------------------------------------------------------
	# Get 'pais, codigo' from document number or text
	#-------------------------------------------------------------------
	def getPaisCodigoFromDocNumber (docNumber):
		paisCodes = {"COLOMBIA":"CO", "ECUADOR":"EC", "PERU": "PE"}
		pais      = Utils.getPaisFromDocNumber (docNumber)
		codigo    = paisCodes [pais]
		return pais.lower(), codigo

	def getPaisFromDocNumber (docNumber):
		try:
			codePaises = {"CO": "COLOMBIA", "EC": "ECUADOR", "PE": "PERU"}
			code   = Utils.getCodigoPais (docNumber)
			print ("+++ DEBUG: getCodigoPais: docNumber:", docNumber)
			pais   = codePaises [code]
			return pais
		except:
			print (f"ALERTA: No se pudo determinar código del pais desde el número: '{docNumber}'")

	#-- Returns the first two letters from document number
	def getCodigoPais (docNumber):
		docNumber = docNumber.upper ()
		try:
			if docNumber.startswith ("CO"): 
				return "CO"
			elif docNumber.startswith ("EC"): 
				return "EC"
			elif docNumber.startswith ("PE"): 
				return "PE"
		except:
			print (f"ALERTA: No se pudo determinar código del pais desde el número: '{docNumber}'")
		return ""
	#-------------------------------------------------------------------
	# Get 'pais, codigo' from text
	#-------------------------------------------------------------------
	def getPaisCodigoFromText (self, text):
		pais, codigo = "NONE", "NO" 
		text = text.upper ()

		if "COLOMBIA" in text:
			pais, codigo = "colombia", "CO"
		elif "ECUADOR" in text:
			pais, codigo = "ecuador", "EC"
		elif "PERU" in text:
			pais, codigo = "peru", "PE"
		else:
			raise Exception (f"No se encontró país en texto: '{text}'")

		return pais, codigo

	#----------------------------------------------------------------
	# Used in EcuapassDocs web
	#----------------------------------------------------------------
	def getCodigoPaisFromPais (pais): #"COLOMBIA", "ECUADOR", "PERU"
		try:
			paises   = {"COLOMBIA":"CO", "ECUADOR":"EC", "PERU":"PE"}
			return paises [pais.upper()]
		except:
			Utils.printException (f"Pais desconocido: '{pais}'") 
			return None

	def getPaisFromCodigoPais (paisCode):
		try:
			paisesCodes   = {"CO":"COLOMBIA", "EC":"ECUADOR", "PE":"PERU"}
			return paisesCodes [paisCode.upper()]
		except:
			Utils.printException (f"Codigo Pais desconocido: '{paisCode}'") 
			return None

	#-------------------------------------------------------------------
	# Get the number part from document number (e.g. COXXXX -> XXXX)
	#-------------------------------------------------------------------
	def getNumberFromDocNumber (docNumber):
		pattern = r'^(CO|EC|PE)(\d+)$'

		match = re.match (pattern, docNumber)
		if match:
			number = match.group(2)
			return int (number)
		else:
			raise Exception ("Número de documento '{docNumber}' sin país")
	#-------------------------------------------------------------------
	# Return 'EXPORTACION' or 'IMPORTACION' according to 'pais' and 'empresa'
	# Used in EcuapassDocs web
	#-------------------------------------------------------------------
	def getProcedimientoFromPais (empresa, pais):
		procedimientosBYZA = {"CO":"IMPORTACION", "EC":"EXPORTACION", "PE":"EXPORTACION"}
		pais = pais.upper ()
		if empresa == "BYZA" and pais.startswith ("CO"):
			return "IMPORTACION"
		elif empresa == "BYZA" and pais.startswith ("EC"):
			return "EXPORTACION"
		else:
			raise Exception (f"No se pudo identificar procedimiento desde '{empresa}':'{pais}'")

	#----------------------------------------------------------------
	#-- Return input parameters file
	#----------------------------------------------------------------
	def getInputsParametersFile (docType):
		if docType == "CARTAPORTE":
			inputsParametersFile = "cartaporte_input_parameters.json"
		elif docType == "MANIFIESTO":
			inputsParametersFile = "manifiesto_input_parameters.json"
		elif docType == "DECLARACION":
			inputsParametersFile = "declaracion_input_parameters.json"
		else:
			raise Exception (f"Tipo de documento desconocido:", docType)
		return inputsParametersFile


	#-----------------------------------------------------------
	# Load user settings (empresa, codebinUrl, codebinUser...)
	#-----------------------------------------------------------
	def loadSettings (runningDir):
		settingsPath  = os.path.join (runningDir, "settings.txt")
		if os.path.exists (settingsPath) == False:
			Utils.printx (f"ALERTA: El archivo de configuración '{settingsPath}' no existe")
			sys.exit (-1)

		settings  = json.load (open (settingsPath, encoding="utf-8")) 

		empresa   = settings ["empresa"]
		Utils.printx ("Empresa actual: ", empresa)
		return settings

	#-----------------------------------------------------------
	# Get ecuField value obtained from docFields
	# CLIENTS: DocsWeb for saving entities, dates,...
	#-----------------------------------------------------------
	def getEcuapassFieldInfo (INFOCLASS, fieldName, docFields):
		jsonFieldsPath, runningDir = Utils.createTemporalJson (docFields)
		docInfo           = INFOCLASS (jsonFieldsPath, runningDir)
		ecuapassFields    = docInfo.extractEcuapassFields ()
		ecuapassFields    = Utils.removeConfidenceString (ecuapassFields)
		print ("+++ DEBUG: ecuapassFields '{ecuapassFields}'")
		fieldInfo         = ecuapassFields [fieldName]
		return fieldInfo

	def createTemporalJson (docFields):
		numero   = docFields ["00b_Numero"]
		tmpPath        = tempfile.gettempdir ()
		jsonFieldsPath = os.path.join (tmpPath, f"ECUDOC-{numero}.json")
		json.dump (docFields, open (jsonFieldsPath, "w"))
		return (jsonFieldsPath, tmpPath)

	#-----------------------------------------------------------
	# Check if text contains word or it is not None or empty
	#-----------------------------------------------------------
	def isValidText (text):
		if text == None:
			return False
		elif text.strip () == "":
			return False
		else:
			return True
