Documents App for GeoNode
===========================

This is a GeoNode extension to handle documents in various formats, even images. It works essentially by enabling files to be attached to a GeoNode Map, Layer or be indipendent.

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

	(basic) replace the page_layout.html file provided in the "extras" folder with the original one in your template folder. (only use this if you have never modified the page_layout.html file)
	
	(advanced) copy the content of the page_layout_snippet.html and insert it in your page_layout.html file in the "nav" block.

#. In order to have the documents linked in the map or layer detail template:
	
	copy the content of the extra/maps/info_snippet.html and insert it in your mapinfo.html or layer.html file in the "header" and "sidebar" block.


