# Item-Catalog
A web application completed as Project 3 of the Udacity Full Stack Web Developer Nanodegree
Udacity Item Catelog

## Description

A web application that will list a categories and associated Items. User can login the applicaion using their google account. Authorised user will have the permission add/edit/delete the items

## JSON API end poinnts
/catogories/JSON
Shows the information of all categories

/catogoryItems/<int:category_id>/JSON
Shows the items details of particular category

/Items/JSON
Shows the information of all the items

## Setting up the database
- run the command python3 database_setup.py
- run the command python3 Insertdata.py

## Running the applicaion with Vagrant
- Clone the repository
- Launch the Vagrant VM with the command vagrant up
- vagrant ssh to ssh into the VM.
- Navigate to the folder using the command cd /vagrant/itemcatelog/itemcatelog
- Run the applicaiton python3 category.py
