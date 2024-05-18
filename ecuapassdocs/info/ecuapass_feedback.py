#!/usr/bin/env python3
"""
Send feedback (text and PDF file) to azure blob
"""

import os
from datetime import datetime

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from .ecuapass_utils import Utils

class EcuFeedback:
	#----------------------------------------------------------------
	#-- Get the blob client to write to Azure blob
	#----------------------------------------------------------------
	def getBlobClient (text_blob_name):
		# Azure Blob Storage container name
		container_name = "blobfeedback"

		# Azure Storage account connection string
		#connection_string = os.environ.get ("AZR_BLOB_CONN_STR")
		connection_string = "DefaultEndpointsProtocol=https;AccountName=lgformsstorage;AccountKey=BHsWkVaWQYStRq8FOpoIl0jI39W+WFvrSJmxesr0euIEJe+qkSi0LoTM0HZfyOn2XbYfnHir7CD8+ASt6ZJnwg==;EndpointSuffix=core.windows.net"

		# Initialize the BlobServiceClient
		blob_service_client = BlobServiceClient.from_connection_string (connection_string)

		# Create a container (if it doesn't exist)
		container_client = blob_service_client.get_container_client (container_name)
		blob_client = container_client.get_blob_client (text_blob_name)

		return (blob_client)

	#----------------------------------------------------------------
	# Send a text to blob
	#----------------------------------------------------------------
	def sendLog (empresa, filename):
		logMessage = f"LOG_{empresa}_{filename.split ('.')[0]}"
		print ("Sending log: ", logMessage)
		try:
			blob_client    = EcuFeedback.getBlobClient (f"{logMessage}")
			blob_client.upload_blob ("", overwrite=True)
		except: 
			print (f"No se pudo enviar el log'")

	#----------------------------------------------------------------
	# Send a file to blob
	#----------------------------------------------------------------
	def sendFile (empresa, docFilepath):
		# Upload PDF file as a blob
		filename    = os.path.basename (docFilepath)
		logFilename = f"LOG_{empresa}_{filename}"
		print ("Sending log file: ", logFilename)
		EcuFeedback.sendFileAsBytes (docFilepath, logFilename)
#		if docFilepath != None and os.path.exists (docFilepath):
#			pdf_blob_client = EcuFeedback.getBlobClient (logFilename)
#			with open(docFilepath, "rb") as pdf_file:
#				pdf_blob_client.upload_blob (pdf_file, overwrite=True)

	def sendFileAsBytes (docFilepath, logFilename):
		if docFilepath != None and os.path.exists (docFilepath):
			pdf_blob_client = EcuFeedback.getBlobClient (logFilename)
			with open(docFilepath, "rb") as pdf_file:
				pdf_blob_client.upload_blob (pdf_file, overwrite=True)

	#----------------------------------------------------------------
	# Send message and file from GUI 
	#----------------------------------------------------------------
	def sendFeedback (zipFilepath, docFilepath):
		try:
			print ("Enviando retroalimentación: ", zipFilepath) 
			# Upload text as a blob
			filename    = os.path.basename (docFilepath)
			logFilename = f"LOG_{filename}"
			EcuFeedback.sendFileAsBytes (zipFilepath, logFilename)

			#feedbackText = EcuFeedback.getTextFromZipFile (zipFilepath)
			#print ("--feedbackText: ", feedbackText)
			#fileSufix    = EcuFeedback.getCurrentDateTimeString ()

			#blob_client  = EcuFeedback.getBlobClient (f"feedback-{fileSufix}.txt")
			#blob_client.upload_blob (feedbackText, overwrite=True)

			#EcuFeedback.sendPdfFile (docFilepath)	

			return (f"Retroalimentación en la nube: Documento {docFilepath}")
		except:
			Utils.printException (f"No se pudo enviar retroalimentación")

		return None

	#----------------------------------------------------------------
	# Get the text as zip file from GUI
	#----------------------------------------------------------------
	def getTextFromZipFile (zip_file_path):
		import zipfile
		import io

		try:
			# Open the ZIP file for reading
			with zipfile.ZipFile (zip_file_path, 'r') as zip_file:
				# Extract the first (and only) file from the ZIP archive
				file_info = zip_file.infolist()[0]
				extracted_text = zip_file.read(file_info.filename).decode('utf-8')

			#print("Extracted Text:")
			#print(extracted_text)
			return extracted_text

		except Exception as e:
			print("Error:", str(e))


	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getCurrentDateTimeString():
		current_datetime = datetime.now()
		formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H:%M:%S")
		return formatted_datetime

