Documents App for GeoNode
===========================

This is a GeoNode extension to handle documents in various formats, even images. It works essentially by enabling files to be attached to GeoNode Map. The layers used to compose the map may or may not be registered in GeoNode.

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

	(basic) replace the base.html file provided in the "extras" folder with the original one in your template folder. (only use this if you have never modified the base.html file)
	
	(advanced) copy the content of the base_snippet.html and insert it in your base.html file in the "nav" block.

#. In order to have the documents linked in the map detail template:

	(basic) replace the mapinfo.html file in the "extras/maps" folder with the original one in your maps/template/maps folder. (only use this if you have never modified the mapinfo.html file)
	
	(advanced) copy the content of the mapinfo_snippet.html and insert it in your maps/templates/maps/mapinfo.html file in the "sidebar" block.

Features
--------

- (Planned) Full metadata from GeoNode ResourceBase
- (Planned) Auto pdf document creation after using the print button in the map composer.

