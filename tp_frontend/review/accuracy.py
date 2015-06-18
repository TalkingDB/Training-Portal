import os

import json
import requests
import csv
import socket
import re
import time
import urllib
output_dir_path = os.path.expanduser("~/Smarter.Codes/src/TrainingPortal/tp_frontend/review/media/output/")
url="http://localhost/"
parent = '{"key": "uid","value":["72894", "81443", "70681", "30857", "52951", "73498", "70263", "68964", "29602", "79779", "65010", "68924", "46911", "75328", "79960", "38911", "74661", "71519", "70131", "69384"]}'
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
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
        s.connect(("testing.smarter.codes", 5012))
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
def get_child_data(data, matching):
    """
    """
    global instruct
    global i


    if data["type"] == "group" and "children" in data:
        for child in data["children"]:
            get_child_data(child, matching)
    elif data["type"] == "item" and "children" in data:
        #result[-1] = result[-1] + "Item = "+data["name"]+"\n"
        if data["instruction"] in item_dict:
            if [item for item in item_dict[data["instruction"]] if "\t"+"Item = " +data["name"] in item]:
                i = i+1
                instruct = data["name"]+"-"+str(i)
            else:
                instruct = data["name"]
            if matching:
                if "." in instruct:
                    item_name = instruct.split(".")
                    if len(item_name[0]) < 4 and item_name[0] != "Dr":
                        instruct = item_name[1].strip()
            if len(data['warning']) > 0:
                if matching:
                    item_dict[data["instruction"]].append((instruct,data["score"]))
                else:
                    for key, val in data["warning"].iteritems():
                        item_dict[data["instruction"]].append(("\t"+"Item = " +instruct+"\n\t"+key+" : "+val,data["score"]))
            else:
                if matching:
                    item_dict[data["instruction"]].append(("\t" +instruct,data["score"]))
                else:
                    item_dict[data["instruction"]].append(("\t"+"Item = " +instruct,data["score"]))
        else:
            instruct = data["name"]
            if len(data['warning']) > 0:
                if matching:
                    item_dict[data["instruction"]] = [(instruct,data["score"])]
                else:
                    for key, val in data["warning"].iteritems():
                        item_dict[data["instruction"]] = [(data["instruction"]+"\n"+"\t"+"Item = " +instruct+"\n\t"+key+" : "+val,data["score"])]
            else:
                if matching:
                    if "." in data["name"]:
                        item_name = data["name"].split(".")
                        if len(item_name[0]) < 4 and item_name[0] != "Dr":
                            data["name"] = item_name[1].strip()
                    item_dict[data["instruction"]] = [(data["name"],data["score"])]
                else:
                    item_dict[data["instruction"]] = [(data["instruction"]+"\n"+"\t"+"Item = " +data["name"],data["score"])]
        #item_dict["Item = " +data["name"]] = data["score"]
            #= result[-1] + key+" : "+value+"\n"
        for child in data["children"]:
            get_child_data(child, matching)
    elif data["type"] == "option_group" and "children" in data:
        for child in data["children"]:
            get_child_data(child, matching)
    elif data["type"] == "option":
        if data["selected"] == 1:
            if instruct:
                if instruct in option_dict:
                    if matching:
                        option_dict[instruct] = option_dict[instruct] + "\n\t"+data["name"]+"\n"
                    else:
                        option_dict[instruct] = option_dict[instruct] + "\n\toption = "+data["name"]+"\n"
                else:
                    if matching:
                        option_dict[instruct] = ("\n\t"+data["name"]+"\n")
                    else:
                        option_dict[instruct] = ("\n\toption = "+data["name"]+"\n")
        if "children" in data:
            for child in data["children"]:
                get_child_data(child, matching)

def get_recommendation_only_1st(instruction,  only_1st, writer, matching):
    """
    """
    global item_dict
    global option_dict
    global i
    params = urllib.urlencode({'parent': parent, 'instruction': instruction.strip()})
    if instruction:
        r = requests.post(url, params=params, headers=headers)
        text =  json.loads(r.text)
        rest_parsed = 0
        total_rest = 1#total number of restaurants
        if len(text["data"]) > 0:
            for data in text["data"]:
                item_dict = {}
                option_dict = {}
                i = 0
                if rest_parsed < total_rest:
                    rest_parsed =  rest_parsed+1
                    if data["type"] == "parent_group":
                        for child in data["children"]:
                            get_child_data(child, matching)
                        item_result = ""
                        new = item_dict
                        for key, val in new.iteritems():
                            # print key
                            # print val
                            # print sorted(val, reverse=True)
                            result = []
                            result.append(key)
                            max_score = 0
                            options_found = 0
                            best_item = ''
                            for d in sorted(val, reverse=True):
                                new_val = d[0]
                                score = d[1]
                                if score > max_score:
                                    max_score = score
                                    best_item = d[0]
                            if not matching:
                                if "Item = " in best_item:
                                    sep = 'Item = '
                                    best_item = best_item.split(sep, 1)[1]
                            result.append(best_item)
                            for key, val in option_dict.iteritems():
                                if key in best_item:
                                    val = val.strip()
                                    result.append(val)
                                    options_found = 1
                            if options_found == 0:
                                result.append("No Options")
                            if matching:
                                result.append(data["name"]+"\n"+data["properties"]['complete'])
                                if "soda" in result[1]:
                                    result[1] = result[2]
                            else:
                                result.append("Resturant = "+data["name"]+"\nResturant-url = "+data["properties"]['complete'])
                            writer.writerow(result)
                    if len(data["not_found"]) > 0:
                        print_notfound(data["not_found"], writer)
        else:
            no_result = [instruction]
            for x in range(0, 3):
                no_result.append("No Recommendations")
            writer.writerow(no_result)



#print not found items into csv
#takes csv writer and not found key as key
def print_notfound(data, writer):
    for item in data:
        result.append(item)
        result.append("Not Found")
    writer.writerow(result)


def get_recommendation(instruction, writer, matching):
    """
    """
    global item_dict
    global option_dict
    global i
    params = urllib.urlencode({'parent': parent, 'instruction': instruction.strip()})
    if instruction:
        result.append(instruction)
        r = requests.post(url, params=params, headers=headers)
        
        text =  json.loads(r.text)
        rest_parsed = 0
        if len(text["data"]) > 0:
            for data in text["data"]:
                item_dict = {}
                option_dict = {}
                i = 0
                if rest_parsed < 3:
                    rest_parsed =  rest_parsed+1
                    if matching:
                        result.append(data["name"]+"\n"+data["properties"]['complete']+"\n")
                    else:
                        result.append("Resturant = "+data["name"]+"\nResturant-url = "+data["properties"]['complete']+"\n")
                    if len(data["not_found"]) > 0:
                         for item in data["not_found"]:
                            result.append(item)
                            result.append(" Not Found\ n")
                    if data["type"] == "parent_group":
                        for child in data["children"]:
                            get_child_data(child, matching)
                        item_result = ""
                        new = item_dict

                        for key, val in new.iteritems():
                            #sorted using score
                            for d in sorted(val, key=lambda e: e[1], reverse=True):
                                new_val = d[0]
                                for key, val in option_dict.iteritems():
                                    if key in d[0]:
                                        new_val = d[0] + val
                                item_result = item_result +new_val + "\n"
                        result[-1] = result[-1]+"\n"+item_result
            diff = 3 - len(text["data"])
            for x in range(0, diff):
                result.append("")
        else:
            for x in range(0, 3):
                result.append("No Recommendations")


def initialization(inputFile, type, only_1st, matching):
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
                if(only_1st):
                    get_recommendation_only_1st(instruction, only_1st, writer, matching)
                else:
                    get_recommendation(instruction, writer, matching)
                    writer.writerow(result)
                # exit()
                # if only_1st:
                #     res_item = "No Item available"
                #     res_option = ""
                #     res_item_key = ''
                #     if len(result[1]) > 1:
                #         res = result[1].split("\n")
                #         if len(res[2:]) > 0:
                #             for item in res[2:]:
                #                 if item:
                #                     if not "\t" in item:
                #                         res_item_key = res[res.index(item)+1]
                #                         res_item = res[res.index(item)+1].replace("\t", "")
                #                         break
                #             # if len(res) >
                #             for x in range(res.index(res_item_key)+1, len(res)):
                #                 if "\toption" in res[x]:
                #                     res_option+= res[x].replace("\t", "")
                #                     res_option+="\n"
                #
                #
                #             result = [result[0], res[0], res[1], res_item, res_option]
                # print "<---writing csv"
                # print result;
                # print "writing csv--->"
                # writer.writerow(result)

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
    input_instruct = []
    spamreader = csv.reader(inputFile, delimiter=',')
    for i in spamreader:
        if len(i) > 0:
            if "\r\n" in i[0]:
                input_instruct.append(str(i[0].replace("\r\n", "~")))
            elif "\r" in i[0]:
                input_instruct.append(str(i[0].replace("\r", "~")))
            elif "\n" in i[0]:
                input_instruct.append(str(i[0].replace("\n", "~")))
            else:
                input_instruct.append(str(i[0].strip()))
    return input_instruct


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
    spamreader = csv.reader(inputFile, delimiter=',')
    for i in spamreader:
        if len(i) > 0:
            if "\n" in i[0]:
                for val in i[0].split("\n"):
                    input_instruct.append(val)
            else:
                input_instruct.append(str(i[0].strip()))

    # for i in inputFile:
    #     print i
    #     if len(i) > 0:
    #         if "\n" in i:
    #            i =  i.replace("\n", "")
    #         if i.strip()[0] == '"':
    #             i = i.strip()[1:]
    #         elif i[-1] == '"':
    #             i =  i.strip()[:-1]
    #         else:
    #             i = i.strip()
    #         # To stop duplicate inputs uncomment if i.strip() not in input_instruct
    #         # it will check if we have saved same query before.
    #         # and remove if True
    #
    #         #if i.strip() not in input_instruct:
    #         if True:
    #             input_instruct.append(i.strip())
    return input_instruct
