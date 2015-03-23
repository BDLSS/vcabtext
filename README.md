vcabtext
========
Django website for holding vocabularies and other text file formats
to create persistent URLS.

Features
--------
* A browse interface to see "public" documents.
* An admin interface for maintaining the data.

Browse interface
----------------
The browsing interface is the main way accessing the site. It features:

* Complete AZ of items.
* Items grouped by collections.
* An item has an information page, that can be used as a persistent URL.
* Single page showing all items.

What are items?
---------------
An item can be:

* any text based document in particular formats. (e.g. *.rdf, *.xsd)
* downloaded for opening in a text editor.
* viewed online with or without syntax highlighting.


Videos
------
These videos are for an early beta version, there are a few features added
based upon user feedback. 

* Introduction to website: https://youtu.be/WNjLxuOYXlI
* Introduction to admin interface: https://youtu.be/3eU0MrHDUZc
* Adding an item: https://youtu.be/-k3BxTK6zlM

The main changes not shown in these videos are:

* The browse list has a third option (single page of all items)
* Each collection gets their own webpage.
* Admin: Values for "creators" and "contributor" are from a controlled lists managed via the "agent" data model.
