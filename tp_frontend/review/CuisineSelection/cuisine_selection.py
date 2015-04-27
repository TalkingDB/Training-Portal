import os
import ast
import subprocess
import csv
import config as c

def select_cuisine(cuisine):
    """
    get all the restraunt id of specific cuisine.
    """
    if not cuisine:
	return False
    with open(c.output+"/cuisines.csv", "rb") as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
	    if row[0] == cuisine:
		if process_restaurants(row[1]):
		    return True
    return False



def process_restaurants(res_list):
    """
    copy all the selected restaurants fram all menu folder to UIP
    """
    try:
    	subprocess.call('sudo find /home/anil.gautam/Smarter.Codes/customer_files/foodweasel.com/UIP -name "*.json" -print0 | xargs -0 rm', shell=True, executable='/bin/bash')
    except Exception as e:
	print e
	return False
    data = ast.literal_eval(res_list)
    res_list= [n.strip() for n in data]
    for res in res_list:
	print res
	try:
	    subprocess.call('sudo cp ' + c.all_menu_path + '/'+str(res)+".json " + c.UIP_path, shell=True, executable='/bin/bash')
    	except Exception as e:
            print e
    return True
    

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

def set_current_cuisine(cuisine):
    """
    """
    f = open(c.output+"/current.txt", "wb")
    f.write(cuisine)
    f.close()

def get_current_cuisine():
    """
    """
    f = open(c.output+"/current.txt", "rb").read()
    return f.replace("\n", "").strip()
