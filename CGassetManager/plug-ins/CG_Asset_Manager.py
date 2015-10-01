#-------------------------------------------------------------------#
#                                                                   #
#                                                                   #
#                                                                   #
#                                                                   #
#   Maya UI script for saving, publishing, and uploading CG Assets  #
#   in an organized folder structure for each show that lives on    #
#   the server.                                                     #
#                                                                   #
#   Created by Jordan Alphonso on 9/28/2015                         #
#   email: jordan@pixelmagicfx.com                                  #
#   version: 1.0                                                    #
#                                                                   #
#                                                                   #
#                                                                   #
#                                                                   #
#-------------------------------------------------------------------#



import maya.OpenMaya as om
import maya.OpenMayaMPx as MPx
import sys
import os
import ctypes.wintypes
import CGAssetMang_v01 as CG_Asset
import maya.mel as mel
import maya.cmds as cmds


kPluginName = "CG_AM"

class AssetManager( MPx.MPxCommand ):

    #constructor
    def __init__(self):
        MPx.MPxCommand.__init__( self )

        #add env variable for maya scripts path
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 1   # Get current, not default value

        docs = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, docs)

        mayaENVfile = docs.value + "/maya/2016/Maya.env"

        os.chmod( mayaENVfile, 0o664 )
        mayaEnv = open( mayaENVfile, 'a' )
        mayaEnvR = open( mayaENVfile, 'r' )

        readEnv = mayaEnvR.readlines()
        lineSet = set(readEnv)

        newline = "MAYA_MODULE_PATH= C:\Program Files\Autodesk\Maya2016\plugin-ins\CGassetManager"
        newlineSpaces = "\n\nMAYA_MODULE_PATH= C:\Program Files\Autodesk\Maya2016\plugin-ins\CGassetManager"

        if not newline in lineSet:
            mayaEnv.writelines(newlineSpaces)

        mayaEnv.close()
        mayaEnvR.close()

        #rehash the maya script cache
        mel.eval( "rehash;" )

        if cmds.layout( "PM_plugins", exists=True ):
            pass
        else:
            mel.eval( "loadNewShelf \"shelf_PM_plugins\";" )





    #invoke manager when command is run
    def doIt(self, argList):

        #load the asset manager
        CG_Asset.CGAssets()



def cmdCreator():

    return MPx.asMPxPtr( AssetManager() )



def initializePlugin( mobject ):

    mplugin = MPx.MFnPlugin(mobject, "Jordan Alphonso", "1.0")

    try:
        mplugin.registerCommand( kPluginName, cmdCreator )
    except:
        sys.stderr.write( "Failed to load plugin " + kPluginName + "." )
        raise

def uninitializePlugin( mobject ):

    mplugin = MPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterCommand( kPluginName )
    except:
        sys.stderr.write( "Failed to unload plugin " + kPluginName + "." )





