import glob #helpful to enumerate files inside a folder
import os

root_dir_path = os.path.expanduser("~/Smarter.Codes")

def getSeedCategories():
    return '["color",4,0,0]'

def getCatalogFiles():
    catalogs = glob.glob(root_dir_path+'/customer_files/foodweasel.com/Training_Portal/*') #returns list of all the files in this folder. a ".." has been prefixed because it is often called from the child folder, the ".." takes the path cursor to current file
    return catalogs

projectName = "Target" #this constant needs to be retrieved from UI of TP Frontend 
