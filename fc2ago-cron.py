## loop through layers_for_ago.txt file and prepare to push data up to ArcGIS Online
#E:\sw_nt\ArcGIS\Pro2\bin\Python\envs\arcgispro-py3\python E:\apps_data\userdata\scripts\public_2_ago\fc2ago.py -pwd xxxx -path E:/apps_data/userdata/scripts/public_2_ago/fc2ago_wildfire.aprx



import arcpy
from arcpy import AddMessage, AddError

import os, sys
import argparse
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import time
import datetime
import schedule
import requests
import json
import sys
import collections

def main():
    # -----------------------------------------------------------------------------
    # Constants
    # -----------------------------------------------------------------------------
    DEFAULT_AGO_PORTAL_URL = "https://governmentofbc.maps.arcgis.com" # Can also reference a local portal
    DEFAULT_AGO_PORTAL_USER = "AGO_USER_NONIDIR"
    DEFAULT_AGO_FOLDER = "ago_feature_layers_hosted_active"
    # -----------------------------------------------------------------------------
    # Parameters
    # -----------------------------------------------------------------------------
    argParser = argparse.ArgumentParser(description="Publishes Feature Classes from a ArcGIS Pro project and updates or creates new Feature Layer AGO Items")
    argParser.add_argument('-user', dest='user', action='store', default=DEFAULT_AGO_PORTAL_USER, required=False, help='the ArcGIS Online User to publish AGO Items with')
    argParser.add_argument('-pwd', dest='password', action='store', default=None, required=True, help='the ArcGIS Online User password')
    argParser.add_argument('-path', dest='prjPath', action='store', default=None, required=True, help='the full path and name to the ArcGIS Pro Project')
    argParser.add_argument('-portal', dest='portal', action='store', default=DEFAULT_AGO_PORTAL_URL, required=False, help='AGO portal URL')
    argParser.add_argument('-folder', dest='shrFolder', action='store', default=DEFAULT_AGO_FOLDER, required=False, help='The ID of the folder that contains all hosted items managed by this script')
    argParser.add_argument('-fcs', dest='fcs', action='store', default=None, required=True, help='The text file that contains a list of feature classes and update times i.e. E:/apps_data/userdata/scripts/public_2_ago/layers_for_ago2.txt')

    try:
       args = argParser.parse_args()
    except argparse.ArgumentError as e:
       argParser.print_help()
       sys.exit(1)

    start_time = time.time()
    now = time.ctime(int(start_time))
    print('Start Time: '+now)

    print('Connecting to {}'.format(args.portal))
    arcpy.SignInToPortal(args.portal, username=args.user, password=args.password)
    gis = GIS(url=args.portal, username=args.user, password=args.password, verify_cert=False )

    prjPath = args.prjPath.replace('/','\\')
    print('Open ArcPro Project '+prjPath)
    prj = arcpy.mp.ArcGISProject(prjPath)

    print("Logged in as " + str(gis.properties.user.username))

    query_dict = { 'f': 'json', 'username': args.user, 'password': args.password, 'referer': args.portal }
    url = args.portal+"/sharing/rest/generateToken"
    r = requests.post(url + "?f=json", params=query_dict)
    t = json.loads(r.text)
    token = t['token']
    print ('token:  '+token)

    if "token" not in r.text:
        print('cound not get token, error')
        sys.exit(1)


    fn = args.fcs
    with open(fn, 'r') as f:
        for line in f:
           print('')
           print('***********************************************')
           x = line.split(";")
           cron=x[0]
           print ('cron expression - '+cron)
           stalemin=int(x[1])
           print ('Stale Minutes - '+str(stalemin))
           title=x[2]
           print ('Title - '+title)
           metadataurl=x[3]
           print ('Metadata Url - '+metadataurl)
           agourl=x[4]
           print ('AGO Item URL - '+agourl)
           #find GUID of ITEM
           guid=agourl.split('id=')[1]


           #check to see the modified date of the AGO item
           #agoitem = gis.content.get(guid)
           print ("search for "+title+' owner - '+args.user)
           #agoitemlist = gis.content.search(query="title:"+ title +" AND owner:" + args.user, item_type='Feature Layer')
           agoitemlist = gis.content.search(query="id:"+ guid +" AND owner:" + args.user, item_type='Feature Layer')

           if agoitemlist:
               agoitem = agoitemlist[0]
               print('found '+agoitem.url)
           else:
               print('not found '+title)

           if agoitem:
               #print (agoitem)
               #print (agoitem.modified)
               #print (agoitem.url)
               # 2: request the json data for the feature

               query_dict = { "f": "json", "token": token }

               jsonResponse = requests.get(agoitem.url+"/0", params=query_dict)
               # lastEditDate is in the editingInfo section of the json response
               # to access other sections, change "editingInfo" to the section name ("types" for example)
               # using OrderedDict keeps the file ordered as sent by server, but is not necessary
               #print(jsonResponse.text)
               resptxt = jsonResponse.text

               if resptxt.find("editingInfo")>0:
                   t = json.loads(jsonResponse.text)
                   lastEditDate = t['editingInfo']['lastEditDate']
               else:
                   jsonResponse = requests.get(agoitem.url+"/1", params=query_dict)
                   #print(jsonResponse.text)
                   resptxt = jsonResponse.text
                   if resptxt.find("editingInfo")>0:
                       t = json.loads(jsonResponse.text)
                       lastEditDate = t['editingInfo']['lastEditDate']
                   else:
                       jsonResponse = requests.get(agoitem.url+"/2", params=query_dict)
                       resptxt = jsonResponse.text
                       if resptxt.find("editingInfo")>0:
                         t = json.loads(jsonResponse.text)
                         lastEditDate = t['editingInfo']['lastEditDate']
                       else:
                         jsonResponse = requests.get(agoitem.url+"/3", params=query_dict)
                         resptxt = jsonResponse.text
                         if resptxt.find("editingInfo")>0:
                           t = json.loads(jsonResponse.text)
                           lastEditDate = t['editingInfo']['lastEditDate']



               print (lastEditDate)
               if not lastEditDate:
                   lastEditDate=agoitem.modified
                   print('using AGO ITEM modified date as feature service edit date is null')

               editTime = lastEditDate/1000
               print ("Last Edited: " + time.strftime('%c', time.localtime(editTime)))

               converted_d1 = datetime.datetime.fromtimestamp(round(lastEditDate / 1000))
               current_time = datetime.datetime.now()

               #print (current_time)
               #print (converted_d1)
               dateage = current_time - converted_d1
               print (dateage)
               age = int(dateage.total_seconds() / 60)
               print(age)
               diff = stalemin-age
               if diff<0:
                   print ("Older than stale minutes so running update  "+str(diff))
                   # run PRO->SD->feature layer steps
                   publish2ago(DEFAULT_AGO_FOLDER,agoitem, gis, metadataurl,prjPath,prj,args.user,guid)

               else:
                   print ("Younger than stale minutes so skipping update  "+str(diff))
           else:
                print (guid+" Not found in AGO - "+title)


def publish2ago(folder,agoitem, gis, metadataurl,prjPath,prj,user,guid):

   # Set sharing options
    shrOrg = False
    shrEveryone = False
    shrGroups = ''
    tags ="BC; British Columbia; Canada; "
    credits="DataBC, GeoBC"
    use_limits = r'<p>This web service is <a href="http://www2.gov.bc.ca/gov/content/home/copyright">Copyright Province of British Columbia</a>.  All rights reserved.</p>  <p>The B.C. Map Hub and associated materials, including map applications (&quot;Maps&quot;), trade-marks and official marks (collectively, &quot;Materials&quot;), are owned or used under license by the Province of British Columbia (&quot;Province&quot;) and are protected by copyright and trade-mark laws.  Please see the <a href="https://www2.gov.bc.ca/gov/content?id=14CE6DD7756F402287618963D936BE44">Disclaimer</a> for further details.</p>  <p>The Province does not collect, use or disclose personal information through the ArcGIS Online website.  Please be aware, however, that IP addresses are collected by Esri and are stored on Esris servers located outside of Canada.  For further information, including the purposes for which your IP address is collected,  please see Esris Privacy Policy at:  <a>http://www.esri.com/legal/privacy</a>.   By accessing or using the B.C. Map Hub, you consent, effective as of the date of such access or use, to Esri storing and accessing your IP address outside of Canada for the purposes described in Esris Privacy Policy.  Should you have any questions about the collection of your IP address, please contact BCGov AGOL CONTACT at Data@gov.bc.ca, PO BOX 9864 STN PROV GOVT, Victoria BC  V8W 9T5</p>'

    # Local paths to create temporary content
    relPath=os.path.dirname(prjPath)
    print("Path to store temporary service definitions: "+relPath)
    #print('Creating SD file')
    arcpy.env.overwriteOutput = True
    prj = arcpy.mp.ArcGISProject(prjPath)

    arcpy.env.workspace = relPath
    print (prj.filePath)



    try:
        for m in prj.listMaps():
            #print("Map: " + m.name)

            lyrs = m.listLayers()
            start_time = time.time()
            for lyr in lyrs:
                cnt = 0
                if lyr.name.strip() == agoitem.title.strip():
                    cnt = 1
                    print('APRX Layer name: '+lyr.name)
                    print('AGO item title: '+agoitem.title)

                    print('Search for original SD on portal')
                    sdItem = gis.content.search(query="title:"+ agoitem.title +" AND owner:" + user, item_type='Service Definition')[0]

                    if sdItem:
                        print ("found existing AGO service definiton for:  "+sdItem.title)

                        cnt=cnt+1
                    else:
                        print('did not find service definition for: '+ lyr.name)


                    sddraft = os.path.join(relPath,"temp.sddraft").replace("/","\\")
                    #sddraft="temp.sddraft"
                    sd = os.path.join(relPath, "temp.sd").replace("/","\\")
                    sd="temp.sd"
                    print("sddraft: "+sddraft)
                    if os.path.exists(sddraft):
                        os.remove(sddraft)
                        print("removing "+sddraft)
                    if os.path.exists(sd):
                        os.remove(sd)
                        print("removing "+sd)
                    now = time.ctime(int(time.time()))
                    #bcdc_package = bcdc.find_package_for_feature_class(feat_class)

                    summary = "Summary from BCDC Last Updated - "+now
                    print (summary)
                    tags = tags +lyr.name
                    description ="Description from BCDC"

                    #print(sddraft, lyr.name, Folder,summary,tags,description,credits,use_limits)

                    print('Create SDDRAFT')
                    #CreateWebLayerSDDraft (map_or_layers, out_sddraft, service_name, {server_type}, {service_type}, {folder_name}, {overwrite_existing_service}, {copy_data_to_server}, {enable_editing}, {allow_exporting}, {enable_sync}, {summary}, {tags}, {description}, {credits}, {use_limitations})
                    print(arcpy.mp.CreateWebLayerSDDraft(lyr, sddraft, lyr.name, 'MY_HOSTED_SERVICES','FEATURE_ACCESS',  folder_name=folder, overwrite_existing_service=True,copy_data_to_server=True, enable_editing=False,allow_exporting=False,enable_sync=False, summary=summary,tags=tags, description=description,credits=credits,use_limitations=use_limits))
                    print('Stage SDDRAFT')
                    print(sddraft, sd)
                    print(arcpy.StageService_server(sddraft, sd))



                    if not sdItem:
                        sdItem = arcpy.UploadServiceDefinition_server (sd, in_server='My Hosted Services' , in_folder_type='FROM_SERVICE_DEFINITION', in_startupType='STARTED', in_override='USE_DEFINITION')
                        #print("Uploading SD: {}, ID: {} ....".format(sdItem.title, sdItem.id))
                        print(sdItem.update(data=sd))
                        fs = sdItem.publish(overwrite=True)
                        print('Found Feature Class: {}, ID: {} Uploading and overwriting'.format(lyr.name, user))
                    else:
                        #print("Found SD: {}, ID: {} n Uploading and overwriting..".format(sdItem.title, sdItem.id))
                        print(sdItem.update(data=sd))
                        print("Overwriting existing feature service..")
                        fs = sdItem.publish(overwrite=True)

                    if shrOrg or shrEveryone or shrGroups:
                        print("Setting sharing options")
                        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)


                    print("Finished updating: {}  ID: {}".format(fs.title, fs.id))
                    elapsed_time = start_time - time.time()
                    print('Elapsed Time: '+str(elapsed_time))
                    now = time.ctime(int(time.time()))
                    print('Time: '+now)
                    print('')



    except RuntimeError as ex:
        if len(ex.args) > 0:
            AddError("Error creating %s. %s" % (relPath, ex.args))
        else:
            AddError(
                "Error creating %s. No further info provided." % relPath)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
  main()
