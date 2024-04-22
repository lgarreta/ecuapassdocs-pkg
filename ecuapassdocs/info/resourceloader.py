
import os, sys, json, traceback
from importlib import resources

# External packages
from PyPDF2 import PdfReader
from PIL import Image 

class ResourceLoader:
	def loadText (resourcePackage, resourceName):
		text = None
		resourcePackage = "ecuapassdocs.resources." + resourcePackage
		try:
			with resources.open_text (resourcePackage, resourceName, encoding="utf-8") as fp:
				text = fp.readlines()
		except:
			print (traceback.format_exc())

		return text

	def loadJson (resourcePackage,  resourceName):
		jsonDic = None
		resourcePackage = "ecuapassdocs.resources." + resourcePackage
		try:
			with resources.open_text (resourcePackage, resourceName, encoding="utf-8") as fp:
				jsonDic = json.load (fp)
		except:
			print (traceback.format_exc())
		return jsonDic

	def loadPdf (resourcePackage, resourceName):
		pdfObject = None
		resourcePackage = "ecuapassdocs.resources." + resourcePackage
		try:
			fp = resources.open_binary (resourcePackage, resourceName)
			pdfObject = PdfReader (fp)
		except:
			print (traceback.format_exc())

		return pdfObject

	def loadImage (resourcePackage, resourceName):
		imgObject = None
		resourcePackage = "ecuapassdocs.resources." + resourcePackage
		try:
			with resources.open_binary (resourcePackage, resourceName) as fp:
				imgObject = Image.open (fp)
		except:
			print (traceback.format_exc())

		return imgObject

	def get_resource_path (resource_name):
		return os.path.join('resources', resource_name)
