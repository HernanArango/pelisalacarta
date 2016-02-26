#! /usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta
# Launcher
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import os, sys, socket
sys.dont_write_bytecode = True

from core import logger
from core import config
from core.item import Item
import threading
from threading import Thread
from platformcode import launcher
from platformcode import platformtools

sys.argv ={}
sys.path.append (os.path.join( config.get_runtime_path(),'lib'))
PORT=int(config.get_setting("server.port"))
WebsocketPort=int(config.get_setting("websocket.port")) 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 53))  # connecting to a UDP address doesn't send packets
myip = s.getsockname()[0]

from functools import wraps
def ThreadNameWrap(func):
    @wraps(func)
    def bar(*args, **kw):
        if not "name" in kw:
          kw['name'] = threading.current_thread().name
        return func(*args, **kw)
    return bar
threading.Thread.__init__ = ThreadNameWrap(threading.Thread.__init__)

 
def ReloadModules():
  if 0:
    import inspect
    #Recorre los modulos cargados en memoria
    for module in sys.modules.keys():
      if inspect.ismodule(sys.modules[module]):
        #Recarga todos los modulos excepto los loggers.
        if config.get_runtime_path() in str(sys.modules[module]) and not "__main__" in str(sys.modules[module]) and not "logger" in str(sys.modules[module]) and not "library_service" in str(sys.modules[module]):
          reload(sys.modules[module])


def ProcessRequest(ID):
  sys.argv[ID]["host"] = "http://"+ myip + ":" + str(PORT)
  ReloadModules()
          
  try:
    if sys.argv[ID]["request"]:
      item = Item()
      item.fromurl(sys.argv[ID]["request"])
    else:
      item = Item(channel="channelselector", action="mainlist")
    launcher.run(item)



  except Exception as e:
    import traceback
    logger.error(traceback.format_exc())
    from core import scrapertools
    patron = 'File "'+os.path.join(config.get_runtime_path(),"channels","").replace("\\","\\\\")+'([^.]+)\.py"'
    canal = scrapertools.find_single_match(traceback.format_exc(),patron)
    if canal:
      platformtools.dialog_ok(
        "Se ha producido un error en el canal " + canal,
        "Esto puede ser devido a varias razones: \n - El servidor no está disponible, o no esta respondiendo.\n - Cambios en el diseño de la web.\n - Etc...\nComprueba el log para ver mas detalles del error.")
    else:
      platformtools.dialog_ok(
        "Se ha producido un error en pelisalacarta",
        "Comprueba el log para ver mas detalles del error." )

def MostrarInfo():
    os.system('cls' if os.name == 'nt' else 'clear')
    print ("--------------------------------------------------------------------")
    print ("Pelisalacarta Iniciado")
    print ("La URL para acceder es http://" + myip + ":" + str(PORT))
    print ("WebSocket Server iniciado en ws://"+ myip + ":" + config.get_setting("websocket.port")+"/")
    print ("--------------------------------------------------------------------")
    print ("Runtime Path      : " + config.get_runtime_path())
    print ("Data Path         : " + config.get_data_path())
    print ("Download Path     : " + config.get_setting("downloadpath") )
    print ("DownloadList Path : " + config.get_setting("downloadlistpath"))
    print ("Bookmark Path     : " + config.get_setting("bookmarkpath"))  
    print ("Library Path      : " + config.get_setting("library_path"))  
    print ("--------------------------------------------------------------------")
    conexiones = []
    for a in sys.argv:
      conexiones.append(sys.argv[a]["socket"].client.getpeername()[0])
    if len(conexiones) >0:
      print ("Clientes conectados:")
      for conexion in conexiones:
        print (conexion)
    else:
      print ("No hay conexiones")


def start():
  logger.info("pelisalacarta server init...")
  import services
  config.verify_directories_created() 
  try: 
      import HTTPServer
      HTTPServer.start()
      import WebSocket
      WebSocket.start(ProcessRequest,MostrarInfo)
      
      # Da por levantado el servicio
      logger.info("--------------------------------------------------------------------")
      logger.info("Pelisalacarta Iniciado")
      logger.info("La URL para acceder es http://" + myip + ":" + str(PORT))
      logger.info("WebSocket Server iniciado en ws://"+ myip + ":" + str(WebsocketPort))
      logger.info("--------------------------------------------------------------------")
      logger.info("Runtime Path      : " + config.get_runtime_path())
      logger.info("Data Path         : " + config.get_data_path())
      logger.info("Download Path     : " + config.get_setting("downloadpath") )
      logger.info("DownloadList Path : " + config.get_setting("downloadlistpath"))
      logger.info("Bookmark Path     : " + config.get_setting("bookmarkpath"))
      logger.info("Library Path      : " + config.get_setting("librarypath"))
      logger.info("--------------------------------------------------------------------")
      MostrarInfo()
      
      Start = True
      import time
      while Start:
        time.sleep(1)
        
  except KeyboardInterrupt:
      print 'Deteniendo el servidor HTTP...'
      HTTPServer.stop()
      print 'Deteniendo el servidor WebSocket...'
      WebSocket.stop()
      print 'Pelisalacarta Detenido'
      Start= False

#Inicia pelisalacarta
start()
