#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import os,sys
import os
import optparse
from xml.dom import minidom
import time

###########################################################################
class OptionParser (optparse.OptionParser):
 
    def check_required (self, opt):
      option = self.get_option(opt)
 
      # Assumes the option's 'default' is set to None!
      if getattr(self.values, option.dest) is None:
          self.error("%s option not supplied" % option)
 
###########################################################################

#get DateTime for XML naming (SvB)

timestamp = time.strftime("%Y%m%d_%H%M%S")

#get URL, name and type within xml file from Scihub
def get_elements(xml_file):
    urls=[]
    contentType=[]
    name=[]
    with open(xml_file) as fic:
        line=fic.readlines()[0].split('<entry>')
        for fragment in line[1:]:
            urls.append(fragment.split('<id>')[1].split('</id>')[0])
            contentType.append(fragment.split('<d:ContentType>')[1].split('</d:ContentType>')[0])
            name.append(fragment.split('<title type="text">')[1].split('</title>')[0])
    os.remove(xml_file)
    return urls,contentType,name

# recursively download file tree of a Granule
def download_tree(rep,xml_file,wg,auth,wg_opt,value):
    urls,types,names=get_elements(xml_file)
    for i in range(len(urls)):
        if types[i]=='Item':
            nom_rep="%s/%s"%(rep,names[i])
            if not(os.path.exists(nom_rep)):
                os.mkdir(nom_rep)
            commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,'files.xml',urls[i]+"/Nodes")
            print commande_wget
            os.system(commande_wget)
            download_tree(nom_rep,'files.xml',wg,auth,wg_opt,value)
        else:
            commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,rep+'/'+names[i],urls[i]+'/'+value)

            os.system(commande_wget)
	    #retry download in case of a Bad Gateway error"
	    while os.path.getsize(rep+'/'+names[i])==0 :
		   os.system(commande_wget)

def get_dir(dir_name,dir_url,product_dir_name,wg,auth,wg_opt,value):
    dir=("%s/%s"%(product_dir_name,dir_name))
    if not(os.path.exists(dir)) :
	os.mkdir(dir)
    commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,'temp.xml',dir_url)
    print commande_wget
    os.system(commande_wget)
    download_tree(product_dir_name+'/'+dir_name,"temp.xml",wg,auth,wg_opt,value)
   
    

##########################################################################




url_search="https://scihub.copernicus.eu/apihub/search?q="

#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example python  %s --lat 43.6 --lon 1.44 -a apihub.txt "%sys.argv[0]
    print "example python  %s --lat 43.6 --lon 1.44 -a apihub.txt -t 31TCJ "%sys.argv[0]
    sys.exit(-1)
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)

    parser.add_option("--lat", dest="lat", action="store", type="float",
                      help="latitude in decimal degrees",default=None)
    parser.add_option("--lon", dest="lon", action="store", type="float",
                      help="longitude in decimal degrees",default=None)
    parser.add_option("--latmin", dest="latmin", action="store", type="float",
                      help="min latitude in decimal degrees",default=None)
    parser.add_option("--latmax", dest="latmax", action="store", type="float",
                      help="max latitude in decimal degrees",default=None)
    parser.add_option("--lonmin", dest="lonmin", action="store", type="float",
                      help="min longitude in decimal degrees",default=None)
    parser.add_option("--lonmax", dest="lonmax", action="store", type="float",
                      help="max longitude in decimal degrees",default=None)
    parser.add_option("-b", "--begin_ingest_date", dest="begin_ingest_date", action="store", type="string",
                      help="begin ingestion date, fmt('2015-12-22')", default=None)
    parser.add_option("-e", "--end_ingest_date", dest="end_ingest_date", action="store", type="string",
                      help="end ingestion date, fmt('2015-12-23')", default=None)
    parser.add_option("-B", "--begin_sense_date", dest="begin_sense_date", action="store", type="string",
                      help="begin sensing date, fmt('2015-12-22')", default=None)
    parser.add_option("-E", "--end_sense_date", dest="end_sense_date", action="store", type="string",
                      help="end sensing date, fmt('2015-12-23')", default=None)
    parser.add_option("-o","--orbit", dest="orbit", action="store", type="int",
                      help="Relative Orbit Number", default=None)
    parser.add_option("-c","--cloud", dest="cloud", action="store",type="float",
                      help="Do not download products with more cloud percentage. "
                           "When tile option selected cloud cover of tile will be searched ",default=110)
    parser.add_option("-s","--sentinel", dest="sentinel", action="store",type="string",
                      help="Sentinel mission considered (S1 or S2)",default=None)
    parser.add_option("-d", "--datatype", dest="datatype", action="store", type="string",
                      help="Sentinel-1 data type fmt('SLC' or 'GRD')", default=None)
    parser.add_option("-t","--tile", dest="tile", action="store",type="string",
                      help="Sentinel-2 Tile number",default=None)
    parser.add_option("-l", "--login", dest="login", action="store", type="string", \
                      help="ESA account and password file (make sure to set for right Hub)")
    parser.add_option("-p", "--proxy_passwd", dest="proxy", action="store", type="string",
                      help="Proxy account and password file", default=None)
    parser.add_option("--colhub", dest="colhub",action="store_true",
                      help="Alternative ColHub interface when SciHub is not working. "
                           "Change login details accordingly", default=False)
    parser.add_option("--cophub", dest="cophub", action="store_true",
                      help="Alternative CopHub interface when SciHub is not working. "
                           "Change login details accordingly", default=False)
    parser.add_option("--dhus", dest="dhus", action="store_true", \
                      help="Try dhus interface when apihub is not working", default=False)
    parser.add_option("-n", "--no_download", dest="no_download", action="store_true", \
                      help="Do not download products, just print wget command", default=False)
    parser.add_option("--downloader", dest="downloader", action="store", type="string", \
                      help="downloader options are aria2 or wget (default is wget)", default=None)
    parser.add_option("-w", "--write_dir", dest="write_dir", action="store", type="string", \
                      help="Path where the products should be downloaded", default='.')
    parser.add_option("-r",dest="MaxRecords",action="store",type="int",
                      help="maximum number of records to download (default=100)",default=100)



    (options, args) = parser.parse_args()
    if options.lat==None or options.lon==None:
        if options.latmin==None or options.lonmin==None or options.latmax==None or options.lonmax==None:
            print "provide at least a point or  rectangle"
            sys.exit(-1)
        else:
            geom='rectangle'
    else:
        if options.latmin==None and options.lonmin==None and options.latmax==None and options.lonmax==None:
            geom='point'
        else:
            print "please choose between point and rectangle, but not both"
            sys.exit(-1)

    if options.tile != None and options.sentinel == 'S1':
        print "The tile option (-t) can only be used for Sentinel-2"
        sys.exit(-1)

    if options.datatype != None and options.sentinel == 'S2':
        print "The datatype option (-d) can only be used for Sentinel-1"
        sys.exit(-1)
        
    parser.check_required("-l")
    
#====================
# read password file
#====================
try:
    f=file(options.login)
    (account,passwd)=f.readline().split(' ')
    if passwd.endswith('\n'):
        passwd=passwd[:-1]
    f.close()
except :
    print "error with password file"
    sys.exit(-2)

#set alternative Hub or dhus option (SvB)

if options.colhub == True:
    url_search = url_search.replace("scihub", "colhub")

if options.cophub == True:
    url_search = url_search.replace("scihub", "cophub")

if options.dhus == True:
    url_search = url_search.replace("apihub", "dhus")

#==================================================
#      prepare wget command line to search catalog
#==================================================
if os.path.exists('query_results_%s.xml' % timestamp):
    os.remove('query_results_%s.xml' % timestamp)

#remove temporary header files, if still exist (SvB)

if  os.path.exists('tile_folder.xml'):
    os.remove('tile_folder.xml')

if os.path.exists('tile_info.xml'):
    os.remove('tile_info.xml')

if options.downloader=="aria2":
    wg='aria2c --check-certificate=false'
    auth='--http-user="%s" --http-passwd="%s"'%(account,passwd)
    search_output=" --continue -o query_results_%s.xml" % timestamp
    wg_opt=" -o "
    if sys.platform.startswith('linux'):
        value="\$value"
    else:
        value="$value"
else :
    wg="wget --no-check-certificate"
    auth='--user="%s" --password="%s"'%(account,passwd)
    search_output="--output-document=query_results_%s.xml" % timestamp
    wg_opt=" --continue --output-document="
    if sys.platform.startswith('linux'):
        value="\\$value"
    else:
        value="$value"

if geom=='point':
    if sys.platform.startswith('linux'):
	query_geom='footprint:\\"Intersects(%f,%f)\\"'%(options.lat,options.lon)
    else :
	query_geom='footprint:"Intersects(%f,%f)"'%(options.lat,options.lon)
	
elif geom=='rectangle':
    if sys.platform.startswith('linux'):
	query_geom='footprint:\\"Intersects(POLYGON(({lonmin} {latmin}, {lonmax} {latmin}, {lonmax} {latmax}, {lonmin} {latmax},{lonmin} {latmin})))\\"'.format(latmin=options.latmin,latmax=options.latmax,lonmin=options.lonmin,lonmax=options.lonmax)
    else :
	query_geom='footprint:"Intersects(POLYGON(({lonmin} {latmin}, {lonmax} {latmin}, {lonmax} {latmax}, {lonmin} {latmax},{lonmin} {latmin})))"'.format(latmin=options.latmin,latmax=options.latmax,lonmin=options.lonmin,lonmax=options.lonmax)

query = '%s filename:%s*' % (query_geom, options.sentinel)

if options.datatype==None:
    query=query
else:
    query=query + ' AND producttype:%s'% options.datatype

if options.orbit==None:
    query=query
else:
    query=query + ' AND relativeorbitnumber:%03d'% options.orbit

if options.begin_ingest_date!=None:
    begin_ingest_date = options.begin_ingest_date+"T00:00:00.000Z"
    if options.end_ingest_date!=None:
        begin_ingest_date=options.end_ingest_date+"T23:59:50.000Z"
    else:
        end_ingest_date="NOW"
    query_ingest_date = " AND ingestionDate:[%s TO %s]" % (begin_ingest_date, end_ingest_date)
    query = query + query_ingest_date

if options.begin_sense_date != None:
    begin_sense_date = options.begin_sense_date + "T00:00:00.000Z"
    if options.end_sense_date != None:
        end_sense_date = options.end_sense_date + "T23:59:50.000Z"
    else:
        end_sense_date = "NOW"
    query_sense_date = " AND beginPosition:[%s TO %s]" % (begin_sense_date, end_sense_date)
    query = query + query_sense_date

print query
commande_wget='%s %s %s "%s%s&rows=%d"'%(wg,auth,search_output,url_search,query,options.MaxRecords)
print commande_wget
os.system(commande_wget)

#=======================
# parse catalog output
#=======================

#query_result.xml with timestamp (SvB)
xml=minidom.parse("query_results_%s.xml" % timestamp)
products=xml.getElementsByTagName("entry")
for prod in products:
    ident=prod.getElementsByTagName("id")[0].firstChild.data
    #print 'Image ID: %s' % ident
    link=prod.getElementsByTagName("link")[0].attributes.items()[0][1] 
    #to avoid wget to remove $ special character
    link=link.replace('$value',value)


    for node in prod.getElementsByTagName("str"):
        (name,field)=node.attributes.items()[0]
        if field=="filename":
            filename= str(node.toxml()).split('>')[1].split('<')[0]   #ugly, but minidom is not straightforward

            if filename[0:2] == 'S2':
                filename_short = filename[0:25] + filename[41:62] + filename[78:]
            else:
                filename_short = filename

    url_granule_dir = link.replace(value, "Nodes('%s')/Nodes('GRANULE')/Nodes" % (filename))

    # extract information from metadata of each image for further information

    for node in prod.getElementsByTagName("summary"):
        summary = str((node.toxml()).split('>')[1].split('<')[0])

    for node in prod.getElementsByTagName("id"):
        uuid = str((node.toxml()).split('>')[1].split('<')[0])

    if options.sentinel == 'S2':
        for node in prod.getElementsByTagName("double"):
            (name,field)=node.attributes.items()[0]
            if field=="cloudcoverpercentage":
                cloud=float((node.toxml()).split('>')[1].split('<')[0])
    else:
        cloud = 0

    for node in prod.getElementsByTagName("int"):
        (name, field) = node.attributes.items()[0]
        if field == "relativeorbitnumber":
            relorb = int((node.toxml()).split('>')[1].split('<')[0])


    # print what has been found to screen, no download

    if options.no_download == True:
        print "\n==============================================="
        print 'Filename: %s' % filename
        print "Summary: %s" % summary
        print "UUID: %s" % uuid
        print "Relative Orbit Number: %s" % relorb

        if options.sentinel == 'S2':
            print "Cloud percentage = %5.2f %%" % cloud
        print "===============================================\n"

    #==================================DOWNLOAD WHOLE PRODUCT
    else:
        if(cloud < options.cloud or options.sentinel == "S1") and options.tile == None:
            commande_wget='%s %s %s%s/%s "%s"'%(wg,auth,wg_opt,options.write_dir,filename+".zip",link)
            #print commande_wget

            #do not download the product if it was already downloaded and unzipped.
            unzipped_file_exists = os.path.exists(("%s/%s")%(options.write_dir,filename))
            unzipped_file_short_exists = os.path.exists(("%s/%s") % (options.write_dir, filename_short))

            if (unzipped_file_exists == True or unzipped_file_short_exists == True):
                print "========================================================================"
                print "File already exists: %s, or short filename already exists: %s" % \
                      (unzipped_file_exists, unzipped_file_short_exists)
                print "=======================================================================\n"
                print commande_wget
            else:
                os.system(commande_wget)

            # rename long S2 folder names (SvB)
            if options.sentinel == 'S2':
                rename_folder = 'mv %s %s' % (filename, filename_short)
                os.system(rename_folder)

        #===============================DOWNLOAD ONLY ONE TILE, FILE PER FILE

        elif options.tile != None and options.sentinel == "S2":
            unzipped_file_exists = os.path.exists(("%s/%s") % (options.write_dir, filename))
            unzipped_file_short_exists = os.path.exists(("%s/%s") % (options.write_dir, filename_short))
            #print commande_wget

            #check whether tiles are already downloaded
            if (unzipped_file_exists == True or unzipped_file_short_exists == True):
                print "========================================================================"
                print "File already exists: %s, or short filename already exists: %s" % \
                      (unzipped_file_exists, unzipped_file_short_exists)
                print "========================================================================\n"
                print commande_wget
            else:
                # find URL of header file
                url_file_dir=link.replace(value,"Nodes('%s')/Nodes"%(filename))
                commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,'file_dir.xml',url_file_dir)
                os.system(commande_wget)
                print commande_wget
                urls,types,names=get_elements('file_dir.xml')
                #search for the xml file
                for i in range(len(urls)):
                    if names[i].find('SAFL1C')>0:
                        xml=names[i]
                        url_header=urls[i]

                #retrieve list of granules
                url_granule_dir=link.replace(value,"Nodes('%s')/Nodes('GRANULE')/Nodes"%(filename))

                commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,'granule_dir.xml',url_granule_dir)
                os.system(commande_wget)
                urls,types,names=get_elements('granule_dir.xml')
                granule=None

                #search for the tile
                for i in range(len(urls)):
                    if names[i].find(options.tile) > 0:
                        granule=names[i]

                #notify if tile is not found in S-2 file

                if granule == None:
                    print "========================================================================"
                    print "Tile %s is not available within product %s" % \
                          (options.tile, filename_short)
                    print "Download will not commence!"
                    print "========================================================================\n"

                #go forth with investigation of the tile, check the cloud cover in the individual tile
                else:
                    url_granule_xml = "%s('%s')/Nodes" % (url_granule_dir, granule)

                    #download the XML metadata file associated with the tile folder to get the exact name of the tile
                    #metadata XML file. Bit of a long route, but no quicker solution found

                    commande_wget = '%s %s %s%s "%s"' % (wg, auth, wg_opt, 'tile_folder.xml', url_granule_xml)
                    print commande_wget
                    os.system(commande_wget)

                    xml_tile = minidom.parse("tile_folder.xml")

                    for node in xml_tile.getElementsByTagName("d:Id"):
                        if 'xml' in str((node.toxml()).split('>')[1].split('<')[0]):
                            tile_xml_id = str((node.toxml()).split('>')[1].split('<')[0])
                            print tile_xml_id

                            # download the XML file of the tile, which is relatively slow as they are 500 Kb each

                            url_granule_xml_info = "%s('%s')/Nodes('%s')/%s" % (url_granule_dir, granule,tile_xml_id, value)

                            commande_wget = '%s %s %s%s "%s"' % (wg, auth, wg_opt, 'tile_info.xml', url_granule_xml_info)

                            os.system(commande_wget)

                            xml_info = minidom.parse("tile_info.xml")

                            #extract cloud cover information from the tile metadata file

                            for node in xml_info.getElementsByTagName("CLOUDY_PIXEL_PERCENTAGE"):
                                tile_cloud = float((node.toxml()).split('>')[1].split('<')[0])
                                print "cloud percentage in tile %s = %5.2f %%"% (options.tile, tile_cloud)
                                os.remove('tile_folder.xml')
                                os.remove('tile_info.xml')

                    if tile_cloud > options.cloud:
                        print "========================================================================"
                        print "Cloud cover in tile %s is %5.2f percent, higher than threshold of %5.2f" % \
                              (options.tile, tile_cloud, options.cloud)
                        print "Download will not commence!"
                        print "========================================================================\n"

                    else:
                        # announce impending download of tile
                        print "========================================================================"
                        print "Cloud cover in tile %s is %5.2f percent, lower than threshold of %5.2f" % \
                              (options.tile, tile_cloud, options.cloud)
                        print "Download of tile %s in image %s will COMMENCE!" % (options.tile, filename_short)
                        print "========================================================================"

                        #create product directory
                        product_dir_name=("%s/%s"%(options.write_dir,filename))
                        if not(os.path.exists(product_dir_name)) :
                            os.mkdir(product_dir_name)
                        #create tile directory
                        granule_dir_name=("%s/%s"%(product_dir_name,'GRANULE'))
                        if not(os.path.exists(granule_dir_name)) :
                            os.mkdir(granule_dir_name)
                        #create tile directory
                        nom_rep_tuile=("%s/%s"%(granule_dir_name,granule))
                        if not(os.path.exists(nom_rep_tuile)) :
                            os.mkdir(nom_rep_tuile)
                        # download product header file
                        commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,product_dir_name+'/'+xml,url_header+"/"+value)
                        print commande_wget
                        os.system(commande_wget)

                        #download INSPIRE.xml
                        url_inspire=link.replace(value,"Nodes('%s')/Nodes('INSPIRE.xml')/"%(filename))
                        commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,product_dir_name+'/'+"INSPIRE.xml",url_inspire+"/"+value)
                        print commande_wget
                        os.system(commande_wget)

                        url_manifest=link.replace(value,"Nodes('%s')/Nodes('manifest.safe')/"%(filename))
                        commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,product_dir_name+'/'+"manifest.safe",url_manifest+"/"+value)
                        print commande_wget
                        os.system(commande_wget)

                        # rep_info
                        url_rep_info_dir=link.replace(value,"Nodes('%s')/Nodes('rep_info')/Nodes"%(filename))
                        get_dir('rep_info',url_rep_info_dir,product_dir_name,wg,auth,wg_opt,value)

                        # HTML
                        url_html_dir=link.replace(value,"Nodes('%s')/Nodes('HTML')/Nodes"%(filename))
                        get_dir('HTML',url_html_dir,product_dir_name,wg,auth,wg_opt,value)

                        # AUX_DATA
                        url_auxdata_dir=link.replace(value,"Nodes('%s')/Nodes('AUX_DATA')/Nodes"%(filename))
                        get_dir('AUX_DATA',url_auxdata_dir,product_dir_name,wg,auth,wg_opt,value)

                        # DATASTRIP
                        url_datastrip_dir=link.replace(value,"Nodes('%s')/Nodes('DATASTRIP')/Nodes"%(filename))
                        get_dir('DATASTRIP',url_datastrip_dir,product_dir_name,wg,auth,wg_opt,value)

                        #granule files
                        url_granule="%s('%s')/Nodes"%(url_granule_dir,granule)
                        commande_wget='%s %s %s%s "%s"'%(wg,auth,wg_opt,'granule.xml',url_granule)
                        print commande_wget
                        os.system(commande_wget)
                        download_tree(nom_rep_tuile,"granule.xml",wg,auth,wg_opt,value)

                        # rename long S2 folder names (SvB)
                        rename_folder = 'mv %s %s' % (filename, filename_short)
                        os.system(rename_folder)

        #=============================NO DOWNLOAD DUE TO TOO MANY CLOUDS
        else:
            print "========================================================================"
            print "Cloud cover in product %s is %5.2f, higher than threshold of %5.2f" % \
                  (filename_short, tile_cloud, options.cloud)
            print "Download will not commence!"
            print "========================================================================\n"



