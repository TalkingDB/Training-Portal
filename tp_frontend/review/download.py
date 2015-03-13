from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from pymongo.mongo_client import MongoClient
from django.contrib.auth.models import User
import cStringIO as StringIO
import csv



client = MongoClient("localhost",27017)
#client.noisy_NER.authenticate("fwadmin", "fwadmin")
db = client['noisy_NER']
entity_collection = db['questions']
synonym_collection = db['entity']

@login_required
def download(request, user_id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404

    users = User.objects.all()
    user_dict = {user.id: user.username for user in users}
    mongodata =entity_collection.find({})
    def data():
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["frequency","question","Trainers"])
        for data in mongodata:
            question = data['question']
            if '>' in question:
                question = data['question'].split('>')[1].replace("_", " ").replace("-", " ")
            csvwriter.writerow([question,get_string(data['trainers'], user_dict)])
        yield csvfile.getvalue()

    response = HttpResponse(data())
    response["Content-Disposition"] = "attachment; filename=Report.csv"
    return response


def get_string(trainers, users):

    list = map(lambda trainer: users[trainer], trainers)
    return ' , '.join(list)

@login_required
def user_report_download(request, id):
    """
    """
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404
    user = User.objects.get(id=id)
    questions = entity_collection.find({"trainers": {"$in": [user.id]}})
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+ str(user.username)+ "_report" +'.csv"'
    writer = csv.writer(response)
    writer.writerow(['question', 'status', 'approved', 'disapproved'])
    data_list = []
    for data in questions:
        csv_list = []
        approved_synonyms = []
        disapproved_synonyms = []
        type = "surface_text"
        find = "entity_url"
        question = data['question']
        if '>' in data['question']:
            type = "entity_url"
            find = "surface_text"
            question = data['question'].split('>')[1].replace("_", " ").replace("-", " ")
        synonyms = synonym_collection.find({
             type: data['question']
         }, {"mentioned_in": 0, "how_this_record": 0, "seed_category":0, "frequency": 0, "intended_trainer":0})
        for synonym in synonyms:
            if '>' in synonym[find]:
                text = synonym[find].split('>')[1].replace("_", " ").replace("-", " ")
            else:
                text = synonym[find]
            if 'approved_by_trainer' in synonym and user.id in synonym['approved_by_trainer']:
                approved_synonyms.append(text)
            if 'disapproved_by_trainer' in synonym and user.id in synonym['disapproved_by_trainer']:
                disapproved_synonyms.append(text)
        if len(approved_synonyms) > 0 or len(disapproved_synonyms) > 0:
            if len(approved_synonyms) > len(disapproved_synonyms):
                for i in range(len(approved_synonyms)):
                    csv_list.append([question, "answered", "", ""])
            else:
                for i in range(len(disapproved_synonyms)):
                    csv_list.append([question, "answered", "", ""])
            for i in range(len(approved_synonyms)):
                csv_list[i][2] = approved_synonyms[i]

            for i in range(len(disapproved_synonyms)):
                csv_list[i][3] = disapproved_synonyms[i]
        else:
            csv_list.append([question, "skipped", "", ""])
        for data in csv_list:
            data_list.append(data)

    for data in data_list:
        try:
            writer.writerow(data)
        except Exception as e:
            print e
    return response