import os
import ast
import subprocess
import csv
import config as c

def select_cuisine(cuisines):
    """
    get all the restraunt id of specific cuisine.
    """
    print "list of cuisines"
    print len(cuisines)
    print "length of cuinishes"
    if len(cuisines) > 0:
        clear_cuisine()
        print len(cuisines)
    rest = []
    
    for cuisine in cuisines:
        with open(c.output+"/cuisines.csv", "rb") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            print cuisine
            if not cuisine:
                return False
            for row in reader:
                if row[0] == cuisine:
                    print "called for "+cuisine
                    process_restaurants(row[1])
                    csvfile.closed
    return False

def process_restaurants(res_list):
    """
    copy all the selected restaurants fram all menu folder to UIP
    """
    data = ast.literal_eval(res_list)
    res_list= [n.strip() for n in data]
    for res in res_list:
	print res
	try:
	    subprocess.call('sudo cp ' + c.all_menu_path + '/'+str(res)+".json " + c.UIP_path, shell=True, executable='/bin/bash')
    	except Exception as e:
            print e
    #return True
    
def clear_cuisine():
    try:
    	subprocess.call('sudo find /home/anil.gautam/Smarter.Codes/customer_files/foodweasel.com/UIP -name "*.json" -print0 | xargs -0 rm', shell=True, executable='/bin/bash')
    except Exception as e:
	print e
	return False

def get_all_cuisines():
    """
     Get all cuisines from csv.
    """
    cuisines = []
    with open(c.output+"/cuisines.csv", "rb") as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
	    cuisines.append(str(row[0]))
    return sorted(cuisines)

def set_current_cuisine(cuisines):
    """
    """
    f = open(c.output+"/current.txt", "wb")
    for cuisine in cuisines:
        f.write(cuisine+" ")
    f.close()
       
def get_current_cuisine():
    """
    """
    f = open(c.output+"/current.txt", "rb").read()
    return f.replace("\n", "").strip()

