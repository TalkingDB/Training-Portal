import glob
import json
import csv
import config

def extract_cuisines():
    """
    Make a csv file for all cuisines with restaurant ids.
    """
    restaurants = glob.glob(config.all_menu_path+"/*")
    all_cuisines = {}
    i = 0
    for res in restaurants:
        f = open(res,'r')
        try:
            data = json.loads(f.read())
            cuisines =  data["data"][0]["properties"]["cuisines"]
            res_id =  data["unique_value"]
            if cuisines:
                if "," in cuisines:
                    for c in cuisines.split(","):
                        if c in all_cuisines:
                            all_cuisines[c].append(res_id)
                        else:
                            all_cuisines[c] = [res_id]
                else:
                    all_cuisines = all_cuisines+[cuisines]
    #           subprocess.call('sudo cp ' + res + ' newyork/', shell=True, executable='/bin/bash')
        except:
            print res
        f.close()
    with open(config.output+'/cuisines.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for key, value in all_cuisines.iteritems():
            spamwriter.writerow([key,value, len(value)])