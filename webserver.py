from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item,  db_User
from database_populator import createData
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


engine = create_engine('postgres:///blanks')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#createData()

#login stuff

@app.route('/login/')
def login():
    return "this shows da login page"


#about page
@app.route('/about/')
def about():
    return "this is the about page"


#main page route
@app.route('/')
@app.route('/home/')
def showCategories():
    categories = session.query(Category).all()
    # if not 'user_id' in login_session:
    #     return render_template('front.html', categories = categories)
    # else:
    #     print 'there is supposed to be noone here'
    return render_template('front.html', categories = categories)

@app.route('/newcategory/', methods = ['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            newCategory = Category(name=request.form['newName'], user_id = 1, description = request.form['newDescription'])
            session.add(newCategory)
            session.commit()
            flash("%s cateory has been added to the database!" % newCategory.name)
        else:
            flash('Boring --- request cancelled')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

@app.route('/category/<int:category_id>/edit', methods = ['GET', 'POST'])
def editCategory(category_id):
    try:
        category = session.query(Category).filter(Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))
    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            category.name = request.form['newName']
            category.description = request.form['newDescription']
            session.add(category)
            session.commit()
            flash("%s category has been edited." % category.name)
        else:
            flash('Boring --- request cancelled.')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=category)

@app.route('/category/<int:category_id>/delete', methods = ['GET', 'POST'])
def deleteCategory(category_id):
    try:
        category = session.query(Category).filter(Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))
    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            flash("%s category has been deleted." % category.name)
            session.delete(category)
            session.commit()
        else:
            flash('Boring --- request cancelled.')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=category)



### item stuff

@app.route('/category/<int:category_id>/', methods = ['GET', 'POST'])
def showItems(category_id):
    category = session.query(Category).filter(Category.id == category_id).one()
    items = session.query(Item).filter(Item.category_id == category.id).all()
    print category.id
    for item in items:
        print item.category_id
    ##change later
    user_id = 1
    return render_template('showItems.html', category=category, items=items, user_id=user_id)


@app.route('/category/<int:category_id>/items/new/', methods = ['GET', 'POST'])
def newItem(category_id):
    try:
        category = session.query(Category).filter(Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))
    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            newItem = Item(name=request.form['newName'], category_id = category.id, user_id = 1, description = request.form['newDescription'], price = request.form['newPrice'])
            session.add(newItem)
            session.commit()
            flash("%s has been added to the %s category" % (newItem.name, category.name))
        else:
            flash('Boring --- request cancelled')
        return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('newItem.html', category = category)

@app.route('/category/<int:category_id>/items/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(category_id, item_id):
    try:
        item = session.query(Item).filter(Item.id == item_id).one()
        category = session.query(Category).filter(Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            item.name = request.form['newName']
            item.description = request.form['newDescription']
            item.price = request.form['newPrice']
            session.add(item)
            session.commit()
            flash('%s has been successfully edited' % item.name)
        else:
            flash('Boring -- request to edit cancelled')
        return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('editItem.html', item = item, category = category)


@app.route('/category/<int:category_id>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(category_id, item_id):
    try:
        item = session.query(Item).filter(Item.id == item_id).one()
        category = session.query(Category).filter(Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))
    catname = category.name
    if request.method == 'POST':
        if request.form['submit'] == 'confirm':
            flash("%s item has been deleted." % item.name)
            session.delete(item)
            session.commit()
        else:
            flash('Boring -- request to delete cancelled')
        return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('deleteItem.html', item = item, category = category)

@app.route('/notfound/')
def notFound():
    return render_template('notFound.html')


# # show ze menu
# @app.route('/restaurant/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu')
# def showMenu(restaurant_id):
#         restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
#         items = session.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).order_by(MenuItem.course).all()
#         for i in items:
#             print i.user_id
#         return render_template('menu.html', restaurant = restaurant, items = items, creator = login_session['user_id'])

# # add a new menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/new', methods =['GET', 'POST'])
# def newMenuItem(restaurant_id):
#     restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['submit'] == "Roger":
#             name = request.form['newItemName']
#             course = request.form['newItemCourse']
#             description = request.form['newItemDescription']
#             price = request.form['newItemPrice']
#             newMenuItem = MenuItem(name = name, course = course, description = description, price = price, restaurant = restaurant, user_id = login_session['user_id'])
#             session.add(newMenuItem)
#             session.commit()
#             flash("new item %s added successfully to %s's menu!!!" % (name, restaurant.name))
#         else:
#             flash('boring...request to add new item was cancelled')
#         return redirect(url_for('showMenu', restaurant_id = restaurant.id))
#     else:
#         return render_template('newMenuItem.html', restaurant = restaurant)

# #edit the menu items
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
# def editMenuItem(restaurant_id, menu_id):
#     restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
#     item = session.query(MenuItem).filter(MenuItem.id == menu_id).one()
#     if request.method == 'POST':
#         if request.form['submit'] == 'Roger':
#             item.name = request.form['newItemName']
#             item.course = request.form['newItemCourse']
#             item.description = request.form['newItemDescription']
#             print 'the description is'
#             print item.description
#             item.price = request.form['newItemPrice']
#             session.add(item)
#             session.commit()
#             flash('Item successfully updated!')
#         else:
#             flash('Boring - edit cancelled')
#         return redirect(url_for('showMenu', restaurant_id = restaurant.id))
#     else:
#         return render_template('editMenuItem.html', restaurant = restaurant, item = item)

# #delete the menu items
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
# def deleteMenuItem(restaurant_id, menu_id):
#     restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
#     item = session.query(MenuItem).filter(MenuItem.id == menu_id).one()
#     if request.method == "POST":
#         if request.form['confirm_delete'] == "Yes - finish him":
#             session.delete(item)
#             session.commit()
#             flash('The item is no more')
#         else:
#             flash('Boring - delete cancelled')
#         return redirect(url_for('showMenu', restaurant_id = restaurant.id))
#     else:
#         return render_template('deleteMenuItem.html', restaurant = restaurant, item = item)

# # jsonify restaurants mate
# @app.route('/restaurants/JSON/', methods = ['GET'])
# def restoJSON():
#     restaurants = session.query(Restaurant).all()

#     return jsonify(Restaurants = [restaurant.serialize for restaurant in restaurants])



# #JSON all menu items of a particular restaurant
# @app.route('/restaurants/<int:restaurant_id>/JSON/', methods =['GET'])
# def itemJSON(restaurant_id):

#     restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).one()
#     items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

#     return jsonify(MenuItems = [item.serialize for item in items])

# # JSON - return just one little bitty menu item
# @app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/', methods =['GET'])
# def indyItemJSON(restaurant_id, menu_id):

#     restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).one()
#     item = session.query(MenuItem).filter(MenuItem.id==menu_id).one()

#     return jsonify(MenuItem = item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
