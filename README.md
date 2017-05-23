README

UDACITY FULL-STACK NANODEGREE - PROJECT FIVE - ITEM CATALOG
JOHN JANNETTO

INTRODUCTION:

This application serves as an item catalog for foam surfboard blanks.  They are organised into categories, with each category having any number of items.  
All parts of the site may be viewed by public, but to add, edit or delete categories and items users must sign in with either their Google or Facebook account.  

Required libraries and dependencies:

- Vagrant virtual machine installed
- Flask version 0.10.1
- SQLalchemy version 0.8.4
- datetime (python library)


Contents of FSND-Virtual-Machine/vagrant:

    pg_config.sh : VM config file (from Udacity)
    Vagrantfile (from udacity)
    Catalog directory:
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

    1. Make sure you have Vagrant virtual machine installed on your host computer

    2. Download the zip file into your preferred directory on you host computer

    3. cd into /vagrant/catalog

    4.  Power on the virtual machine:
        - cd to /FSND-Virtual-Machine/vagrant/tournament folder
        - in the CLI, type "vagrant up" to power on the virtual machine
        - then type "vagrant ssh" which logs into the machine
        - if all working, the CLI should read something like this: vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$
        - if not, see this guide for more details:
        https://docs.google.com/document/d/16IgOm4XprTaKxAa8w02y028oBECOoB1EI1ReddADEeY/pub?embedded=true

    6. Create the database in psql
        - From the command line, type "psql"
        - type “CREATE DATABASE blanks;”
	- exit the psql CLI by typing \q and then ENTER

    7.  Make sure you have either a Facebook or Google account


Operating Instructions:


    1. Run webserver.py
        - Now that you're back in the VM CLI ("trusty etc") type "python webserver.py"
        - Next go “http://localhost:8000/home on your web-browser 

    2.  To create a category, first login (upper right corner)
 
    3.  Once logged in, you can create, edit, delete categories and items at will.  

    4.  Note that you can only modify those categories and items that you have created.  



Licensing:

    No license - use and modify at will!

Contact:

    Through my GitHub johnnycp84 or johnnyjannetto@gmail.com




