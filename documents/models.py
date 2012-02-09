from django.db import models
from geonode.maps.models import Map, Resource
from django.db.models import signals
import os
from django.contrib.auth.models import User
from geonode.core.models import AUTHENTICATED_USERS, ANONYMOUS_USERS

class Document(Resource):
	"""

	A document is any kind of information that can be attached to a map such as pdf, images, videos, xls...

	"""

	maps = models.ManyToManyField(Map)
	file = models.FileField(upload_to='documents')
	mimetype = models.CharField(max_length=128,blank=True,null=True)

	def __unicode__(self):
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return self.file.url
		
	class Meta:
		# custom permissions,
		# change and delete are standard in django
		permissions = (
			('view_document', 'Can view'), 
			('change_document_permissions', "Can change permissions"),
		)

	LEVEL_READ	= 'document_readonly'
	LEVEL_WRITE = 'document_readwrite'
	LEVEL_ADMIN = 'document_admin'

def pre_save_document(instance, sender, **kwargs):
	base_name, extension = os.path.splitext(instance.file.name)
	instance.type=extension[1:]

signals.pre_save.connect(pre_save_document, sender=Document)