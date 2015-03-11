from subprocess import call
import sys


def mongo_import(database, collection, filePath, flags=''):
    print ('mongoimport -d ' + database + ' -c ' + collection + ' --file ' + filePath + ' ' + flags)
    call ('mongoimport -d ' + database + ' -c ' + collection + ' --file ' + filePath + ' ' + flags,shell=True)
        
def mongo_collection_drop(database, collection):
    print ('mongo ' + database + ' --eval "db.' + collection + '.drop()"')
    call('mongo ' + database + ' --eval "db.' + collection + '.drop()"',shell=True)
        
        
def mongo_query(database, collection,queryFile):
    print 'mongo ' + database + ' ' + queryFile
    call('mongo ' + database + ' ' + queryFile,shell=True)
    print "Import complete"