import re
from flask import Blueprint, jsonify, request
from config.config import Config
from db import Mongo
from app.paginate import Paginate

bp_rent = Blueprint(
    'rent', __name__, url_prefix='/')

mongo = Mongo('192.168.99.100', 27017, 'rent591', 'houses').client()


@bp_rent.route('/' + Config.API_BASE_PATH + '/ans1', methods=['GET'])
def api_ans1():
    page = request.args.get('page', 1)
    gender = request.args.get('gender', '男生')
    region = request.args.get('region', '3')

    gender_limit = '男生' if gender == '女生' else '女生'

    query = {
        'gender_limit': {'$ne': gender_limit},
        'region': int(region),
    }
    result = mongo.find(query, {"_id": 0})

    p = Paginate(result, current_page=int(page))

    response = {
        'current_page': page,
        'total_pages': p.total_pages,
        'data': list(p.items),
    }

    return jsonify(response)


@bp_rent.route('/' + Config.API_BASE_PATH + '/ans2', methods=['GET'])
def api_ans2():
    page = request.args.get('page', 1)
    phone = request.args.get('phone', 0)

    query = {
        'phone': {'$regex': re.compile(phone)},
    }
    result = mongo.find(query, {"_id": 0})

    p = Paginate(result, current_page=int(page))

    response = {
        'current_page': page,
        'total_pages': p.total_pages,
        'data': list(p.items),
    }

    return jsonify(response)


@bp_rent.route('/' + Config.API_BASE_PATH + '/ans3', methods=['GET'])
def api_ans3():
    page = request.args.get('page', 1)
    landlord_type_not = request.args.get('landlord_type_not', '屋主')

    query = {
        'landlord_type': {'$ne': landlord_type_not},
    }
    result = mongo.find(query, {"_id": 0})

    p = Paginate(result, current_page=int(page))

    response = {
        'current_page': page,
        'total_pages': p.total_pages,
        'data': list(p.items),
    }

    return jsonify(response)


@bp_rent.route('/' + Config.API_BASE_PATH + '/ans4', methods=['GET'])
def api_ans4():
    page = request.args.get('page', 1)
    region = request.args.get('region', '1')
    landlord_type = request.args.get('landlord_type', '屋主')
    landlord_gender = request.args.get('landlord_gender', '小姐')
    landlord_last_name = request.args.get('landlord_last_name', '吳')

    query = {
        'region': int(region),
        'landlord_type': landlord_type,
        '$and': [
            {'landlord': {'$regex': '^{}'.format(landlord_last_name)}},
            {'landlord': {'$regex': '{}$'.format(landlord_gender)}},
        ],
    }
    result = mongo.find(query, {"_id": 0})

    p = Paginate(result, current_page=int(page))

    response = {
        'current_page': page,
        'total_pages': p.total_pages,
        'data': list(p.items),
    }

    return jsonify(response)
