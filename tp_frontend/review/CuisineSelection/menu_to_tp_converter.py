'''
Created on 27-Jan-2015
Takes input of delivery.com restaurant menus in JSON format
Spits out a plain text file with restaurant items, and options separated by newline
This plain text file is useful for giving input to Smarter.Codes Training Portal
@author: tushar@solutionbeyond.net
'''
import glob #helpful to enumerate files inside a folder
import json
import config as c

#TODO: Presently it outputs a plain text file with text with unstructured text separated by newline.
#in coming version this program must create a JSON file (than plain text file) which Smarter.Codes can take as input


def menu_converter():
    """
    Convert json menu to text file output for Training Portal
    """
    restaurants = glob.glob(c.UIP_path+'/*.json') #returns LIST of JSON files in given folder
    output = open(c.TP_output + '/1','wb')
    for restaurant in restaurants:
        print 'processing restaurant file = ' + restaurant
        delivery_com_JSON_file = open(restaurant,'r')

        data = json.loads(delivery_com_JSON_file.read())

        uid = data['unique_value']
        for jsonElement in data['data']:

            #Variable declaration
            nodeType = jsonElement['type']

            if nodeType in ['item','option']:

                # String to manipulate (Restraunt menu item)
                manipulated_string = str((jsonElement['name']).encode('utf8'))

                name = manipulated_string

                # Condition : If we encounter "." in name of dish like "B1. Chicken Chilly"
                # split by "." and check if previous text is alpha numeric or less than 4 chars
                # if yes pick valuie after "." that is " Chicken Chilly" strip white spaces "Chicken Chilly"
                if "." in manipulated_string:
                    sub_string = manipulated_string.split('.')
                    if any(char.isdigit() for char in sub_string[0]) or len(sub_string[0]) < 4:
                        name = sub_string[1].strip()

                # Change value in json data from "B1. Chicken Chilly" to "Chicken Chilly"
                jsonElement['name'] = name

                # Write in output.txt like "Chicken Chilly" to "chicken chilly"
                output.write( name.lower() + '\n')

        delivery_com_JSON_file.close()
    output.close()
