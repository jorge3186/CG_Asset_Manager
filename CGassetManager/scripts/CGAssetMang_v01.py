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

import maya.cmds as cmds
import maya.mel as mel
import os
import sys
import datetime
import shutil
from functools import partial




#which os am i on?
mayaPath = ''

if os.name == 'nt':
    mayaPath = 'C:/Program Files/Autodesk/Maya2016/'
else:
    mayaPath = '/Applications/Autodesk/maya2016/'




#hard coded variables
ripleyPath = "//core/ripley/"
iconPath = mayaPath+"plug-ins/CGassetManager/icons"


helpText = ["This is an asset mananger for all cg assets coming into and out of each\n"+
            "project. Select which project your asset is for, then choose the appropriate\n"+
            "sub categories, and finally type your name into the artist box.\n\n"+
            "When starting a new version of your asset, you will be asked to build the\n"+
            "designed file structure. In doing so, this plugin will take your current\n"+
            "scene and save the file as it's new name, export out all geometry as OBJ files\n"+
            "and export all texture files into their appropriate folders. That being said, \n"+
            "please be mindful that the name of your geometry in the scene is going to\n"+
            "be the same name that is given to the OBJ file. The same goes for your\n"+
            "textures. So, please be organized and name all things accordingly so your \n"+
            "project does not get messy.\n\n"+
            "When loading existing projects, you will also be asked if you would like to\n"+
            "version up or just continue working on the current version. Remember that \n"+
            "versions are free, so when in doubt just version up and continue working.\n\n"+
            "This plugin is designed so artists will have freedom from keeping track of\n"+
            "current assets, updated textures, modeling tweaks, etc. You should no\n"+
            "longer need to save and load projects from the File menu inside Maya.\n"+
            "Everything you need is provided in this plugin, whether you are starting\n"+
            "a new asset, or continuing one from another day.\n\n"+
            "That is all, and may the force be with you."]




class CGAssets():

    #constructor
    def __init__( self ):

        #create dictionary for access to local variables
        self.widgets = {}

        #call the UI function
        self.CGAsset_UI()



    def CGAsset_UI( self ):

        #if window exists, then delete it.
        if cmds.window( "mainWindow", exists=True ):
            cmds.deleteUI( "mainWindow" )

        #create main window
        self.widgets[ "mainWindow" ] = cmds.window( "mainWindow", title='CG Asset Manager | v1.0', mnb=False, mxb=False, sizeable=False )
        cmds.window( self.widgets[ "mainWindow" ], edit=True, h=410, w=400 )

        self.widgets[ "tabLayout" ] = cmds.tabLayout()

        self.widgets[ "mainLayout" ] = cmds.columnLayout( "Asset Manager", p=self.widgets[ "tabLayout" ] )

        self.widgets[ "helpTab" ] = cmds.columnLayout( "Help", p=self.widgets[ "tabLayout" ], co=('both', 5), w=400,columnAlign='left' )
        cmds.separator( h=10, p=self.widgets[ "helpTab" ] )
        cmds.text( helpText, p=self.widgets[ "helpTab" ])

        #banner image
        cmds.image( "banner", image=iconPath+"/banner_2016.jpg", p=self.widgets[ "mainLayout" ] )

        #option menu for projects
        self.widgets[ "uiLayout" ] = cmds.columnLayout( "uiLayout", w=400, co=('both', 15), p=self.widgets[ "mainLayout" ] )
        cmds.separator( h=15 )
        self.widgets[ "ProjectOptionWidget" ] = cmds.optionMenu( label="Project:  ", w=370, cc=self.populateAssets )

        #option menu for assets
        cmds.separator( h=15 )
        self.widgets[ "AssetOptionWidget" ] = cmds.optionMenu( label="Asset:    ", w=370, cc=self.populateJobs )

        #option menu for job
        cmds.separator( h=15 )
        self.widgets[ "jobLayout" ] = cmds.rowColumnLayout( w=370, numberOfColumns=2, columnWidth=[(1, 339),(2, 20)], co=(2, 'left', 10) )
        self.widgets[ "assetJobMenu" ] = cmds.optionMenu( label='Job:       ', cc=self.populateVersions )
        self.widgets[ "assetJobButton" ] = cmds.button( label='+', w=20, h=22, c=self.createJobButton )

        #option menu for version folders
        cmds.columnLayout(p=self.widgets[ "uiLayout" ])
        cmds.separator( h=15 )
        tempRCLayout = cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[( 1, 140 ), (2, 20), (3, 55), (4, 152)], co=[(2, 'left', 10), (3, 'left', 20)])
        self.widgets[ "versionMenu" ] = cmds.optionMenu( label='Version: ', cc=self.versionUpdate )
        self.widgets[ "addVersionButton" ] = cmds.button( label="+", w=20, c=self.addVersionButton )
        self.widgets[ "artistText" ] = cmds.text( "Artist: " )
        self.widgets[ "artistTextField" ] = cmds.textField( text='', editable=True )


        #create build and load buttons
        cmds.columnLayout( p=self.widgets[ "uiLayout" ] )
        cmds.separator( h=15 )
        self.widgets[ "largeButtonLayout" ] = cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[( 1, 184 ), (2, 184)], co=( 1, 'right', 20 ) )
        cmds.rowColumnLayout( self.widgets[ "largeButtonLayout" ], edit=True )
        self.widgets[ "buildButton" ] = cmds.button( label='BUILD', enable=False, h=50, w=174, c=self.buildButton )
        self.widgets[ "loadButton" ] = cmds.button( label='LOAD', enable=False, h=50, w=174, c=self.loadButton )

        #progress bar
        cmds.columnLayout( p=self.widgets[ "uiLayout" ] )
        cmds.separator( h=10 )
        self.widgets[ "progressBar" ] = cmds.progressBar( step=1, w=370, enable=False )

        #progress Bar Text
        cmds.columnLayout( p=self.widgets[ "uiLayout" ] )
        self.widgets[ "progressBarText" ] = cmds.text( label='', align='center', w=365 )

        #populate Projects
        self.populateProjects()

        #populate assets
        projectsList = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], query=True, itemListLong=True )
        if projectsList != None:
            self.populateAssets()

        #populate jobs
        assetsList = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], query=True, itemListLong=True )
        if assetsList != None:
            self.populateJobs()

        #populate versions
        jobsList = cmds.optionMenu( self.widgets[ "assetJobMenu" ], query=True, itemListLong=True )
        if jobsList != None:
            self.populateVersions()

        #show window
        cmds.showWindow( self.widgets[ "mainWindow" ] )



    def populateVersions( self, *args ):

        #clear the VERSION item list when changing assets
        menuItems = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, itemListLong=True )
        if menuItems != None:
            for item in menuItems:
               cmds.deleteUI( item )

        #empty versions list
        versions = []

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get current job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True )

        #directory for versions
        versionDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+currentAsset+"/"+currentJob

        if os.path.exists( versionDir ):

            vList = os.listdir( versionDir )
            for v in vList:
                versions.append( v )


            for version in versions:
                cmds.menuItem( label=version, p=self.widgets[ "versionMenu" ] )


        if currentJob == "Create New Job":
            cmds.button( self.widgets[ "assetJobButton" ], edit=True, enable=True )
            cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, enable=False )
            cmds.button( self.widgets[ "addVersionButton" ], edit=True, enable=False )
            cmds.button( self.widgets[ "buildButton" ], edit=True, enable=False )
            cmds.button( self.widgets[ "loadButton" ], edit=True, enable=False )

        else:
            cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, enable=True )
            cmds.button( self.widgets[ "assetJobButton" ], edit=True, enable=False )
            cmds.button( self.widgets[ "addVersionButton" ], edit=True, enable=True )



        #alway select most recent version
        versionList = []

        #scan versions dir
        if os.path.exists( versionDir ):
            jobList = os.listdir( versionDir )
            for d in jobList:
                versionList.append(d)

            #latest version folder
            latestVer = len(versionList)
            paddedNumber = '%03d' % latestVer
            verFolder = "v"+str(paddedNumber)

            cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, value=verFolder )


        #check to see if maya file exists
        if os.path.exists( versionDir ):
            curVer = cmds.optionMenu( self.widgets[ "versionMenu" ], query=True, value=True )
            mayaPath = versionDir+"/"+curVer+"/maya_files"

            if len(os.listdir(mayaPath)) == 0:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=True )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=False )
            else:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=False )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=True )


    def versionUpdate( self, *args ):

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get current job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True )

        #directory for versions
        versionDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+currentAsset+"/"+currentJob


        #check to see if maya file exists
        if os.path.exists( versionDir ):
            curVer = cmds.optionMenu( self.widgets[ "versionMenu" ], query=True, value=True )
            mayaPath = versionDir+"/"+curVer+"/maya_files"

            if len(os.listdir(mayaPath)) == 0:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=True )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=False )
            else:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=False )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=True )

         #check to see if maya file exists
        if os.path.exists( versionDir ):
            curVer = cmds.optionMenu( self.widgets[ "versionMenu" ], query=True, value=True )
            mayaPath = versionDir+"/"+curVer+"/maya_files"

            if len(os.listdir(mayaPath)) == 0:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=True )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=False )
            else:
                cmds.button( self.widgets[ "buildButton" ], edit=True, enable=False )
                cmds.button( self.widgets[ "loadButton" ], edit=True, enable=True )




    def populateJobs( self, *args ):

        #clear the JOB item list when changing assets
        menuItems = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, itemListLong=True )
        if menuItems != None:
            for item in menuItems:
               cmds.deleteUI( item )

        #job list
        jobs = []

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get asset path
        currentAssetDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)

        if os.path.exists( currentAssetDir ):

            #populate Jobs
            files = os.listdir( currentAssetDir )
            for file in files:
                jobs.append( file )

        jobs.append( "Create New Job" )

        for job in jobs:
            cmds.menuItem( label=job, p=self.widgets[ "assetJobMenu" ] )

        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], query=True, value=True )
        if currentJob == "Create New Job":
            cmds.button( self.widgets[ "assetJobButton" ], edit=True, enable=True )
        else:
            cmds.button( self.widgets[ "assetJobButton" ], edit=True, enable=False )

        #update versions
        self.populateVersions()




    def populateAssets( self, *args ):

        #clear the ASSET item list when changing projects
        AmenuItems = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, itemListLong=True )
        if AmenuItems != None:
            for item in AmenuItems:
               cmds.deleteUI( item )

        #clear the JOB item list when changing projects
        JmenuItems = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, itemListLong=True )
        if JmenuItems != None:
            for item in JmenuItems:
               cmds.deleteUI( item )

        #clear the VERSION item list when changing projects
        VmenuItems = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, itemListLong=True )
        if VmenuItems != None:
            for item in VmenuItems:
               cmds.deleteUI( item )

        assets = []


        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #path to current assets
        currentAssetsDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"
        if os.path.exists( currentAssetsDir ):

            cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], edit=True, enable=True )
            cmds.optionMenu( self.widgets[ "assetJobMenu" ], edit=True, enable=True )
            cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, enable=True )
            cmds.text( self.widgets[ "artistText" ], edit=True, enable=True )
            cmds.textField( self.widgets[ "artistTextField" ], edit=True, enable=True )
            cmds.button( self.widgets[ "addVersionButton" ], edit=True, enable=True )
            files = os.listdir(currentAssetsDir)
            for file in files:
                assets.append(file)

            #add assets to list
            for asset in assets:
                cmds.menuItem( label=asset, p=self.widgets[ "AssetOptionWidget" ] )

            #update jobs and versions
            assetsList = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], query=True, itemListLong=True )
            if assetsList != None:
                self.populateJobs()
            jobsList = cmds.optionMenu( self.widgets[ "assetJobMenu" ], query=True, itemListLong=True )
            if jobsList != None:
                self.populateVersions()


        else:
            cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], edit=True, enable=False )
            cmds.optionMenu( self.widgets[ "assetJobMenu" ], edit=True, enable=False )
            cmds.button( self.widgets[ "assetJobButton" ], edit=True, enable=False )
            cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, enable=False )
            cmds.text( self.widgets[ "artistText" ], edit=True, enable=False )
            cmds.textField( self.widgets[ "artistTextField" ], edit=True, enable=False )
            cmds.button( self.widgets[ "addVersionButton" ], edit=True, enable=False )
            cmds.button( self.widgets[ "buildButton" ], edit=True, enable=False )
            cmds.button( self.widgets[ "loadButton" ], edit=True, enable=False )
            cmds.warning( "Missing directory. For example, there should be a directory path of //core/ripley/<Project Name>/09_CG_RnD/CG_Assets/" )



    def populateProjects( self, *args ):

        #create a list of projects on server
        serverList = os.listdir(ripleyPath)

        projectDir = []

        #list projects on server
        for path in serverList:
            rndPath = ripleyPath+path+"/09_CG_RnD"

            if os.path.exists(rndPath) == True:
                projectDir.append(path)

        #remove template folder from project list
        projectDir.remove("rev_template")

        #add menu item for each project in list
        for i in projectDir:
            cmds.menuItem( label=i, parent=self.widgets[ "ProjectOptionWidget" ] )



    def createJobButton( self, *args ):

        if cmds.window( "newJobWindow", exists=True ):
            cmds.deleteUI( "newJobWindow" )

        #create new job window
        self.widgets[ "newJobWindow" ] = cmds.window( "newJobWindow", title='Create New Job', w=300, mnb=False, mxb=False, sizeable=False )
        cmds.window( self.widgets[ "newJobWindow" ], edit=True, h=100 )
        cmds.columnLayout( co=( 'both', 10 ), h=100 )
        cmds.separator( h=10 )
        cmds.text( "Please enter the name of the job you want to create." )
        cmds.separator( h=10 )
        self.widgets[ "newJobTextField" ] = cmds.textField( text='', editable=True, w=280 )
        cmds.separator( h=10 )
        buttonLayout = cmds.rowColumnLayout( numberOfColumns=2, co=[ (1, 'both', 5), (2, 'both', 5) ], h=50 )
        cmds.button( label='Create',w=130, p=buttonLayout, c=self.newJobMenuCreate )
        cmds.button( label='Cancel',w=130, p=buttonLayout, c=self.newJobMenuCancel )

        cmds.showWindow( self.widgets[ "newJobWindow" ] )



    def newJobMenuCancel( self, *args ):

        #kill the window
        cmds.deleteUI( self.widgets[ "newJobWindow" ] )

    def newJobMenuCreate( self, *args ):

        #get text from job textfield
        newJobTitle = cmds.textField( self.widgets[ "newJobTextField" ], q=True, text=True )

        if newJobTitle != "":
            if cmds.window( "confirmWindow", exists=True ):
                cmds.deleteUI( "confirmWindow" )

            #are you sure?
            self.widgets[ "confirmWindow" ] = cmds.window( "confirmWindow", title='Confirm Job?', mnb=False, mxb=False, sizeable=False )
            cmds.columnLayout( co=( 'both', 10 ), h=70 )
            cmds.window( self.widgets[ "confirmWindow" ], edit=True, h=70, w=150 )
            cmds.separator( h=5 )
            cmds.text( 'Create job "' +newJobTitle+ '"?' )
            cmds.separator( h=10 )
            cmds.rowColumnLayout( numberOfColumns=2, co=[ (1, 'both', 5), (2, 'both', 5) ] )
            cmds.button( label='Create', w=90, c=self.confirmJobCreate )
            cmds.button( label='Cancel', w=90, c=self.confirmJobCancel )

            cmds.showWindow( self.widgets[ "confirmWindow" ] )

        else:
            cmds.warning( "There is no job title." )





    def confirmJobCancel( self, *args ):

        #kill the window
        cmds.deleteUI( self.widgets[ "confirmWindow" ] )



    def confirmJobCreate( self, *args ):


        #sub directories
        subDirs = [
            'maya_files',
            'textures',
            'mari_archives',
            'exports',
            'scripts',
            'notes'
        ]


        #get text from job textfield
        newJobTitle = cmds.textField( self.widgets[ "newJobTextField" ], q=True, text=True )

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #current asset directory
        currentAssetDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)

        #newJob directory
        newJobDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(newJobTitle)

        #create new job directory
        os.makedirs(newJobDir)

        #create v001 directory with sub directories inside
        os.makedirs(newJobDir+"/v001")
        for sub in subDirs:
            os.makedirs( newJobDir+"/v001/"+sub )

        #clear and reload menu items in job list
        menuItems = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, itemListLong=True )
        if menuItems != None:
            for menu in menuItems:
                cmds.deleteUI(menu)

        jobs = []

        if os.path.exists(newJobDir):
            cmds.optionMenu( self.widgets[ "assetJobMenu" ], edit=True, enable=True )
            files = os.listdir(currentAssetDir)
            for file in files:
                jobs.append(file)
            jobs.append( "Create New Job" )

        #add assets to Job menu
        for job in jobs:
            cmds.menuItem( label=job, p=self.widgets[ "assetJobMenu" ] )

        #kill both job create windows
        cmds.deleteUI( self.widgets[ "confirmWindow" ])
        cmds.deleteUI( self.widgets[ "newJobWindow" ])

        #update versions and jobs
        self.populateVersions()

        #make recently created the selected job
        cmds.optionMenu( self.widgets[ "assetJobMenu" ], edit=True, value=newJobTitle )


    def addVersionButton( self, *args ):

        #sub directories
        subDirs = [
            'maya_files',
            'textures',
            'mari_archives',
            'exports',
            'scripts',
            'notes'
        ]


        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get curent job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True  )

        #version directory
        versionDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"

        #empty version list
        versionList = []

        #scan versions
        jobList = os.listdir( versionDir )
        for d in jobList:
            versionList.append(d)

        #new version folder
        newVer = len(versionList)+1
        paddedNumber = '%03d' % newVer
        newVerFolder = "v"+str(paddedNumber)

        #create version directory with sub directories inside
        newDir = versionDir+"/"+newVerFolder
        os.makedirs( str(newDir) )
        for sub in subDirs:
            os.makedirs( newDir+"/"+sub )


        #clear and reload menu items in job list
        menuItems = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, itemListLong=True )
        if menuItems != None:
            for menu in menuItems:
                cmds.deleteUI(menu)

        self.populateVersions()

        #make recently created the selected job
        cmds.optionMenu( self.widgets[ "versionMenu" ], edit=True, value=newVerFolder )



    def buildButton( self, *args ):

        #get artist name
        artistName = cmds.textField( self.widgets[ "artistTextField" ], query=True, text=True )

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get curent job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True  )

        #get curent version
        currentVersion = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, v=True  )

        #export Directory
        exportDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/exports"

        #texture directory
        textureDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/textures"

        #mayaPath directory
        mayaDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/maya_files"

        #notes directory
        notesDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/notes"



        #get list of all geometry in scene
        geoList = cmds.ls( type='mesh')
        geoLength = len( geoList )

        #get list of all textures in scene
        textureList = cmds.ls( type='file' )
        textureLength = len( textureList )

        #full length of export list
        exportLength = textureLength + geoLength




        #export all and save scene
        artist = cmds.textField( self.widgets[ "artistTextField" ], query=True, text=True )
        if artist != "":

            #-----------------------------------------------#
            #                   SCENE SAVE                  #
            #-----------------------------------------------#
            i=1
            cmds.progressBar( self.widgets[ "progressBar" ], edit=True, maxValue=10000 )

            for i in range(1, 10000):
                cmds.text( self.widgets[ "progressBarText" ], edit=True, label="Saving Scene File." )
                cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=i )
                i=i+1
            cmds.file( rename=mayaDir+"/"+currentJob+"_"+currentVersion+".mb" )
            cmds.file( save=True, type='mayaBinary' )

            cmds.text( self.widgets[ "progressBarText" ], edit=True, label="" )
            cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=0 )





            #-----------------------------------------------#
            #                   GEO EXPORT                  #
            #-----------------------------------------------#
            g=1

            if geoLength > 0:

                try:
                    cmds.progressBar( self.widgets[ "progressBar" ], edit=True, maxValue=geoLength )
                    cmds.select( geoList )
                    for geo in geoList:
                        if cmds.file( exportDir+"/"+geo+'.obj', query=True, exists=True ):
                            pass
                        else:
                            cmds.text( self.widgets[ "progressBarText" ], edit=True, label="Exporting Geo " + str(g) + " of " + str(geoLength) + "." )
                            g= g+1
                            cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=g )
                            cmds.file( exportDir+"/"+geo+'.obj', exportSelected=True, type='OBJexport', force=True )

                    cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=0 )
                    cmds.text( self.widgets[ "progressBarText" ], edit=True, label="" )

                    #kill all .mtl files
                    OBJList = os.listdir( exportDir )
                    for mtl in OBJList:
                        if mtl.endswith( ".mtl" ):
                            os.remove( exportDir+"/"+mtl )
                except:
                    raise


            else:
                cmds.warning( "There is no geometry in the scene." )






            #-----------------------------------------------#
            #               TEXTURE EXPORT                  #
            #-----------------------------------------------#

            t=1
            tFiles = []

            cmds.filePathEditor( refresh=True )

            if textureLength > 0:

                try:
                    cmds.select( textureList )
                    cmds.progressBar( self.widgets[ "progressBar" ], edit=True, maxValue=textureLength )

                    directories = cmds.filePathEditor( query=True, listDirectories="" )
                    for d in directories:
                        fileName = cmds.filePathEditor( query=True, listFiles=d )
                        for f in fileName:
                            fullTexturePath = str(d+"/"+f)
                            tFiles.append(fullTexturePath)


                    #copy files from previous folder to correct destination
                    for tex in tFiles:
                        cmds.text( self.widgets[ "progressBarText" ], edit=True, label="Exporting Texture " + str(t) + " of " + str(textureLength) + "." )
                        cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=t )
                        if os.path.exists(tex):
                            shutil.copy( tex,  textureDir+"/")
                        t=t+1

                    #reload textures from current assset folder
                    for t in textureList:
                        cmds.filePathEditor( t+".fileTextureName", repath=textureDir+"/", force=True )

                except:
                    raise

            else:
                cmds.warning("Therer are no textures in your scene.")


            cmds.progressBar( self.widgets[ "progressBar" ], edit=True, progress=0 )
            cmds.text( self.widgets[ "progressBarText" ], edit=True, label="" )





            #-----------------------------------------------#
            #                     NOTES                     #
            #-----------------------------------------------#
            textureExport = os.listdir( textureDir )
            textureExportLength = len(textureExport)


            notesFile = open( notesDir+"/"+currentJob+"_"+currentVersion+".rtf", 'w' )

            notes = []
            notes.append( "Date: "+str(datetime.date.today())+"\n" )
            notes.append( "\n" )
            notes.append( "Time: "+str(datetime.datetime.now().time())+"\n" )
            notes.append( "\n" )
            notes.append( "Artist: "+artistName+"\n" )
            notes.append( "\n" )
            notes.append( "Number of meshes exported to OBJ format = "+ str(geoLength)+":\n" )
            for geo in geoList:
                notes.append( geo+"\n" )
            notes.append( "\n" )
            notes.append( "\n" )
            notes.append( "\n" )
            notes.append( "Number of textures exported from scene = "+str(textureExportLength)+":\n" )
            for t in textureExport:
                notes.append( t+"\n" )
            notes.append( "\n" )

            notesFile.writelines( notes )

            notesFile.close();



            #update version list
            self.populateVersions()

        #if no name is entered in to the artist field
        else:
            cmds.warning( "Please enter your name in the artist field." )



    def loadButton( self, *args ):

        #get artist name
        artistName = cmds.textField( self.widgets[ "artistTextField" ], query=True, text=True )

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get curent job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True  )

        #get curent version
        currentVersion = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, v=True  )

        #export Directory
        exportDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/exports"

        #texture directory
        textureDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/textures"

        #mayaPath directory
        mayaDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/maya_files"

        #notes directory
        notesDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/notes"

        #versions list
        versionFolders = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)
        versionList = os.listdir(versionFolders)

        #new version folder
        newVer = len(versionList)+1
        paddedNumber = '%03d' % newVer
        newVerFolder = "v"+str(paddedNumber)

        if artistName != "":
            try:
                if cmds.window( "versionUpWindow", exists=True ):
                    cmds.deleteUI( "versionUpWindow" )

                self.widgets[ "versionUpWindow" ] = cmds.window( "versionUpWindow", title="Version Up?", sizeable=False, mnb=False, mxb=False )
                cmds.window( self.widgets[ "versionUpWindow" ], edit=True, w=300, h=100 )
                cmds.columnLayout()
                cmds.separator( h=10 )
                cmds.text( "Would you like to create a " + newVerFolder + "\nor continue working from " + currentVersion + "?", align='center', w=300)

                cmds.separator( h=10 )
                cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[( 1, 135 ), ( 2, 135 )], co=[(1, "left", 7), (2, "left", 20)], w=300 )
                cmds.button( label=("Create "+ str(newVerFolder)+ "?"), w=135, h =30, c=self.versionUpCreate)
                cmds.button( label="Load Current", w=135, h =30, c=self.versionUpCancel)


                cmds.showWindow( self.widgets[ "versionUpWindow" ] )
            except:
                raise

        else:
            cmds.warning( "Please enter your name in the artist field" )



    def versionUpCancel( self, *args ):

        #get artist name
        artistName = cmds.textField( self.widgets[ "artistTextField" ], query=True, text=True )

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get curent job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True  )

        #get curent version
        currentVersion = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, v=True  )

        #export Directory
        exportDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/exports"

        #texture directory
        textureDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/textures"

        #mayaPath directory
        mayaDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/maya_files/"

        #current maya file
        mayaFile = mayaDir+currentJob+"_"+currentVersion+".mb"


        #load file
        existingFile = cmds.file( query=True, sceneName=True )

        if mayaFile != existingFile:
            cmds.file( mayaFile, open=True, force=True )

        else:
            cmds.warning( "The file is already loaded." )

        #close the UI after complete
        cmds.deleteUI( self.widgets[ "versionUpWindow" ] )


    def versionUpCreate( self, *args ):

        #get artist name
        artistName = cmds.textField( self.widgets[ "artistTextField" ], query=True, text=True )

        #get current project
        currentProject = cmds.optionMenu( self.widgets[ "ProjectOptionWidget" ], q=True, v=True )

        #get curent asset
        currentAsset = cmds.optionMenu( self.widgets[ "AssetOptionWidget" ], q=True, v=True  )

        #get curent job
        currentJob = cmds.optionMenu( self.widgets[ "assetJobMenu" ], q=True, v=True  )

        #get curent version
        currentVersion = cmds.optionMenu( self.widgets[ "versionMenu" ], q=True, v=True  )

        #export Directory
        exportDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/exports"

        #texture directory
        textureDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/textures"

        #mayaPath directory
        mayaDir = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)+"/"+str(currentVersion)+"/maya_files/"

        #versions list
        versionFolders = ripleyPath+currentProject+"/09_CG_RnD/CG_Assets/"+str(currentAsset)+"/"+str(currentJob)
        versionList = os.listdir(versionFolders)

        #new version folder
        newVer = len(versionList)+1
        paddedNumber = '%03d' % newVer
        newVerFolder = "v"+str(paddedNumber)

        #current maya file
        mayaFile = mayaDir+currentJob+"_"+currentVersion+".mb"
        newMayaFile = mayaDir+currentJob+"_"+newVerFolder+".mb"

        #kill the UI window
        cmds.deleteUI( self.widgets[ "versionUpWindow" ] )

        #version Up
        self.addVersionButton()

        #load and rename previous version to new version
        cmds.file( mayaFile, open=True, force=True )
        cmds.file( rename=newMayaFile )

        self.buildButton()




