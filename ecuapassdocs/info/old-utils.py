import os, json, re, sys
import pyautogui as py

import traceback
from traceback import format_exc as traceback_format_exc

#--------------------------------------------------------------------
# Utility function used in EcuBot class
#--------------------------------------------------------------------
class Utils:
	runningDir = None
	message = ""   # Message sent by 'checkError' function

  	#-- Remove text added with confidence value ("wwww||dd")
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
		Utils.printx (">>> IMAGESDIR: ", imagesDir)
		path = os.path.join (imagesDir, imageFilename)
		if os.path.isfile (path):
			return path
		elif os.path.isdir (path):
			pathList = []
			for file in sorted ([os.path.join (path, x) for x in os.listdir (path)]):
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

	#-- Detect ECUAPASS window
	def detectEcuapassWindow ():
		Utils.printx ("Detectando ventana del ECUAPASS...")
		windows = py.getAllWindows ()
		ecuWin = None
		for win in windows:
			if win.title == 'ECUAPASS - SENAE browser':
				ecuWin = win
				break
		if Utils.checkError (ecuWin, "ALERTA: No se detectó ventana del ECUAPASS"):
			return Utils.message

		return (ecuWin)

	#-- Check if active webpage is the true working webpage
	def detectEcuapassDocumentWindow (docName):
		Utils.printx (f"Detectando página de '{docName}' activa...")
		docFilename = "";
		if docName == "cartaporte":
			docFilename = "image-text-CartaporteCarretera.png"; 
		elif docName == "manifiesto":
			docFilename = "image-text-ManifiestoTerrestre.png"; 
		elif docName == "declaracion":
			docFilename = "image-text-DeclaracionTransito.png"; 

		print (">>> DocFilename:", docFilename)
		title = Utils.getBox (Utils.imagePath (docFilename), confidence=0.7, grayscale=True)
		if Utils.checkError (title, f"ALERTA: No se detectó página de '{docName}' "):
			return Utils.message

	#-- Activate window by title
	def activateWindowByTitle (titleString):
		Utils.printx (f"Detectando ventana '{titleString}'...")
		windows = py.getAllWindows ()
		ecuWin = None
		for win in windows:
			if titleString in win.title:
				ecuWin = win
				break
		if Utils.checkError (ecuWin, f"ALERTA: No se detectó ventana '{titleString}' "):
			return Utils.message

		Utils.printx (f"Activando ventana '{titleString}'...")
        
		SLEEP=0.2
		if ecuWin.isMinimized:
			ecuWin.restore (); py.sleep (SLEEP)

		ecuWin.minimize (); py.sleep (SLEEP)
		ecuWin.maximize (); py.sleep (SLEEP)
		#ecuWin.activate (); #py.sleep (SLEEP)
		ecuWin.resizeTo (py.size()[0], py.size()[1]); py.sleep (SLEEP)
		#ecuWin.moveTo (0, 0)

		return (ecuWin)

	#-- Detect and activate ECUAPASS-browser/ECUAPASS-DOCS window
	def activateEcuapassWindow ():
		return Utils.activateWindowByTitle ('ECUAPASS - SENAE browser')

	def activateEcuapassDocsWindow ():
		return Utils.activateWindowByTitle ('Ecuapass-Docs')

	#-- Maximize window clicking on 'maximize' buttone
	def maximizeWindow (win):
		py.keyDown('alt')
		py.press(' ')
		py.press('x')
		py.keyUp('alt')

	def maximizeWindow_click (win):
		if win.isMaximized:
			Utils.printx ("Ventana ya está maximizada...")
			return

		Utils.printx ("Maximixando la ventana...")
		Utils.printx ("\tWin info:", Utils.getWinInfo (win))
		win.moveTo (0,0)

		xy = py.locateCenterOnScreen (Utils.imagePath ("image-windows-WindowButtons.png"),
					confidence=0.8, grayscale=True, 
					region=(win.left, win.top, win.width, win.height))
		if Utils.checkError (xy, "ERROR: No se localizó botón de maximizar la ventana"):
			return Utils.message

		py.click (xy[0], xy[1])

		w, h = py.size ()
		win.left = win.top = 0
		win.width = w

	#-- Clear previous webpage content
	def clearWebpageContent ():
		Utils.printx ("Localizando botón de borrado...")
		filePaths = Utils.imagePath ("image-button-ClearPage")
		for fpath in filePaths:
			print (">>> Probando: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.80, grayscale=True)
			if (xy):
				print (">>> Detectado")
				py.click (xy[0], xy[1], interval=1)    
				return True

		# Utils.printx ("ALERTA: No se detectó botón de borrado")
		return (False)
		

#	def org_clearWebpageContent ():
#		Utils.printx ("Localizando botón de borrado...")
#		xy = py.locateCenterOnScreen (Utils.imagePath ("image-field-ClearButton.png"), 
#				confidence=0.8, grayscale=True)
#		if Utils.checkError (xy, "ALERTA: No se detectó botón de borrado"):
#			return Utils.message
#
#		py.click (xy[0], xy[1], interval=1)    
#
#		return xy

	#-- Clear previous webpage content
	def clickSelectedCartaporte ():
		Utils.printx ("Localizando cartaporte seleccionada...")
		xy = py.locateCenterOnScreen (Utils.imagePath ("image-text-blue-TERRESTRE-manifiesto.png"), 
				confidence=0.8, grayscale=False)
		if Utils.checkError (xy, "ALERTA: No se detectó cartaporte seleccionada"):
			return Utils.message

		py.click (xy[0], xy[1], interval=1)    

		return xy

	#--------------------------------------------------------------------
	# Scroll to beginning by clicking in scroll up button (^)
	#--------------------------------------------------------------------
	def mouse_scrollWindowToBeginning ():
		Utils.printx ("Scrolling window hasta el inicio...")
		xy = py.locateCenterOnScreen (Utils.imagePath ("image-scroll-up.png"), 
				confidence=0.8, grayscale=True)
		if Utils.checkError (xy, "ALERTA: No se detectó botón de scroll-up"):
			return Utils.message

		py.mouseDown (xy[0], xy[1])
		py.sleep (3)
		py.mouseUp (xy[0], xy[1])
		#for i in range (0,5):
		#	py.click (xy[0], xy[1], interval=1)    

	def scrollWindowToBeginning ():
		Utils.printx ("Scrolling window hasta el inicio...")
		xy = py.locateCenterOnScreen (Utils.imagePath ("image-scroll-up.png"), 
				confidence=0.8, grayscale=True)
		if Utils.checkError (xy, "ALERTA: No se detectó botón de scroll-up"):
			return Utils.message

		py.mouseDown (xy[0], xy[1])
		py.sleep (3)
		py.mouseUp (xy[0], xy[1])

	#-- Scroll down/up N times (30 pixels each scroll)
	def scrollN (N, direction="down"):
		sizeScroll = -10000 if direction=="down" else 10000
		#Utils.printx (f"\tScrolling {sizeScroll} by {N} times...")
		for i in range (N):
			#Utils.printx (f"\t\tScrolling {i} : {30*i}")
			py.scroll (sizeScroll)

	#-- Center field in window by scrolling down
	def centerField (imageName):
		Utils.printx ("\tCentering field...")
		xy = Utils.getBox (imageName, grayscale=True)
		Utils.printx ("XY: ", xy)
		if Utils.checkError (xy, f"ERROR: Campo no localizado"):
			return Utils.message

		while xy.top > 0.7 * win.height:
			Utils.printx ("\t\tScrolling down:", xy)
			Utils.scrollN (2)
			xy = Utils.getBox (imageName, confidence=0.8, grayscale=True)

	#-- Check if 'resultado' has values or is None
	def checkError (resultado, message):
		if resultado == None:
			Utils.message = f"ERROR: '{message}'"
			if "ALERTA" in message:
				Utils.printx (message)
			raise Exception (message)
		return False

	#-- Get information from window
	def getWinInfo (win):
		info = "Left: %s, Top: %s, Width: %s, Height: %s" % (
				win.left, win.top, win.width, win.height)
		return (info)

	#-- Redefinition of 'locateOnScreen' with error checking
	def getBox (imgName, region=None, confidence=0.7, grayscale=True):
		try:
			box = py.locateOnScreen (imgName, region=region,
				confidence=confidence, grayscale=grayscale)
			return (box)
		except Exception as ex:
			Utils.printx (f"EXCEPTION: Función 'getBox' falló. ImgName: '{imgName}'. Region: '{region}'.")
			raise 

	def printx (*args, flush=True, end="\n"):
		print ("SERVER:", *args, flush=flush, end=end)

	
	def printException (message, text=None):
		Utils.printx ("EXCEPCION: ", message) 
		Utils.printx ("\tTEXT:", text)
		Utils.printx (traceback_format_exc())

	#-- Send exception info to file
	def logException (e, message=None):
		msg = ">>> Excepcion: " + message
		print (msg)
		exc_type, exc_value, exc_traceback = type(e), e, e.__traceback__
		with open("exception_log.txt", "a") as f:
			f.write (msg + "\n")
			f.write("Exception Type: {}\n".format(exc_type.__name__))
			f.write("Exception Value: {}\n".format(exc_value))
			f.write("Traceback:\n")
			traceback_str = "".join(traceback.format_tb(exc_traceback))
			f.write(traceback_str)
			f.write("\n")

	#-- Get value from dict fields [key] 
	def getValue (fields, key):
		try:
			return fields [key]["content"]
		except:
			Utils.printException ("EXEPCION: Obteniendo valor para la llave:", key)
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
		with open (outFilename, "w") as fp:
			json.dump (fieldsDict, fp, indent=4, default=str)

	def initDicToValue (dic, value):
		keys = dic.keys ()
		for k in keys:
			dic [k] = value
		return dic

	#-- Remove "." and "-XXX"
	def convertToEcuapassId (id):
		id = id.replace (".","")
		id = id.split ("-")[0]
		return id


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

