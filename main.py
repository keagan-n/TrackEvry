#firebase imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#flask imports 
from flask import Flask,request,jsonify, render_template
app = Flask(__name__)
#other python libraries
import datetime


#iniitialize the SDK credentials from json key
cred = credentials.Certificate("productivity-app-2175e-firebase-adminsdk-zjbx9-f8872b4741.json")
firebase_admin.initialize_app(cred)

#initialize firestore instance
db=firestore.client()

#create Flask App object
app = Flask(__name__,
            static_url_path='',
            static_folder='static')

#Categories -- A set, can be added to later by the user in the UI
#   defaults are 'work' and 'life'
#   Even if the user can implement it on their own, the categories will implement lower case
categories = {'work','life'}

#Collections
#   Tasks and Events
task_coll=db.collection('task')
event_coll=db.collection('event')

#Consants
now = datetime.datetime.now()
today = datetime.datetime.today()

#function to delete all documents in the collection given as argument
def delete_collection(coll_ref):
    docs = coll_ref.get()
    for doc in docs:
        key = doc.id
        coll_ref.document(key).delete()
    return coll_ref.stream()

#each @app method is tied to a url
@app.route('/',methods =['GET']) #this is the default html page
def root():
    docs = delete_collection(task_coll)
    new_docs = delete_collection(event_coll)
    return render_template("index.html", lists=docs,checks=new_docs)
 


#new_task and new_event are quick ways to make new... tasks and events
def new_task(name: str,category: str,description: str, deadline: datetime) -> dict:
    return {
        'name':name,
        'deadline':deadline,
        'description':description,
        'category':category
        
    }


def new_event(name: str,category: str,description: str,start_time: 'date',end_time: 'date') -> dict:
    return {'name': name,
            'category': category,
            'description': description,
            'start_time': start_time,
            'end_time': end_time
            }

#fields for each task are "deadline" , "category", "description", and "name"
# new_item = {'category':'Test',
#     'name':'hw one',
#     'deadline':datetime.datetime.now(),
#     'description':'hope this works'}
    
# db.collection('task').add(new_item)



@app.route('/add',methods=['GET','POST'])
def createTask():
    """ create() adds a document into the Firestore collection with a request body"""
    try:
        id = request.form['text']
        #id is the name of the document
        task_coll.document(id).set({}) #creates a document with the name "id"
        task_list = db.collection('task').stream()
        event_list = db.collection('event').stream()
        return render_template("index.html", lists=task_list,checks=event_list)
    except Exception as e:
        return f"An Error Occurred:{e}"
#decide whether so use known or auto IDs


@app.route('/addEvent',methods=['POST'])
def createEvent():
    try:

        id = request.form['new-task-input']
        event_coll.document(id).set({})
        docs = db.collection('event').stream()
        task_list = db.collection('task').stream()
        event_list = db.collection('event').stream()
        return render_template("index.html", lists=task_list,checks=event_list)

    except Exception as e:
        return f"An Error Occurred:{e}"


@app.route('/update',methods=['POST','PUT'])
def updateTask():
    '''update() updates a document and all of its fields inside with the passed value'''
    try:
        id = request.json['doc name']
        task_coll.document(id).update(request.json)
        return jsonify({"success":True}),200 #this displays success in console 
    except Exception as e:
        return f"An Error Occurred:{e}"


@app.route('/delete',methods =['GET','DELETE'])
def deleteTask():
    ''' delete() deletes a document that matches the id given'''
    try:
        id = request.args.get('doc name')
        task_coll.document(id).delete()
        return jsonify({"success":True}),200
    except Exception as e:
        return f'An Error Occurred: {e}'



if __name__ == "__main__":
    app.run()


