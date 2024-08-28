import re, os
from importlib import resources
from traceback import format_exc as traceback_format_exc

from .ecuapass_utils import Utils
from .resourceloader import ResourceLoader 

#--------------------------------------------------------------------
# Class for extracting different values from document texts
#--------------------------------------------------------------------
class Extractor:
	#-------------------------------------------------------------------
	#-- Get location info: ciudad, pais, fecha -------------------------
	#-- Boxes: Recepcion, Embarque, Entrega ----------------------------
	#-------------------------------------------------------------------
	def extractLocationDate (text, resourcesPath, fieldType=None):
		location = {"ciudad":"||LOW", "pais":"||LOW", "fecha":"||LOW"}
		try:
			text   = text.replace ("\n", " ")
			# Fecha
			fecha = Extractor.getDate (text, resourcesPath)
			location ["fecha"] = fecha if fecha else "||LOW"
			# Pais
			text, location = Extractor.removeSubjectCiudadPais (text, location, resourcesPath, fieldType)
		except:
			Utils.printException (f"Obteniendo datos de la localización: '{fieldType}' en el texto", text)

		return (location)

	#-----------------------------------------------------------
	#-- Get subject (remitente, destinatario, declarante,..) info
	#-- Info: nombre, dir, pais, ciudad, id, idNro
	#-----------------------------------------------------------
	def getSubjectInfoFromText (text, resourcesPath, subjectType):
		subject = {"nombre":None, "direccion":None, "pais": None, 
		           "ciudad":None, "tipoId":None, "numeroId": None}
		try:
			lines   = text.split ("\n")

			if len (lines) == 3:
				nameDirLines = lines [0:2]
				idPaisLine   = lines [2]
			elif len (lines) == 4:
				nameDirLines = lines [0:3]
				idPaisLine   = lines [3]
			elif len (lines) < 3:
				print (f">>> Alerta:  Pocas líneas de texto para extraer información de empresa.")
				return subject

			text, subject = Extractor.removeSubjectId (idPaisLine, subject, subjectType)
			text, subject = Extractor.removeSubjectCiudadPais (text, subject, resourcesPath, subjectType)
			text, subject = Extractor.removeSubjectCiudadPais (text, subject, resourcesPath, subjectType)
			nameDirText   = "\n".join (nameDirLines)
			text, subject = Extractor.removeSubjectNombreDireccion
			(nameDirText, subject, subjectType)
			subject ["numeroId"] = Utils.convertToEcuapassId (subject ["numeroId"])
		except:
			Utils.printException (f"Obteniendo datos del sujeto: '{subjectType}' en el texto: '{text}'")

		print (subject)
		return (subject)

	#--  Extracts and replaces IdType and IdNumber from text-------
	def getReplaceSubjectId (text, subject, replaceString, type):
		try:
			if not any (x in text.upper() for x in ["NIT", "RUC", "OTROS"]): 
				return (text, subject)

			reNumber = r'\d+(?:[.,]*\d*)+' # RE for extracting a float number 
			reId     = rf"(RUC|NIT|OTROS)[\s.:]+({reNumber}(?:-\d)?)\s*"
			result	 = re.search (reId, text, flags=re.S)
		 
			subject ["tipoId"]   = result.group (1) if result else None
			subject ["numeroId"] = result.group (2).replace (".", "") if result else None

			text	 = re.sub (reId, replaceString, text, flags=re.S).strip()
		except:
			Utils.printException (f"Obteniendo informacion de ID de '{type}'")

		return (text, subject)

	#--  Extracts and removes IdType and IdNumber from text-------
	def removeSubjectId (text, subject, type):
		text, subject = Extractor.getReplaceSubjectId (text, subject, "", type)
		return (text, subject)
		

	#------------------------------------------------------------------
	#-- Get ciudad + pais using data from ecuapass
	#------------------------------------------------------------------
#	def extractCiudadPais (text, resourcesPath):
#		info = {"ciudad":None, "pais":None}
#		try:
#			rePais = ".*?(ECUADOR|COLOMBIA|PERU)"
#			pais   = Extractor.getValueRE (rePais, text, re.I)
#			info ["pais"] = pais 
#				
#			if (pais):
#				cities = Extractor.getSubjectCitiesString (pais, resourcesPath)
#				reLocation = f"(?P<ciudad>{cities}).*(?P<pais>{pais})[.\s]*"
#				result = re.search (reLocation, text, flags=re.I)
#				info ["ciudad"] = result.group ("ciudad") if result != None else None
#			else:
#				reCiudad = r"\b(\w+(?:\s+\w+)*)\b"
#				info ["ciudad"] = Extractor.getValueRE (reCiudad, text, re.I)
#
#		except:
#			Utils.printException (f"Obteniendo ciudad-pais de '{text}'", text)
#
#		return (info)

	
	#-- Get ciudad + pais using data from ecuapass ------------------
	def removeSubjectCiudadPais (text, subject, resourcesPath, type):
		text = text.upper ()
		try:
			rePais = ".*?(ECUADOR|COLOMBIA|PERU)"
			pais   = Extractor.getValueRE (rePais, text, re.I)
			subject ["pais"] = pais
				
			cities = Extractor.getSubjectCitiesString (pais, resourcesPath)

			reLocation = f"(?P<ciudad>{cities})[\s\-,\s]+(?P<pais>{pais})[.\s]*"
			result = re.search (reLocation, text, flags=re.I)
			if (result == None):
				printx (f"Ciudad desconocida en texto: '{text}' de '{type}'")
			else:
			#if (type in ["06_Recepcion", "07_Embarque", "08_Entrega", "19_Emision"]):
				subject ["ciudad"] = result.group ("ciudad") if result else None
				text	= text.replace (result.group (0), "")

		except:
			Utils.printException (f"Obteniendo ciudad-pais de '{type}'", text)

		return (text.strip(), subject)


	#-- Extracts and remove Nombre and Direccion---------------------
	def removeSubjectNombreDireccion (text, subject, type):
		try:
			textLines = text.split ("\n")
			subject ["nombre"] = textLines [0].strip()
			if len (textLines) == 2:
				subject ["direccion"] = textLines [1].strip()
			else:
				subject ["direccion"] = " ".join (textLines[1:]) + "||LOW"
				#printx ("EXCEPCION: Información sujeto con muchas líneas")
				#printx ("\tTEXT:", textLines)
		except:
			Utils.printException (f"Obteniendo nombre-direccion de '{type}'")

		return (text, subject)

	#-- Extracts and remove Nombre and Direccion---------------------
	#-- Check if name or dir is expanded in more than one line ------
	def removeSubjectNombreDireccion (text, subject, type):
		try:
			lines = text.split ("\n")
			if len (lines) == 2:
				subject ["nombre"]    = lines [0].strip()
				subject ["direccion"] = lines [1].strip()
			elif len (lines) == 3:
				if len (lines [0]) > len (lines [1]):
					subject ["nombre"]    = lines [0].strip () + " " + lines [1].strip () + "||LOW"
					subject ["direccion"] = lines [2].strip () + "||LOW"
				else: 
					subject ["nombre"]    = lines [0].strip () + "||LOW"
					subject ["direccion"] = lines [1].strip () + " " + lines [2].strip () + "||LOW"
		except:
			Utils.printException (f"Obteniendo nombre-direccion de '{type}'")

		return (text, subject)

	#-----------------------------------------------------------
	# Using "search" extracts first group from regular expresion. 
	# Using "findall" extracts last item from regular expresion. 
	#-----------------------------------------------------------
	def getValueRE (RE, text, flags=re.I, function="search"):
		if text != None:
			if function == "search":
				result = re.search (RE, text, flags=flags)
				return result.group (1) if result else None
			elif function == "findall":
				resultList = re.findall (RE, text, flags=flags)
				return resultList [-1] if resultList else None
		return None

	#-- Extract all type of number (int, float..) -------------------
	def getNumber (text):
		reNumber = r'\d+(?:[.,]?\d*)+' # RE for extracting a float number 
		number = Utils.getValueRE (reNumber, text, function="findall")
		return (number)

	def getRemoveNumber (text):
		number = Extractor.getNumber (text)
		if number != None:
			text.replace (number, "")
		return text, number

	#-- Get "numero documento" with possible prefix "No."------------
	def getNumeroDocumento (text):
		# Cases SILOGISTICA and others
		# Examples: ["N° PO-CO-0011-21-338781-23", "No.019387", "CO003627"]
		reNumber = r'(?:N.*?)?\b([A-Za-z0-9-]+)\b'

		# NTA, BYZA, SYTSA
		#reNumber = r'([A-Za-z]+\d+)'
		number   = Extractor.getValueRE (reNumber, text)
		return number
	
	#-- Get MRN number from text using the pattern "MRN:XXXX"
	def getMRNFromText (text):
		reMRN = r"\bMRN\b\s*[:]?\s*\b(\w*)\b"
		MRN = Utils.getValueRE (reMRN, text)
		return MRN

	def getLastString (text):
		string = None
		try:
			reStrings = r'([a-zA-Z0-9-]+)'
			results   = re.findall (reStrings, text) 

			if len (results) > 1:
				string    = results [-1] if results else None 
		except Exception as e:
			Utils.printException (f"Extrayendo última cadena desde el texto: '{text}'", e)
		return string

	def getFirstString (text):
		string = None
		try:
			reStrings = r'([a-zA-Z0-9-]+)'
			results   = re.findall (reStrings, text) 
			string    = results [0] if results else None 
		except Exception as e:
			Utils.printException (f"Extrayendo última cadena desde el texto: '{text}'", e)
		return string
	
	#------------------------------------------------------------------
	# Extracts last word from a string with 1 or more words|numbers
	#------------------------------------------------------------------
	def getLastWord (text):
		word = None
		try:
			# RE for extracting all words as a list (using findall)
			reWords = r'\b[A-Za-z]+(?:/\w+)?\b' 
			results = re.findall (reWords, text) 
			word    = results [-1] if results else None 
		except Exception as e:
			Utils.printException (f"Extrayendo última palabra desde el texto: '{text}'", e)
		return word
	
	#------------------------------------------------------------------
	# Extracts last int number from a string with 1 or more numbers
	#------------------------------------------------------------------
	def getLastNumber (text):
		number = None
		try:
			reNumbers = r'\b\d+\b' # RE for extracting all numeric values as a list (using findall)
			number = re.findall (reNumbers, text)[-1]
		except:
			Utils.printException ("Extrayendo último número desde el texto: ", text)
		return number
	#------------------------------------------------------------------
	# Extract conductor's name (full)
	#------------------------------------------------------------------
	def extractNames (text):
		names = None
		try:
			reNames = r'\b[A-Z][A-Za-z\s]+\b'
			names = re.search (reNames, text).group(0).strip()
		except:
			Utils.printException ("Extrayendo nombres desde el texto: ", text)
		return names
			
	#------------------------------------------------------------------
	# Get pais from nacionality 
	#------------------------------------------------------------------
	def getPaisFromPrefix (text):
		pais = None
		try:
			if "COL" in text.upper():
				pais = "COLOMBIA"	
			elif "ECU" in text.upper():
				pais = "ECUADOR"	
			elif "PER" in text.upper():
				pais = "PERU"	
		except:
			Utils.printException ("Obtenidendo pais desde nacionalidad en el texto:", text)
		return pais

	#------------------------------------------------------------------
	# Extract pais
	#------------------------------------------------------------------
	def getPais (text, resourcesPath):
		pais = None
		try:
			rePaises = Extractor.getDataString ("paises.txt", resourcesPath)
			pais     = Extractor.getValueRE (f"({rePaises})", text, re.I)

			if not pais: # try "(CO), "(EC)" and "(PE)"
				rePais   = r'.*\((CO|EC|PE)\)'
				paisCode = Extractor.getValueRE (rePais, text, re.I)
				pais     = Utils.getPaisFromCodigoPais (paisCode)
		except:
			Utils.printException (f"Obteniendo pais desde texto '{text}'")
		return pais

	#-- Get ciudad given pais else return stripped string ------------ 
	def getCiudad (text, pais, resourcesPath):
		if pais: # if pais get ciudades from pais and search them in text
			reCities = Extractor.getSubjectCitiesString (pais, resourcesPath)
			ciudad   = Extractor.getValueRE (f"({reCities})", text, re.I)
		else:      # if no pais, get the substring without trailing spaces
			reCiudad = r"\b(\w+(?:\s+\w+)*)\b"
			results  = re.findall (reCiudad, text)
			ciudad   = results [-1] if results [-1] else None

		return ciudad

	def getCiudadPais (text, resourcesPath):
		pais   = Extractor.getPais (text, resourcesPath)
		ciudad = Extractor.getCiudad (text, pais, resourcesPath)
		return ciudad, pais

	#------------------------------------------------------------------
	# Extract 'placa' and 'pais'
	#------------------------------------------------------------------
	def getPlacaPais (text, resourcesPath):
		result = {"placa":None, "pais":None}

		text = text.upper ()
		if (text == "X" or text is None or "N/A" in text or "XX" in text):
			return result

		try:
			pais             = Extractor.getPais (text, resourcesPath)
			text             = text.replace (pais, "")   
			#rePlacaPais01 = r"(\w+)\W+(\w+)"
			#rePlacaPais      = r'^([A-Z0-9]+)[\s\-]*?(COLOMBIA|ECUADOR|PERU).*$'
			rePlaca           = r'(\b[A-Z0-9]+(?:-[A-Z0-9]+)?\b)'
			result ["placa"]  = Extractor.getValueRE (rePlaca, text)
			result ["pais"]   = pais
		except:
			Utils.printException (f"Extrayendo placa pais desde el texto: '{text}'")
		return result
			

	#------------------------------------------------------------------
	# Get 'embalaje' from text with number + embalaje: NNN WWWWW
	#------------------------------------------------------------------
	def getTipoEmbalaje (text):
		try:
			reNumber   = r'\d+(?:[.,]*\d*)+' # RE for extracting a float number 
			reEmbalaje = rf"{reNumber}\s+(\b(\w+)\b)"    # String after number
			embalaje   = Extractor.getValueRE (reEmbalaje, text) 

			codeEmbalaje = Extractor.getCodeEmbalaje (embalaje)

			return codeEmbalaje
		except:
			Utils.printx (f"Problemas extrayendo embalaje desde texto: '{text}'")
			#Utils.printException ()
			return None

	def getCodeEmbalaje (embalaje):
		if "PALLET" in embalaje or "ESTIBA" in embalaje:
			return "152" # "[152] PALETAS"
		elif "SACO" in embalaje.upper ():
			return "104" # "[104] SACO"
		elif "CAJA" in embalaje.upper ():
			return "035" # "[035] CAJA"
		else:
			return embalaje.strip () + "||LOW"

	#------------------------------------------------------------------
	#-- Extract numerical or text date from text ----------------------
	#------------------------------------------------------------------
	def getDate (text, resourcesPath):
		numericalDate = "||LOW"
		try:
			# Load months from data file
			monthsString = Extractor.getDataString ("meses.txt", resourcesPath)
			monthsList   = monthsString.split ("|")
		
			# Search for numerical or text date
			reDay      = r'(?P<day>\d{1,2})'
			reMonthNum = r'(?P<month>\d{1,2})'
			reMonthTxt = rf'(?P<month>{monthsString})'
			reYear     = r'(?P<year>\d[.]?\d{3})'
			reWordSep  = r'\s+(?:DE|DEL)\s+'
			reSep      = r'(-|/)'

			#reDate0 = rf'\b{reDay}\s*[-]\s*{reMonthNum}\s*[-]\s*{reYear}\b'     # 31-12-2023
			reDate0 = rf'\b{reDay}\s*{reSep}\s*{reMonthNum}\s*{reSep}\s*{reYear}\b'     # 31-12-2023
			reDate1 = rf'\b{reMonthTxt}\s+{reDay}{reWordSep}{reYear}\b'         # Junio 20 del 2023
			reDate2 = rf'\b{reMonthTxt}\s+{reDay}{reSep}{reYear}\b'             # Junio 20/2023
			reDate3 = rf'\b{reDay}{reWordSep}{reMonthTxt}{reWordSep}{reYear}\b' # 20 de Junio del 2023
			reDate4 = rf'\b{reYear}{reSep}{reMonthNum}{reSep}{reDay}\b'         # 2023/12/31
			reDate5 = rf'\b{reYear}{reSep}{reMonthTxt}{reSep}{reDay}\b'         # 2023/DICIEMBRE/31
			reDate6 = rf'\b{reDay}{reSep}{reMonthTxt}{reSep}{reYear}\b'         # 2023/DICIEMBRE/31
			reDateOptions = [reDate0, reDate1, reDate2, reDate3, reDate4, reDate5, reDate6]

			# Evaluate all reDates and select the one with results
			results = [re.search (x, text, re.I) for (i, x) in enumerate (reDateOptions)]
			if results [0]:
				result = results [0]
				month  = result.group('month')
			elif results [1] or results [2]:
				result = results [1] if results [1] else results [2]
				month  = monthsList.index (result.group('month').upper()) + 1
			elif results [3]:
				result = results [3]
				month  = monthsList.index (result.group('month').upper()) + 1
			elif results [4]:
				result = results [4]
				month  = result.group('month')
			elif results [5]:
				result = results [5]
				month  = monthsList.index (result.group('month').upper()) + 1
			elif results [6]:
				result = results [6]
				month  = monthsList.index (result.group('month').upper()) + 1
			else:
				printx (f"No existe fecha en texto '{text}'")
				return None

			year = result.group ('year').replace (".", "")
			numericalDate = f"{result.group('day')}-{month}-{year}"
		except Exception as e:
			Utils.printException (f"Obteniendo fecha de texto: '{text}'", e)
			
		return numericalDate

	#-------------------------------------------------------------------
	#-- Load cities from DB and create a piped string of cites ---------
	#-------------------------------------------------------------------
	def getSubjectCitiesString (pais, resourcesPath):
		if (pais=="COLOMBIA"):
			citiesString = Extractor.getDataString ("ciudades_colombia.txt", resourcesPath)
		elif (pais=="ECUADOR"):
			citiesString = Extractor.getDataString ("ciudades_ecuador.txt", resourcesPath)
		elif (pais=="PERU"):
			citiesString = Extractor.getDataString ("ciudades_peru.txt", resourcesPath)
		else:
			return None

		return citiesString

	#-------------------------------------------------------------------
	#-- Get ECUAPASS data items as dic taking resources from package no path
	#-------------------------------------------------------------------
	def old_getDataDic (dataPath):
		dirList         = dataPath.split (os.path.sep)
		resourceName    = dirList [-1]
		resourcePackage = dirList [-2]

		dataDic = {} 
		dataLines = ResourceLoader.loadText (resourcePackage, resourceName)

		for line in dataLines [1:]:
			res = re.search (r"\[(.+)\]\s+(.+)", line)
			dataDic [res.group(1)] = res.group(2)

		return (dataDic)

	def getDataDic (dataFilename, resourcesPath, From="values"):
		dataPath        = os.path.join (resourcesPath, dataFilename)
		dirList         = dataPath.split (os.path.sep)
		resourceName    = dirList [-1]
		resourcePackage = dirList [-2]

		dataDic = {} 
		dataLines = ResourceLoader.loadText (resourcePackage, resourceName)

		for line in dataLines [1:]:
			res = re.search (r"\[(.+)\]\s+(.+)", line)
			dataDic [res.group(1)] = res.group(2)

		return (dataDic)
  
	#-------------------------------------------------------------------
	#-- Return a piped string of ECUPASS data used in regular expression
	#-- From join "values" or join "keys"
	#-------------------------------------------------------------------
	def getDataString (dataFilename, resourcesPath, From="values"):
		dataPath   = os.path.join (resourcesPath, dataFilename)
		dataDic    = Extractor.getDataDic (dataFilename, resourcesPath)
		dataString = None
		if From=="values":
			#dataString = "|".join (map (re.escape, dataDic.values())) #e.g. 'New York' to 'New\\ York'
			dataString = "|".join (dataDic.values()) #e.g. 'New York' to 'New\\ York'
		else:
			dataString = "|".join (dataDic.keys())
		return (dataString)


#-------------------------------------------------------------------
# Global utility functions
#-------------------------------------------------------------------

def printx (*args, flush=True, end="\n", plain=False):
	print ("SERVER:", *args, flush=flush, end=end)
