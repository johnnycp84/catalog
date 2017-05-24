import json
import random
import string
import os
import httplib2
import requests
from database_setup import Base, Category, Item, db_User
from flask import Flask, render_template, url_for, request, redirect, flash, \
    jsonify
from flask import make_response
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
def getClientSecrets_gg():
	return os.path.join(APP_ROOT, "client_secrets_gg.json") 

def getClientSecrets_fb():
	return os.path.join(APP_ROOT, "fb_client_secrets.json")

app = Flask(__name__)

engine = create_engine('postgresql://catalog:catalog@localhost/blanks')
Base.metadata.bind = engine

# google sign in globals
CLIENT_ID = json.loads(
    open(getClientSecrets_gg(), 'r').read())['web']['client_id']
print 'CLIENT ID IS'
APPLICATION_NAME = "Blanks By Manzanita"

# our DB session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# login stuff

# create user from username and email
def createUser(login_session):
    newUser = db_User(name=login_session['username'],
                      email=login_session['email'])
    session.add(newUser)
    session.commit()
    # return user id of this new user
    user = session.query(db_User).filter_by(email=login_session['email']).one()
    return user.id


# returns a user from user id
def getUserInfo(user_id):
    user = session.query(db_User).filter_by(id=user_id).one()
    return user


# get's user id from email
def getUserID(email):
    try:
        user = session.query(db_User).filter_by(email=email).one()
        return user.id
    except:
        return None


# login route
@app.route('/login/')
def login():
    # check if user is logged in already...
    if 'username' in login_session:
        flash("You're already logged in amigo")
        redirect_url = login_session['redirect_url']
        return redirect(redirect_url)
    # CSFR state token
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in
        xrange(32))
    login_session['state'] = state
    # check to see where in the site user is coming from, if not send user
    # back to home
    if 'redirect_url' not in login_session:
        redirect_url = url_for('showCategories')
    else:
        redirect_url = login_session['redirect_url']
    return render_template('login.html', STATE=state, redirect_url=redirect_url)


# route for logging in as different user (which logs you out of current account)
@app.route('/loginother')
def loginOther():
    # capture redirect url
    # ensure user is logged in...
    if 'username' in login_session:
        redirect_url = login_session['redirect_url']
        clearLoginSession()
        login_session['redirect_url'] = redirect_url
    return redirect(url_for('login'))


# Google login/logout

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
        oauth_flow = flow_from_clientsecrets(getClientSecrets_gg(), scope='')
        oauth_flow.redirect_uri = 'postmessage'
        oauth_flow.params['access_type'] = 'offline'
        credentials = oauth_flow.step2_exchange(code)
	print 'the credentials are'
	print credentials
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
    result = json.loads(h.request(url, 'GET')[1])
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # keep redirect url but clear everything else from previous session
    redirect_url = login_session['redirect_url']
    clearLoginSession()
    # Store the access token and refresh token in the session for later uses
    login_session['access_token'] = access_token
    login_session['refresh_token'] = credentials.refresh_token
    login_session['gplus_id'] = gplus_id
    login_session['redirect_url'] = redirect_url

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
   # credentials_json = credentials.to_json()
   # login_session['credentials'] = credentials_json
   # print 'the login session is'
    print login_session
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print 'the login session is'
    print login_session

    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return 'Login Successful.  Redirecting...'


@app.route('/gdisconnect')
def gDisconnect():
    # refresh token:
    refreshToken()
    # obtain token...
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        # Clear the login session on the server side...
        clearLoginSession()
        return response
    else:
        clearLoginSession()
        flash("You've successfully logged out")
        return redirect(url_for('showCategories'))


# facebook login

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # validate the state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open(getClientSecrets_fb(), 'r').read())['web']['app_id']
    app_secret = json.loads(
        open(getClientSecrets_fb(), 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    # Extract the access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API.
    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)
    # keep redirect url but clear everything else from previous login session
    redirect_url = login_session['redirect_url']
    clearLoginSession()
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['redirect_url'] = redirect_url

    # The token must be stored in the login_session in order to properly logout,
    #  let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]

    login_session['access_token'] = stored_token

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    return 'Login Successful.  Redirecting...'


# facebook disconnect
@app.route('/fbdisconnect/')
def fbDisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    clearLoginSession()
    flash("You've successfully logged out")
    return redirect(url_for('showCategories'))


# clear login session function
def clearLoginSession():
    login_session.clear()
    return "Session cleared"


# disconnect function
@app.route('/disconnect/')
def disconnect():
    # check if anyone is connected:
    if login_session.get('access_token') is not None:
        # case where logged in via google
        if login_session['provider'] == 'google':
            return gDisconnect()
        # or else facebook
        elif login_session['provider'] == 'facebook':
            return fbDisconnect()
    else:
        flash('You are not logged in')
        return redirect(url_for('showCategories'))


# refresh google access token
@app.route('/refreshtoken')
def refreshToken():
    if 'provider' in login_session and login_session['provider'] != 'google':
        return 'no need to refresh token'
    refresh_token = login_session['refresh_token']
    with open(getClientSecrets_gg()) as json_file:
        json_data = json.load(json_file)
    client_secret = json_data['web']['client_secret']

    data = {
        'client_id': CLIENT_ID,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'}
    # r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
    r = requests.post('https://accounts.google.com/o/oauth2/token', data=data)
    answer = r.json()
    print 'the answer is'
    print answer
    if 'access_token' in answer:
        login_session['access_token'] = answer['access_token']
        return True
    else:
        # for whatever reason the access token couldn't be refreshed.
        # log the user out.
        flash('You have been logged out, please logged back in')
        clearLoginSession()
        return False


# main 'home' route
@app.route('/')
@app.route('/home/')
def showCategories():
    categories = session.query(Category).all()
    login_session['redirect_url'] = url_for('showCategories')
    # pass username and user id in template if user logged in
    if 'username' not in login_session:
        return render_template('front.html', categories=categories)
    else:
        return render_template('front.html', categories=categories,
                               username=login_session['username'],
                               user_id=login_session['user_id'])


# about page
@app.route('/about/')
def about():
    login_session['redirect_url'] = url_for('about')
    if 'username' in login_session:
        return render_template('about.html', username=login_session['username'])
    else:
        return render_template('about.html')


# add a new category
@app.route('/newcategory/', methods=['GET', 'POST'])
def newCategory():
    if 'user_id' not in login_session:
        flash('You must be logged in to create a new category')
        # set redirect url before sending to login page
        login_session['redirect_url'] = url_for('newCategory')
        return redirect(url_for('login'))
    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['submit'] == 'confirm':
            # request to create new category confirmed...

            # check both required fields are there
            if not request.form['newName'] or not request.form[
                'newDescription']:
                flash('You need to fill out both fields please')
                # set state token and render form
                state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for x
                    in xrange(32))
                login_session['state'] = state
                return render_template('newCategory.html',
                                       username=login_session['username'],
                                       STATE=state)

            newCategory = Category(name=request.form['newName'],
                                   user_id=login_session['user_id'],
                                   description=request.form['newDescription'])
            session.add(newCategory)
            session.commit()
            # refresh the google token to ensure another 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
            flash(
                "%s category added to the database!" % newCategory.name)
        else:
            # request to create new category cancelled
            flash('Boring --- request cancelled')
        return redirect(url_for('showCategories'))

    else:
        # set state token and render form
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('newCategory.html',
                               username=login_session['username'], STATE=state)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    # authentication check:
    user_id = login_session.get('user_id')
    if user_id is None:
        flash('You must be logged in to create a edit a category')
        login_session['redirect_url'] = url_for('editCategory',
                                                category_id=category_id)
        return redirect(url_for('login'))

    # check category exists
    try:
        category = session.query(Category).filter(
            Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    # authorisation check
    cat_author = category.user_id
    if user_id != cat_author:
        login_session['redirect_url'] = url_for('editCategory',
                                                category_id=category.id)
        return redirect(url_for('permissionDenied'))

    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # request to edit confirmed?
        if request.form['submit'] == 'confirm':

            # check content still there
            if not request.form['newName'] or not request.form[
                'newDescription']:
                flash('You need to fill out both fields please')
                # set state token and render form
                state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for x
                    in xrange(32))
                login_session['state'] = state
                return render_template('editCategory.html', category=category,
                                       username=login_session['username'],
                                       STATE=state)

            category.name = request.form['newName']
            category.description = request.form['newDescription']
            session.add(category)
            session.commit()
            # refresh the google refresh token to ensure another
            # 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
            flash("%s category has been edited." % category.name)
        else:
            # request to edit cancelled
            flash('Boring --- request cancelled.')
        return redirect(url_for('showCategories'))

    else:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('editCategory.html', category=category,
                               username=login_session['username'], STATE=state)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # authentication check:
    user_id = login_session.get('user_id')
    if user_id is None:
        flash('You must be logged in to create delete a category')
        login_session['redirect_url'] = url_for('deleteCategory',
                                                category_id=category_id)
        return redirect(url_for('login'))

    # check category exists
    try:
        category = session.query(Category).filter(
            Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    # authorisation check
    cat_author = category.user_id
    if user_id != cat_author:
        login_session['redirect_url'] = url_for('deleteCategory',
                                                category_id=category.id)
        return redirect(url_for('permissionDenied'))

    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['submit'] == 'confirm':
            # request to delete confirmed
            flash("%s category has been deleted." % category.name)
            session.delete(category)
            session.commit()
            # refresh the google refresh token to ensure
            # another 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
        else:
            # request to delete cancelled
            flash('Boring --- request cancelled.')
        return redirect(url_for('showCategories'))

    else:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('deleteCategory.html', category=category,
                               username=login_session['username'], STATE=state)


### item stuff -----

# show items for a particular category
@app.route('/category/<int:category_id>/', methods=['GET', 'POST'])
def showItems(category_id):
    # check category exists
    try:
        category = session.query(Category).filter(
            Category.id == category_id).one()
        items = session.query(Item).filter(
            Item.category_id == category.id).all()
    except:
        return redirect(url_for('notFound'))

    # set redirect url
    login_session['redirect_url'] = url_for('showItems',
                                            category_id=category.id)

    # render template with user info if user signed in, leave blank if not
    if 'username' in login_session:
        return render_template('showItems.html', category=category, items=items,
                               username=login_session['username'],
                               user_id=login_session['user_id'])
    else:
        return render_template('showItems.html', category=category, items=items)


# new item
@app.route('/category/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newItem(category_id):
    # authentication check:
    user_id = login_session.get('user_id')
    if user_id is None:
        flash('You must be logged in to create delete a category')
        login_session['redirect_url'] = url_for('newItem',
                                                category_id=category_id)
        return redirect(url_for('login'))

    # check category exists
    try:
        category = session.query(Category).filter(
            Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['submit'] == 'confirm':
            # request to create new item confirmed

            # check all content is there:
            if not request.form['newName'] or not request.form[
                'newDescription'] or not request.form['newPrice']:
                flash('Oh no! Ya did not fill out thee required feeeeelds!!')
                state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for x
                    in xrange(32))
                login_session['state'] = state
                return render_template('newItem.html', category=category,
                                       username=login_session['username'],
                                       STATE=state)

            newItem = Item(name=request.form['newName'],
                           category_id=category.id,
                           user_id=login_session['user_id'],
                           description=request.form['newDescription'],
                           price=request.form['newPrice'])
            session.add(newItem)
            session.commit()
            flash("%s has been added to the %s category" % (
                newItem.name, category.name))
            # refresh the token to ensure another 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
        else:
            # request was cancelled
            flash('Boring --- request cancelled')
        return redirect(url_for('showItems', category_id=category.id))

    else:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('newItem.html', category=category,
                               username=login_session['username'], STATE=state)


@app.route('/category/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # authentication check:
    user_id = login_session.get('user_id')
    if user_id is None:
        flash('You must be logged in to create delete a category')
        login_session['redirect_url'] = url_for('editItem',
                                                category_id=category_id,
                                                item_id=item_id)
        return redirect(url_for('login'))

    # check item and categories exist
    try:
        item = session.query(Item).filter(Item.id == item_id).one()
        category = session.query(Category).filter(
            Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    # authorisation check
    item_author = item.user_id
    if user_id != item_author:
        login_session['redirect_url'] = url_for('editItem',
                                                category_id=category.id,
                                                item_id=item.id)
        return redirect(url_for('permissionDenied'))

    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['submit'] == 'confirm':
            # request to edit confirmed by user:

            # check content is there:
            # check all content is there:
            if not request.form['newName'] or not request.form[
                'newDescription'] or not request.form['newPrice']:
                flash('Oh no! Ya did not fill out thee required feeeeelds!!')
                state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for x
                    in xrange(32))
                login_session['state'] = state
                return render_template('editItem.html', item=item,
                                       category=category,
                                       username=login_session['username'],
                                       STATE=state)

            item.name = request.form['newName']
            item.description = request.form['newDescription']
            item.price = request.form['newPrice']
            session.add(item)
            session.commit()
            flash('%s has been successfully edited' % item.name)
            # refresh the token to ensure another 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
        else:
            flash('Boring -- request to edit cancelled')
        return redirect(url_for('showItems', category_id=category.id))

    else:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('editItem.html', item=item, category=category,
                               username=login_session['username'], STATE=state)


@app.route('/category/<int:category_id>/items/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # authentication check:
    user_id = login_session.get('user_id')
    if user_id is None:
        flash('You must be logged in to create delete a category')
        login_session['redirect_url'] = url_for('deleteItem',
                                                category_id=category_id,
                                                item_id=item_id)
        return redirect(url_for('login'))

    # check category and item exist
    try:
        item = session.query(Item).filter(Item.id == item_id).one()
        category = session.query(Category).filter(
            Category.id == category_id).one()
    except:
        return redirect(url_for('notFound'))

    # authorisation check
    item_author = item.user_id
    if user_id != item_author:
        login_session['redirect_url'] = url_for('deleteItem',
                                                category_id=category.id,
                                                item_id=item.id)
        return redirect(url_for('permissionDenied'))

    if request.method == 'POST':

        # validate state token
        if request.form.get('STATE') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if request.form['submit'] == 'confirm':
            flash("%s item has been deleted." % item.name)
            session.delete(item)
            session.commit()
            # refresh the token to ensure another 60minutes of use.
            if 'refresh_token' in login_session:
                refreshToken()
        else:
            flash('Boring -- request to delete cancelled')
        return redirect(url_for('showItems', category_id=category.id))

    else:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for x in
            xrange(32))
        login_session['state'] = state
        return render_template('deleteItem.html', item=item, category=category,
                               username=login_session['username'], STATE=state)


# route for 'not found'
@app.route('/notfound/')
def notFound():
    username = login_session.get('username')
    return render_template('notFound.html', username=username)


# route for permission denied
@app.route('/permissiondenied/')
def permissionDenied():
    username = login_session.get('username')
    return render_template('permissionDenied.html',
                           username=username)


# JSON all categories as shown on homepage
@app.route('/home/JSON/', methods=['GET'])
def categoryJSON():
    categories = session.query(Category).all()

    return jsonify(categories=[category.serialize for category in categories])


# #JSON all items of a particular category
@app.route('/category/<int:category_id>/JSON/', methods=['GET'])
def itemJSON(category_id):
    category = session.query(Category).filter(Category.id == category_id).one()
    items = session.query(Item).filter(Item.category_id == category.id).all()

    return jsonify(Items=[item.serialize for item in items])


# # JSON - return just one particular item
@app.route('/category/<int:category_id>/items/<int:item_id>/JSON/',
           methods=['GET'])
def indyItemJSON(category_id, item_id):
    item = session.query(Item).filter(Item.id == item_id).one()

    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run()
