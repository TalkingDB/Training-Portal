import os

import json
import requests
import csv
import socket
import re
import time

output_dir_path = os.path.expanduser("~/Smarter.Codes/src/TrainingPortal/tp_frontend/review/media/output/")
url="http://training.smarter.codes:8001/recommendation/generate/"
parent = '{"key": "uid","value":["72894", "81443", "70681", "30857", "52951", "73498", "70263", "68964", "29602", "79779", "65010", "68924", "46911", "75328", "79960", "38911", "74661", "71519", "70131", "69384"]}'
headers = {'Content-type': 'application/json', 'Accept': '*/*', "Authorization": "Basic Zm9vZHdlYXNlbC5jb206Q2hhbmdlTWU="}
client = requests.session()
item_dict = {}
option_dict = {}
i = 0
instruct = ""
result = []

def commandProcessorHit(arg):
    """
    Function to hit command processor socket
    to fetch NER response as JSON

    Input : string name
    Output: dict buf of type
        {
            'links':{},
            'nodes':{}
        }
    """
    try:
        s = socket.socket()
        s.connect(("training.smarter.codes", 5012))
        s.send(arg)
        buf = ''
        #Iterator applied to receive chunks of data over socket
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            else:
                buf += chunk

        return buf
    except UnicodeDecodeError:
        print arg + ' is a unicode string'
    except Exception as e:
        print e
def get_child_data(data):
    """
    """
    global instruct
    global i
    if data["type"] == "group" and "children" in data:
        for child in data["children"]:
            get_child_data(child)
    elif data["type"] == "item" and "children" in data:
        #result[-1] = result[-1] + "Item = "+data["name"]+"\n"
        if data["instruction"] in item_dict:
            if [item for item in item_dict[data["instruction"]] if "\t"+"Item = " +data["name"] in item]:
                i = i+1
                print data["name"]+"-"+str(i)
                instruct = data["name"]+"-"+str(i)
            else:
                instruct = data["name"]
            if len(data['warning']) > 0:
                for key, val in data["warning"].iteritems():
                    item_dict[data["instruction"]].append(("\t"+"Item = " +instruct+"\n\t"+key+" : "+val,data["score"]))
            else:
                item_dict[data["instruction"]].append(("\t"+"Item = " +instruct,data["score"]))
        else:
            instruct = data["name"]
            if len(data['warning']) > 0:
                for key, val in data["warning"].iteritems():
                    item_dict[data["instruction"]] = [(data["instruction"]+"\n"+"\t"+"Item = " +instruct+"\n\t"+key+" : "+val,data["score"])]
            else:
                item_dict[data["instruction"]] = [(data["instruction"]+"\n"+"\t"+"Item = " +data["name"],data["score"])]
        #item_dict["Item = " +data["name"]] = data["score"]
            #= result[-1] + key+" : "+value+"\n"
        for child in data["children"]:
            get_child_data(child)
    elif data["type"] == "option_group" and "children" in data:
        for child in data["children"]:
            get_child_data(child)
    elif data["type"] == "option":
        if data["selected"] == 1:
            if instruct:
                if instruct in option_dict:
                    option_dict[instruct] = option_dict[instruct] + "\n\toption = "+data["name"]+"\n"
                else:
                    option_dict[instruct] = ("\n\toption = "+data["name"]+"\n")
        if "children" in data:
            for child in data["children"]:
                get_child_data(child)

def get_recommendation(instruction):
    """
    """
    global item_dict
    global option_dict
    global i
    if instruction:
        result.append(instruction)
        r = requests.post(url, data=json.dumps({"parent":parent, "instruction":instruction.strip()}), headers=headers)
        text =  json.loads(r.text)
        rest_parsed = 0
        if len(text["data"]) > 0:
            for data in text["data"]:
                item_dict = {}
                option_dict = {}
                i = 0
                if rest_parsed < 3:
                    rest_parsed =  rest_parsed+1
                    result.append("Resturant = "+data["name"]+"\nResturant-url = "+data["properties"]['complete']+"\n")
                    if data["type"] == "parent_group":
                        for child in data["children"]:
                            get_child_data(child)
                        item_result = ""
                        new = item_dict

                        for key, val in new.iteritems():
                            for d in sorted(val, reverse=True):
                                new_val = d[0]
                                for key, val in option_dict.iteritems():
                                    if key in d[0]:
                                        new_val = d[0] + val
                                item_result = item_result +new_val + "\n"
                        result[-1] = result[-1]+"\n"+item_result
                        # print option_list
                        # print result
                        # if option_list:
                        #     result[-1] = result[-1]+"\n"+("").join(option_list)
            diff = 3 - len(text["data"])
            for x in range(0, diff):
                result.append("")
        else:
            for x in range(0, 3):
                result.append("No Recommendations")


def initialization(inputFile, type, only_1st):
    """
    Start process of creating a csv.

    inputFile : Selected csv file by django front end.
    type : Output file type: line by line or generate result of mass query

    :return Path to new out put file that is media/output/file-current_date-output.csv

    define global variables and check for type of desired output file.

    Format input according to desired output type

    Write csv and send path of file.
    """
    global item_dict
    global option_dict
    global i
    global instruct
    global result

    outputFile = str(inputFile).split(".")[0]+str(int(round(time.time() * 1000)) % 100) + "-output.csv"
    outputFilePath = output_dir_path + outputFile
    if type == "mass_input":
        instruction_list = mass_query_format(inputFile)
    elif type == 'line_input':
        instruction_list = line_query_format(inputFile)

    with open(outputFilePath, "wb") as out_csv:
        writer = csv.writer(out_csv, delimiter=',')

        for instruction in instruction_list:
            item_dict = {}
            option_dict = {}
            i = 0
            instruct = ""
            result = []
            if instruction:
                get_recommendation(instruction)
                print "writing csv"
                if only_1st:
                    res_item = "No Item available"
                    res_option = "No Options available"
                    if len(result[1]) > 1:
                        res = result[1].split("\n")
                        for item in res[2:]:
                            if item:
                                if not "\t" in item:
                                    res_item = item
                                    break
                        if "\t" in res[res.index(res_item)+1]:
                            res_option = res[res.index(res_item)+1].replace("\t", "")
                        result = [result[0], res[0], res[1], res_item, res_option]

                writer.writerow(result)

    return "output/"+ outputFile



def mass_query_format(inputFile):
    """
    input : inputFile - In memory csv uploaded from front end
            sample : "chicken chilly
                     coke
                     veg lo mein"

    :return : list of instructions
            desired result sample : chicken chilly~coke~veg lo mein

    Replace enter separated value by ""
    if first char is (") then it means starting of query.

    if last char is (") then it means it is end of instruction

    else middle statements so prepend (~) and add to query

    convert input file in a long string of instructions sperated by (,)

    return list by splitting string.
    """
    input_instruct = ''
    for i in inputFile:
        if len(i) > 0:
            print i[0]
            if "\n" in i:
               i =  i.replace("\n", "")
            if len(i) > 0 and i[0] == '"':
                input_instruct = input_instruct+ i[1:].strip()
            elif len(i) > 0 and i[-1] == '"':
                input_instruct = input_instruct+ "~" + i[:-1].strip() + ","
            else:
                input_instruct = input_instruct + "~"+i.strip()

    return input_instruct.split(",")


def line_query_format(inputFile):
    """
    input : inputFile - In memory csv uploaded from front end
            sample : "chicken chilly
                     coke
                     veg lo mein"

    :return : list of instructions
            desired result sample : chicken chilly
                                    coke
                                    veg lo mein

    if first char is (") then replace by "".

    if last char is (") then replace by ""

    append value in a list and return

    """
    input_instruct = []
    for i in inputFile:
        if len(i) > 0:
            if "\n" in i:
               i =  i.replace("\n", "")
            if len(i) > 0 and i[0] == '"':
                i = i[1:].strip()
            elif len(i) > 0 and i[-1] == '"':

                i =  i[:-1].strip()
            else:
                i = i.strip()
            if i not in input_instruct:
                input_instruct.append(i)
    return input_instruct

# def mass_input_query(inputFile):
#     """
#     """
#     global item_dict
#     global option_dict
#     global i
#     global instruct
#     global result
#
#     outputFile = "/mass_output.csv"
#     input_instruct = ''
#     for i in inputFile:
#         if "\n" in i:
#            i =  i.replace("\n", "")
#         if i[0] == '"':
#             input_instruct = input_instruct+ i[1:]
#         elif i[-1] == '"':
#             input_instruct = input_instruct+ "~" + i[:-1] + ","
#         else:
#             input_instruct = input_instruct + "~"+i
#
#     with open(outputFile, "wb") as out_csv:
#         writer = csv.writer(out_csv, delimiter=',')
#         #writer.writerow(['instruction', "Restaurant 1", "Restaurant 2", "Restaurant 3"])
#
#         # for row in reader:
#         #     query_list = row[0].split("\n")
#         #     print query_list
#         for instruction in input_instruct.split(','):
#             item_dict = {}
#             option_dict = {}
#             i = 0
#             instruct = ""
#             result = []
#             print instruction
#             if instruction:
#                 get_recommendation(instruction)
#                 print "writing csv"
#                 writer.writerow(result)
#
#         return outputFile
#
# # reply = commandProcessorHit('oelo itop pizza')
# # print reply
# # print re.findall(r'2 label "(.*?)" end . entity "~NoTag"', reply)
#
#
# def line_input_query(file):
#     print "lin query"