Cartography App for GeoNode
===========================

This is a GeoNode extension to handle documents in farious formats, even images. It works essentially by enabling files to be attached to GeoNode Map. The layers used to compose the map may or may not be registered in GeoNode.

Installation
------------

#. Install the documents app:

    source bin/activate

    pip install -e git+git://github.com/simod/geonode-documents.git#egg=documents

#. Edit your settings.py file and add ``documents`` to the list of installed apps

#. Append the following line to your urls.py::

     (r'^documents/', include('documents.urls')),

# Then re-run ``syncdb`` and reload your web server.

Extras
------

#. In order to have the documents directly linked in the main menu bar:

	(basic) replace the page_layout.html file provided in the "extras" folder with the original one in your template folder.
	
	(advanced) copy the content of the page_layout_snippet.html and insert it in your page_layout.html file in the "nav" block.

#. In order to have the documents linked in the map detail template:

	(basic) replace the mapinfo.html file in the "extras/maps" folder with the original one in your template folder.
	
	(advanced) copy the content of the mapinfo_snippet.html and insert it in your mapinfo.html file in the "sidebar" block.

Features
--------

- (Planned) Upload form for document. It can either be attached to an existing map or a new one can be created with a custom widget to select the bounding box.
- (Planned) Integration with GeoNetwork (maps and files registered in GeoNetwork)
- (Planned) Easy installable on an existing GeoNode installation. Without having to alter existing tables / data.
- (Planned) Auto pdf document creation after using the print button in the map composer.

