This repository contains a python script, an ArcGIS Pro project file, and a list of feature classes and their stale dates. 
mrdouville 20190715

================================================================================
README: Feature Class upload process for ArcGIS Online - Wildfire 
================================================================================

Prepared by: Michelle Douville (michelle.douville@gov.bc.ca)

## Table of Contents

### Section 1. Overview (of the Feature Class upload to ArcGIS Online Process)
### Section 2. ArcGIS Pro Project File
### Section 3. Running the python upload Process (instructions)

	

### Section 1. Overview (of the Feature Class upload to ArcGIS Online Process)
--------------------------------------------------------------------------------
The goal of the project is to contain the configs for pushing ArcGIS feature class to ArcGIS Online. 
Two ArcGIS Online Items are created a service defintion and a feature layer type. 
All of the items are put into one folder see - "ago_feature_layers_hosted_active" - https://governmentofbc.maps.arcgis.com/home/content.html?folder=0349d0b89f6a4609b96616d42ddc67c6
Based on the stale minutes, for each feature class list in /layers_for_ago2.txt file
A Jenkins job will run the python script to upload the data. See the Jenkinsfile here - /Jenkinsfile (This could be scheduled to run every 30 minutes :25 and :55 past the hour. 

    
### Section 2. ArcGIS Pro Project File
--------------------------------------------------------------------------------
An ArcGIS Pro project (ie. /fc2ago_wildfire.aprx) would need to be authored that contains the data to push to ArcGIS Online.. 
    
### Section 3. Running the python upload Process (instructions)
--------------------------------------------------------------------------------
    
To run the job manually you will need Python 3 and ARCPY you can run the script at a command prompt like this: 
    
    E:\sw_nt\ArcGIS\Pro2\bin\Python\envs\arcgispro-py3\python.exe fc2ago-cron.py -pwd *[password of AGO USER]* -path *[full path and filename of aprx ArcGIS Pro project file]* -fcs *[text file that describes the feature layers to upload]*
    
    
#### Example script call:
    E:\sw_nt\ArcGIS\Pro2\bin\Python\envs\arcgispro-py3\python.exe fc2ago-cron.py -pwd [password of AGO USER] -path E:/sw_nt/jenkins/workspace/waops/fc2ago-wildfire/fc2ago_wildfire.aprx -fcs layers_for_ago2.txt 
    
The text file that describes the feature layers to upload has several columns that are delimited by a semi-colon. 
The first column describes the time and stale minutes, at the moment only the stale minutes are used and not the cron expression. 
The second column is the feature title that is given in the Arc Pro Project (the must match) and AGO Item. 
The Third column contains the BC Data Catalogue URL, if it exists.
The Fourth column contains the AGO Item URL, this MUST exist prior to running the script (1st initial upload must be done manually at the moment). 
    
####Example line: 
    *32    ;10;Fire Locations Current;http://catalogue.data.gov.bc.ca/dataset/2790e3f7-6395-4230-8545-04efb5a18800;https://governmentofbc.maps.arcgis.com/home/item.html?id=7cda51ae6ab447dc9de72ac34332d1c1*
    

