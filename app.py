from flask import Flask, request
#import werkzeug._reloader
from flask_restplus import Api, Resource, fields, inputs, marshal_with
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest
from functools import wraps 

from datetime import date
import time
from flask_restplus.fields import String
from flask_restplus import reqparse
import sqlite3 as sql
import sys
import sqlite3
from _sqlite3 import Error
import datetime

DATABASE = 'data.db'

query = reqparse.RequestParser()
query.add_argument('status', type=str)


authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'API-KEY'
    }
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, authorizations=authorizations, version='1.0', title='Nayan MVC API',
    description='A simple Restplus+sqlite TodoMVC API',
)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'API-KEY' in request.headers:
            token = request.headers['API-KEY']

        if not token:
            return {'message' : 'Token is missing.'}, 401

        if token != 'admin':
            return {'message' : 'Your token is incorrect!!!'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated

ns = api.namespace('todos', description='TODO operations')

def checkdate(date):
    yy,mm,dd=date.split('-')
    dd=int(dd)
    mm=int(mm)
    yy=int(yy)
    if(mm==1 or mm==3 or mm==5 or mm==7 or mm==8 or mm==10 or mm==12):
        max1=31
    elif(mm==4 or mm==6 or mm==9 or mm==11):
        max1=30
    elif(yy%4==0 and yy%100!=0 or yy%400==0):
        max1=29
    else:
        max1=28
    if(mm<1 or mm>12):
        raise BadRequest("Worng month date")
    elif(dd<1 or dd>max1):
        raise BadRequest("Worng day date")
    else:
        return True
def checkstatus(status):
    st=str(status)
    st=st.lower()
    if(st=='finished'):
        return st
    elif(st=='pending'):
        return st
    else:
        raise BadRequest('only accept finished or pending')
def message(msg):
    return msg

class TimeFormat(fields.DateTime):
    __schema_example__ = time.strftime('%Y-%m-%d')
 

     
class statusFormat(fields.String):
    __schema_example__ = '\'Finished\'or\'Pending\''
    

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by':TimeFormat,
    'status':statusFormat
    
})


def query_db(query, args=(), one=False):
    with sql.connect("data.db") as con:
        con.row_factory = sql.Row
        rv=0
        
        try:
            cur = con.cursor()
            cur.execute(query,args)
            rv=cur.fetchall()
        except Error as e:
            rv.append("error in insert operation")
            cur.rollback()            
        finally:
            return rv
            cur.close

message=api.model('Message', {
    'message': fields.Integer(readonly=True, description='The task unique identifier'),    
    })
class TodoDAO(object):
    def __init__(self):
        count=query_db('SELECT COUNT(*) FROM (SELECT * FROM tables)');
        self.counter =count[0][0]
        self.todos = []
        self.user=[]
        query_db('CREATE TABLE IF NOT EXISTS tables (id INTEGER NOT NULL primary key,task TEXT , due_by TEXT ,status TEXT )', one=True)
    
    
    
    
    #"GET /due?due_date=yyyy-mm-dd"
    def due(self, due_date):
        if checkdate(due_date):
            user = query_db("SELECT * FROM tables WHERE due_by=?",[due_date], one=True)
            return user
        else:
            raise BadRequest("wrong date")
    
    "GET /overdue"
    def overdue(self):
        today = time.strftime('%Y-%m-%d')
        print (today,  file=sys.stdout)
        user = query_db("SELECT * FROM tables WHERE due_by<?",[today], one=True)
        return user

    "GET /finished" 
    def finish(self,finished):
        if checkstatus(finished):
            user = query_db("SELECT * FROM tables WHERE status=? ",[finished], one=True)
            return user
        api.abort(404, "Todo {} doesn't exist".format(user))
            

    def get(self, id):
        user = query_db("SELECT * FROM tables WHERE id=? ",[id], one=True)
        return user
        api.abort(404, "Todo {} doesn't exist".format(user))

    def all(self):
        coll=[]
        user = query_db("SELECT * FROM tables", one=True)
        return user
        api.abort(404, "Todo {} doesn't exist".format(user))

    def create(self, data):
        todo = data
        duedate=todo['due_by']
        status=checkstatus(todo['status'])
        if checkdate(duedate):
                data['id']=self.counter=self.counter+1
                user = query_db('INSERT INTO tables (task,due_by,status) VALUES (?,?,?)',
                        [data['task'],data['due_by'],status], one=True)
                return data
        else:
            raise BadRequest('i told ya')
        

    def update(self, id, data):
        todo = data
        coll=[]
        status=checkstatus(todo['status'])
        user = query_db('UPDATE tables SET task=?,due_by=?,status=? WHERE id=?',
                [data['task'],data['due_by'],status,id], one=True)
        todo['status']=str('Your data is successfully Updated')
        return todo
        

    def delete(self, id):
        query='DELETE FROM tables WHERE "id"='
        user=query_db(query+str(id))
        todo = user
        #return message("Successfully deleted").format(message)
        
        return todo


DAO = TodoDAO()






@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo, envelope='resource')
    def get(self, **kwargs):
        '''List all tasks'''
        return DAO.all()

    @api.doc(security='apikey')
    @token_required
    @ns.expect(todo)
    #@api.marshal_with(model, envelope='resource')
    @ns.marshal_with(todo,code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload),201

@ns.route('/due')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''   
    @ns.doc('overdue')
    @ns.marshal_with(todo)
    def get(self):
        '''Check overdue task'''
        return DAO.overdue()
        

@ns.route('/<string:status>')
@ns.response(404, 'Todo not found')
@ns.param('status')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''  
    @ns.doc('finished')
    @ns.expect('status')
    @ns.marshal_with(todo)
    def get(self,status):
        '''Check finished task'''
        return DAO.finish(status)

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @api.doc(security='apikey')
    @token_required
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @api.doc(security='apikey')
    @token_required
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/due <string:due_by>')
@ns.response(404, 'Todo not found')
@ns.param('due_by')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @api.doc(security='apikey')
    @token_required
    @ns.marshal_with(todo)
    def get(self, due_by):
        '''Fetch a due date'''
        return DAO.due(due_by)
        

if __name__ == '__main__':
    app.run(debug=True)