Cartography App for GeoNode
===========================

This is a GeoNode extension to handle documents in farious formats, even images. It works essentially by enabling files to be attached to GeoNode Map. The layers used to compose the map may or may not be registered in GeoNode.

Installation
------------

#. Install the documents app:

    source bin/activate

    pip install -e git+git://github.com/simod/geonode-documents.git#egg=documents

#. Edit your settings.py file and add ``documents`` to the list of installed apps

#. Edit your settings.py file and modify the TEMPLATE_DIRS entry as follows:

	TEMPLATE_DIRS = (
		os.path.join(PROJECT_ROOT,'..','..','documents','documents',"templates"),
		
		os.path.join(PROJECT_ROOT,"templates"),
	)

#. Append the following line to your urls.py::

     (r'^documents/', include('documents.urls')),

# Then re-run ``syncdb`` and reload your web server.

Features
--------

- (Planned) Upload form for document. It can either be attached to an existing map or a new one can be created with a custom widget to select the bounding box.
- (Planned) Integration with GeoNetwork (maps and files registered in GeoNetwork)
- (Planned) Easy installable on an existing GeoNode installation. Without having to alter existing tables / data.
- (Planned) Auto pdf document creation after using the print button in the map composer.

