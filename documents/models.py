import os

from django.db import models
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from geonode.core.models import PermissionLevelMixin
from geonode.core.models import AUTHENTICATED_USERS, ANONYMOUS_USERS


class Document(models.Model,PermissionLevelMixin):
	"""

	A document is any kind of information that can be attached to a map such as pdf, images, videos, xls...

	"""

	# Relation to the resource model
	content_type = models.ForeignKey(ContentType,blank=True,null=True)
	object_id = models.PositiveIntegerField(blank=True,null=True)

	title = models.CharField(max_length=255)
	file = models.FileField(upload_to='documents')
	type = models.CharField(max_length=128,blank=True,null=True)
	owner = models.ForeignKey(User, verbose_name='owner', blank=True, null=True)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return '/documents/%s' % self.id
		
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
	
	def set_default_permissions(self):
		self.set_gen_level(ANONYMOUS_USERS, self.LEVEL_READ)
		self.set_gen_level(AUTHENTICATED_USERS, self.LEVEL_READ)
		
		# remove specific user permissions
		current_perms =	 self.get_all_level_info()
		for username in current_perms['users'].keys():
			user = User.objects.get(username=username)
			self.set_user_level(user, self.LEVEL_NONE)
		
		# assign owner admin privs
		if self.owner:
			self.set_user_level(self.owner, self.LEVEL_ADMIN) 

def pre_save_document(instance, sender, **kwargs):
	base_name, extension = os.path.splitext(instance.file.name)
	instance.type=extension[1:]

signals.pre_save.connect(pre_save_document, sender=Document)