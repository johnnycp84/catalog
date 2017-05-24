README

UDACITY FULL-STACK NANODEGREE - PROJECT SEVEN -DEPLOYMENT OF ITEM CATALOG
JOHN JANNETTO

INTRODUCTION:

This application serves as an item catalog for foam surfboard blanks.  They are organised into categories, with each category having any number of items.  
All parts of the site may be viewed by public, but to add, edit or delete categories and items users must sign in with either their Google or Facebook account.  

The project has been deployed on Amazon LightSail:

URL: http://ec2-54-236-4-187.compute-1.amazonaws.com/home/

IP address of server:54.236.4.187

Required libraries and dependencies:

- Vagrant virtual machine installed
- Flask version 0.10.1
- SQLalchemy version 0.8.4
- datetime (python library)


Contents of repositoryt:

  
    Catalog directory:
	- __init__.py : main application (a modified of development app webserver.py
	- webserver.py : main web server file that you run through vagrant machine
	- database_setup.py : contains table descriptions for database
	- client_secrets_gg.json : contains client id and secret for google sign-in
	- fb_client_secrets.json : contains id/secret for Facebook sign-in
	- templates directory
	- static directory (contains images, css, js files)
	- templates:
		about.html  deleteCategory.html  editCategory.html  fblogin.html  login.html        newItem.html   permissionDenied.html
		base.html   deleteItem.html      editItem.html      front.html    newCategory.html  notFound.html  showItems.html

Installation Instructions:

    1. Make sure you have a computer with an internet connection and modern web browser

    2.  Make sure you have either a Facebook or Google account


Operating Instructions:


    1. Go to this URL:http://ec2-54-236-4-187.compute-1.amazonaws.com/home/

    2.  To create a category, first login (upper right corner)
 
    3.  Once logged in, you can create, edit, delete categories and items at will.  

    4.  Note that you can only modify those categories and items that you have created.  

Project Notes:

 - Server has Ubuntu 16.04.2.  Web server is Apache/2.4.18 and application handleris mod-wsgi.  Database server is Postgresql 9.5
 - Flask 0.10.1 was used as the framework for this project
 - Security:
	- password authentification through remote login disabled
	- remote login by root user disabled
	- firewall in place (ufw) 
 - __init__.py was modified : secret key removed, absolute file path functions created to read API client secret JSON files
 - git directory hidden (apache2 conf file edited)

Licensing:

    No license - use and modify at will!

Contact:

    Through my GitHub johnnycp84 or johnnyjannetto@gmail.com




