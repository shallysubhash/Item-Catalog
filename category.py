#!/usr/bin/env python3
from flask import Flask, render_template, request,  \
                  redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Item, Base
from os import environ
import json
# import for google sign in
from flask import session as login_session
import random
import string
from datetime import datetime

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu app"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    print(state)
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    return "The current session state is %s" % login_session['state']


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current'
                                            'user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/')
def showcatalogs():
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Item).order_by(Item.id.desc())
    return render_template('category.html', categories=categories, items=items)


@app.route('/category/<int:category_id>')
def showCategoryItems(category_id):
    # Get all the categories
    categories = session.query(Category).order_by(Category.name)
    # Get items of selected category
    items = session.query(Item).filter_by(Category_id=category_id).all()
    return render_template('category.html', categories=categories, items=items)


@app.route('/Item/<int:item_id>')
def ShowItem(item_id):
    # Get the item
    singleItem = session.query(Item).filter_by(id=item_id).one()
    return render_template('CategoryItem.html', Item=singleItem)


@app.route('/EditItem/<int:item_id>', methods=['GET', 'POST'])
def editItem(item_id):
    singleItem = session.query(Item).filter_by(id=item_id).one()
    categories = session.query(Category).order_by(Category.name)
    if request.method == 'POST':
        singleItem.name = request.form['name']
        singleItem.description = request.form['description']
        singleItem.category_id = request.form['category']
        session.add(singleItem)
        session.commit()
        return redirect(
            url_for('showcatalogs'))
    else:
        return render_template('EditItem.html', Item=singleItem, categories=categories)


@app.route('/DeleteItem/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(
            url_for('showcatalogs'))
    else:
        return render_template('deleteItem.html', Item=item)


@app.route('/NewItem', methods=['GET', 'POST'])
def NewItem():
    categories = session.query(Category).order_by(Category.name)
    if request.method == 'POST':
        ItemToAdd = Item(Category_id=request.form['category'],
                         description=request.form['description'], name=request.form['name'])
        session.add(ItemToAdd)
        session.commit()
        return redirect(
            url_for('showcatalogs'))
    else:
        return render_template('NewItem.html', categories=categories)

# JSON to view catogories
@app.route('/catogories/JSON')
def categoriesJSON():
    categories = session.query(Category).order_by(Category.name)
    return jsonify(categories=[c.serialize for c in categories])

# to get items of a single category
@app.route('/catogoryItems/<int:category_id>/JSON')
def CategoryItemsJSON(category_id):
    CategoryItems = session.query(Item).filter_by(Category_id=category_id)
    return jsonify(CategoryItems=[c.serialize for c in CategoryItems])

# to get all items
@app.route('/Items/JSON')
def ItemsJSON():
    Items = session.query(Item).order_by(Item.name)
    return jsonify(Items=[c.serialize for c in Items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
