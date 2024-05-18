import os, re
from traceback import format_exc as traceback_format_exc

#-----------------------------------------------------------
#-- Class containing data for filling Ecuapass document
#-----------------------------------------------------------
class EcuData:
	temporalDir = None

	empresas = { 
		"BYZA": {
			'id'       : "BYZA",
			"nombre"   : "Grupo BYZA S.A.S.",
			"direccion": "Av. Coral y los Alamos",
			"idTipo"   : "RUC", 
			"idNumero" : "0400201414001",
			"modelCartaportes": "Model_02_Cartaportes_NTA_BYZA",
			"modelManifiestos": "Manifiestos_NTA_BYZA_Template",
			#"modelManifiestos": "Model_Manifiestos_NTA_BYZA_4",
			"modelDeclaraciones": None,
			"MRN": None,
			"MSN": None,
			"permisos" : {"originario":"PO-CO-0033-22", "servicios1": "PO-CO-0033-22"}
		},
		"BOTERO": {
			'id'     : "BOTERO",
			"nombre" : "EDUARDO BOTERO SOTO S.A.",
			"direccion": "Carrera 42 No 75-63 Aut. Sur, Itagui (Antioquia)",
			"idTipo" : "NIT", 
			"idNumero" : "890.901.321-5",
			"modelCartaportes": "Model_Cartaportes_Botero",
			"modelManifiestos": "Model_Manifiestos_Botero",
			"modelDeclaraciones": None,
			"MRN": None,
			"MSN": None,
		},
		"NTA" : { 
			'id'     : "NTA",
			"nombre" : "NUEVO TRANSPORTE DE AMERICA COMPAÑIA LIMITADA", 
			"direccion": "ARGENTINA Y JUAN LEON MERA - TULCAN",
			"idTipo" : "RUC", 
			"idNumero" : "1791834461001",
			"modelCartaportes": "Model_Cartaportes_NTA_BYZA",
			"modelManifiestos": "Manifiestos_NTA_BYZA_Template",
			"modelDeclaraciones": "Model_Declaraciones_NTA_Single",
			"MRN": "CEC202340350941",
			"MSN": "0001",
			"permisos" : {"originario":"C.I.-E.C.-0060-04",
				          "servicios1":"P.P.S.CO015905", "servicios2":"P.P.S.PE000210"}
		},
		"SILOGISTICA": {
			'id'     : "SILOGISTICA",
			"nombre": "PROVIZCAINO S.A.",
			"direccion": "ANTIZ Y 9 DE AGOSTO, CALDERÓN - QUITO",
			"idTipo": "RUC",
			"idNumero": "1791882253001",
			"modelCartaportes": "Model_Cartaportes_Silogistica",
			"modelManifiestos": "Model_Manifiestos_Silogistica",
			"modelDeclaraciones": "Model_Declaraciones_NTA_Single",
			"MRN": "||LOW",
			"MSN": "||LOW"
		},
		"SYTSA": {
			'id'     : "SYTSA",
			"nombre" : "TRANSPORTES Y SERVICIOS ASOCIADOS SYTSA CIA. LTDA",
			"direccion": "Panamericana norte, sector El Rosal, Tulcán",
			"idTipo" : "RUC", 
			"idNumero" : "1791770358001",
			"modelCartaportes": "Model_Cartaportes_NTA_SILOG",
			"modelManifiestos": "Model_Manifiestos_NTA",
			"modelDeclaraciones": "Model_Declaraciones_NTA_Single",
			"MRN": None,
			"MSN": None
		}
	}

	def getEmpresaInfo (empresaName):
		return EcuData.empresas [empresaName]

	def old_getEmpresaInfo (ecuapassName):
		empresa = {"nombre":None, "direccion":None, "idTipo": None,
		           "RUC": None, "idNumero":None, "MRN":None, "MSN":None}
		empresaName = None
		try:
			if "NUEVO TRANSPORTE DE AMERICA" in ecuapassName:
				empresaName = "N.T.A."
			elif "PROVIZCAINO" in ecuapassName:
				empresaName = "SILOGISTICA"

			empresa = EcuData.empresas [empresaName]
		except:
			print (f"EXCEPCION: Obteniendo datos de la empresa: {empresaName}")
			print (traceback_format_exc())
		return (empresa)

	def getEmpresaId (empresa):
		return EcuData.empresas[empresa]["numeroId"]

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	mainInfo ()
