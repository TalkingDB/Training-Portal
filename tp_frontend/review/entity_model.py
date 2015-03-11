__author__="Atul Tagra"
__email__="atul@ignitras.com"
__date__ ="$Nov 11, 2014 3:55:09 PM$"


class EntityModel():
    
    def __init__(self, db, table):
        self.table = db[table]
    
    def insertQuestion(self, subject):
        existing = self.exists(subject['question'])

        if not existing:
            subject_id = self.table.insert(subject)
        else:
            subject_id = existing

        return subject_id


    def insert(self, subject):
        existing = self.exists(subject['name'])
        
        if not existing:
            subject_id = self.table.insert(subject)
        else:
            subject_id = existing
            
        return subject_id
    
    def insert_many(self, documents):
        _ids = self.table.insert(documents)
        return _ids
    
    def exists(self, subject):
        result = self.table.find_one({"name":subject})
        if result:
            return result['_id']
        else:
            return False
        
    def select_one(self, where):
        result = self.table.find_one(where)
        return result
    
    def group_by(self, a, b , c, d):
        result = self.table.group(a, b, c, d)
        return result
        
    def select_all(self):
        result = self.table.find()
        return result
    
    def select_by(self, where):
        result = self.table.find(where)
        return result
    
    def select_by_distinct(self, where, field):
        result = self.table.find(where).distinct(field)
        return result
    
    def update(self, where, document):
        result = self.table.update(where, document, False)
        return result
    
    def count(self):
        result = self.table.count()
        return result
   
    def remove(self):
        self.table.remove()
        return True
