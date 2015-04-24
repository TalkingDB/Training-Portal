import os

file_dir_path = os.path.expanduser("~/Smarter.Codes/customer_files/foodweasel.com/accuracy_measurement/")
import json
import socket
import re
import csv

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


# with open(file_dir_path+ 'Mturk_output.csv', 'rb') as f, open(file_dir_path+"no_tag_output.csv", "a") as out_csv:
#     reader = csv.reader(f)
#     writer = csv.writer(out_csv, delimiter=',')
#     writer.writerow(['instruction', "No Tags"])
#     for instruction in reader:
#         if instruction != "instruction":
#             result = []
#             reply = commandProcessorHit(instruction[0].strip())
#             data = reply.split('node')
#             for entity in data:
#                 if "~NoTag" in entity and "label" in entity:
#                     NoTagFound = re.findall('label "(.*?)"', entity)
#                     if NoTagFound not in result:
#                         result = result + NoTagFound
#             if result:
#                 print result
#                 writer.writerow([instruction[0], ", ".join(result)])
#             else:
#                 print "No result"
#                 writer.writerow([instruction[0], "Not Found"])

reply = commandProcessorHit('A large diet coke.')
print reply
# print re.findall(r'2 label "(.*?)" end . entity "~NoTag"', reply)


