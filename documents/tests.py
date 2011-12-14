"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

"""
from django.test import TestCase
from django.conf import settings
from geonode.maps.models import Map, MapLayer
from documents.models import Document
from django.test.client import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
import StringIO

LOGIN_URL = settings.SITEURL + "accounts/login/"

superuser = User.objects.create_superuser('bobby', 'bobby@foo.com', 'bob')
imgfile = StringIO.StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
	                            '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
def create_document():
	f = SimpleUploadedFile('test_img_file.gif', imgfile.read(), 'image/gif')
	m, __ = Map.objects.get_or_create(id=1, title='foo', projection='4326', zoom=2, center_x=0, center_y=0,
	                                  owner=User.objects.get_or_create(username='foo')[0])
	for ord, lyr in enumerate(settings.MAP_BASELAYERS):
		MapLayer.objects.from_viewer_config(
			map=m,
			layer=lyr,
			source=settings.MAP_BASELAYERSOURCES[lyr["source"]],
			ordering=ord
		).save()
	m.set_default_permissions()
	c, created = Document.objects.get_or_create(id=1, file=f,owner=superuser)
	c.maps.add(m)
	return c, created

class EventsTest(TestCase):

	def test_map_details(self):
		"""/maps/1 -> Test accessing the detail view of a map"""
		create_documents()
		map = Map.objects.get(id=1)
		c = Client()
		response = c.get("/maps/%s" % str(map.id))
		self.assertEquals(response.status_code, 200)

	def test_document_details(self):
		"""/documents/1 -> Test accessing the detail view of a document"""
		create_document()
		document = Document.objects.get(id=1)
		c = Client()
		response = c.get("/documents/%s" % str(document.id))
		self.assertEquals(response.status_code, 200)

	def test_access_document_upload_form(self):
		"""Test the form page is returned correctly via GET request /documents/upload"""
		c = Client()
		log = c.login(username='bobby', password='bob')
		self.assertTrue(log)
		response = c.get("/document/upload")
		self.assertTrue('Add document' in response.content)

	def test_document_isuploaded(self):
		"""/documents/upload -> Test uploading a document"""
		f = SimpleUploadedFile('test_img_file.gif', imgfile.read(), 'image/gif')
		m, __ = Map.objects.get_or_create(id=1, title='foo', projection='4326', zoom=2, center_x=0, center_y=0,
		                                  owner=User.objects.get_or_create(username='foo')[0])
		c = Client()
		
		c.login(username='bobby', password='bob')
		response = c.post("/documents/upload", {'file': f, 'title': 'uploaded_document', 'map': m.id},
		                  follow=True)
		self.assertEquals(response.status_code, 200)

	def test_newmap_template(self):
		"""
		Test if the newmap template is returned correctly
		"""
		c = Client()
		response = c.get('/documents/newmap')
		self.assertEquals(response.status_code, 200)

	def test_document_creation(self):
		"""
		Test if a document is created properly
		"""
		f = SimpleUploadedFile('test_img_file.gif', imgfile.read(), 'image/gif')
		m, __ = Map.objects.get_or_create(id=1, title='foo', projection='4326', zoom=2, center_x=0, center_y=0,
	                                  owner=User.objects.get_or_create(username='foo')[0])
		m.set_default_permissions()
		d,created = Document.objects.get_or_create(id=1, file=f)
		d.maps.add(m)
		self.assertTrue(created)