''' controller and routes for users '''
import os
import sys
import json
from flask import request, jsonify, Response
from app import app, mongo
from bson.json_util import dumps
from bson.json_util import loads
import logger

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))

@app.route('/insert-device', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def insertDevice():
    data = request.get_json()
    if request.method == 'POST':
        feed = {}
        feed['state'] = 0
        feed['error'] = 0
        feed['version'] = 0
        foo = mongo.db.users.find_one({'email': data['users']})
        #print("Foo", foo, file=sys.stderr)
        feed['users'] = [foo['_id']]
        feed['function'] = data['function']
        feed['devicename'] = data['devicename']
        feed['devicekey'] = data['devicekey']

        mongo.db.devices.insert_one(feed)
        return jsonify({'ok': True, 'message': 'User created successfully!'}), 200

@app.route('/data-handler', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def user():
    x = {}
    if request.method == 'GET':
        query = request.args
        users_id = mongo.db.users.find_one(query['users'])
        foo = {'users': users_id}
        foo = loads(dumps(mongo.db.devices.find(users_id)))
        #print("Foo", dumps(foo), file=sys.stderr)
        return dumps(foo), 200

    data = request.get_json()
    if request.method == 'POST':
        if data.get('devicekey', None) is not None and data.get('state', None) is not None:
            mongo.db.devices.insert_one(data)
            return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    # if request.method == 'DELETE':
    #     if data.get('email', None) is not None:
    #         db_response = mongo.db.users.delete_one({'email': data['email']})
    #         if db_response.deleted_count == 1:
    #             response = {'ok': True, 'message': 'record deleted'}
    #         else:
    #             response = {'ok': True, 'message': 'no record found'}
    #         return jsonify(response), 200
    #     else:
    #         return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'PATCH':
        if data.get('devicekey', {}) != {}:
            query = {"devicekey": data["devicekey"]}
            newvalues = {'$set': {'state': data["state"]}}
            mongo.db.devices.update_one(query, newvalues)
            response = mongo.db.devices.find_one(query)['state']
            print(response, file=sys.stderr)
            return jsonify(response), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

@app.route('/share-device', methods=['POST'])
def sharedevice():
    data = request.get_json()
    if request.method == 'POST':
        foo = mongo.db.users.find_one({'email': data['shareUser']})
        mongo.db.devices.update({'devicekey': data["devicekey"]}, {'$push': {'users': foo['_id']}})
        return jsonify({'ok': True, 'message': 'User created successfully!'}), 200

@app.route('/create-user', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def createUser():
    data = request.get_json()
    if request.method == 'POST':
        print(data, file=sys.stderr)
        mongo.db.users.insert_one(data)
        return jsonify({'ok': True, 'message': 'User created successfully!'}), 200