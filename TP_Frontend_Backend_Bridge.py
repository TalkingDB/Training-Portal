import glob #helpful to enumerate files inside a folder

def getSeedCategories():
    return '["color",4,0,0]'

def getCatalogFiles():
    catalogs = glob.glob('../../customer_files/foodweasel.com/*') #returns list of all the files in this folder. a ".." has been prefixed because it is often called from the child folder, the ".." takes the path cursor to current file
    return catalogs

projectName = "Foodweasel" #this constant needs to be retrieved from UI of TP Frontend 
