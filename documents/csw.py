from owslib.csw import CatalogueServiceWeb,namespaces
import urllib, urllib2
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from owslib.util import http_post

addresses = {
	'geonetwork': {
		'csw': 'srv/en/csw',
		'login': 'srv/en/xml.user.login',
		'logout': 'srv/en/xml.user.logout', 
	}
}

class Catalog(CatalogueServiceWeb):
	def __init__(self, base, user, password,catalog_type='geonetwork',skip_caps=True):
		self.catalog = catalog_type
		self.base = base
		self.user = user
		self.password = password
		self._group_ids = {}
		self._operation_ids = {}
		self.connected = False
		url = '%s%s' % (self.base,addresses[self.catalog]['csw'])
		CatalogueServiceWeb.__init__(self, url=url, skip_caps=skip_caps)
		
	def login(self):
		if self.catalog == 'geonetwork':
			url = '%s%s' % (self.base,addresses[self.catalog]['login'])
			headers = {
				"Content-Type": "application/x-www-form-urlencoded",
				"Accept": "text/plain"
			}
			post = urllib.urlencode({
				"username": self.user,
				"password": self.password
			})
			request = urllib2.Request(url, post, headers)
			self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(),
					urllib2.HTTPRedirectHandler())
			response = self.opener.open(request)
			body = response.read()
			dom = minidom.parseString(body)
			assert dom.childNodes[0].nodeName == 'ok', "%s login failed!" % self.catalog
			self.connected = True

	def logout(self):
		if self.catalog == 'geonetwork':
			url = '%s%s' % (self.base,addresses[self.catalog]['logout'])
			request = urllib2.Request(url)
			response = self.opener.open(request)
			self.connected = False
		
	def csw_request(self, document, template):
		tpl = get_template(template)
		ctx = Context({
			'document': document,
			'SITEURL': settings.SITEURL[:-1],
		})
		md_doc = tpl.render(ctx)
		md_doc = md_doc.encode("utf-8")
		if self.catalog == 'geonetwork':
			headers = {
				"Content-Type": "application/xml; charset=UTF-8",
				"Accept": "text/plain"
			}
			request = urllib2.Request(self.url, md_doc, headers)
			response = self.urlopen(request)
		else:
			response = http_post(self.url, md_doc)
		return response

	def create_from_document(self, document):
		response = self.csw_request(document, "maps/csw/transaction_insert.xml")
		# TODO: Parse response, check for error report

		# Turn on the "view" permission (aka publish) for
		# the "all" group in GeoNetwork so that the layer
		# will be searchable via CSW without admin login.
		# all other privileges are set to False for all 
		# groups.
		self.set_metadata_privs(document.uuid, {"all":	 {"view": True}})
	
		return '%s?%s' % (self.url, urllib.urlencode({
			"request": "GetRecordById",
			"service": "CSW",
			"version": "2.0.2",
			"OutputSchema": "http://www.isotc211.org/2005/gmd",
			"ElementSetName": "full",
			"id": document.uuid
		}))

	def get_by_uuid(self, uuid):
		self.getrecordbyid([uuid], outputschema=namespaces["gmd"])
		if hasattr(self, 'records'):
			recs = self.records
			return recs.values()[0] if len(recs) > 0 else None
		else:
			return None

	def url_for_uuid(self, uuid):
		return "%s?%s" % (self.url, urllib.urlencode({
			"request": "GetRecordById",
			"service": "CSW",
			"version": "2.0.2",
			"id": uuid,
			"outputschema": namespaces["gmd"],
			"elementsetname": "full"
		}))

	def delete_layer(self, layer):
		response = self.csw_request(layer, "maps/csw/transaction_delete.xml")
		# TODO: Parse response, check for error report

	def update_layer(self, layer):
		response = self.csw_request(layer, "maps/csw/transaction_update.xml")
		# TODO: Parse response, check for error report

	def set_metadata_privs(self, uuid, privileges):
		"""
		set the full set of geonetwork privileges on the item with the 
		specified uuid based on the dictionary given of the form: 
		{
		  'group_name1': {'operation1': True, 'operation2': True, ...},
		  'group_name2': ...
		}

		all unspecified operations and operations for unspecified groups 
		are set to False.
		"""
		
		# XXX This is a fairly ugly workaround that makes 
		# requests similar to those made by the GeoNetwork
		# admin based on the recommendation here: 
		# http://bit.ly/ccVEU7

		if self.catalog == 'geonetwork':
			get_dbid_url = '%ssrv/en/portal.search.present?%s' % (self.base,urllib.urlencode({'uuid': uuid}))

			# get the id of the data.
			request = urllib2.Request(get_dbid_url)
			response = self.urlopen(request)
			doc = XML(response.read())
			data_dbid = doc.find('metadata/{http://www.fao.org/geonetwork}info/id').text

			# update group and operation info if needed
			if len(self._group_ids) == 0:
				self._group_ids = self._get_group_ids()
			if len(self._operation_ids) == 0:
				self._operation_ids = self._get_operation_ids()

			# build params that represent the privilege configuration
			priv_params = {
				"id": data_dbid, # "uuid": layer.uuid, # you can say this instead in newer versions of GN 
			}
			for group, privs in privileges.items():
				group_id = self._group_ids[group.lower()]
				for op, state in privs.items():
					if state != True:
						continue
					op_id = self._operation_ids[op.lower()]
					priv_params['_%s_%s' % (group_id, op_id)] = 'on'

			# update all privileges
			update_privs_url = "%ssrv/en/metadata.admin?%s" % (self.base,urllib.urlencode(priv_params))
			request = urllib2.Request(update_privs_url)
			response = self.urlopen(request)

			# TODO: check for error report	
		
	def _geonetwork_get_group_ids(self):
		"""
		helper to fetch the set of geonetwork 
		groups.
		"""
		# get the ids of the groups.
		get_groups_url = "%ssrv/en/xml.info?%s" % (self.base,urllib.urlencode({'type': 'groups'}))
		request = urllib2.Request(get_groups_url)
		response = self.urlopen(request)
		doc = XML(response.read())
		groups = {}
		for gp in doc.findall('groups/group'):
			groups[gp.find('name').text.lower()] = gp.attrib['id']
		return groups

	def _geonetwork_get_operation_ids(self):
		"""
		helper to fetch the set of geonetwork 
		'operations' (privileges)
		"""
		# get the ids of the operations	   
		get_ops_url =  "%ssrv/en/xml.info?%s" % (self.base, urllib.urlencode({'type': 'operations'}))
		request = urllib2.Request(get_ops_url)
		response = self.urlopen(request)
		doc = XML(response.read())
		ops = {}
		for op in doc.findall('operations/operation'):
			ops[op.find('name').text.lower()] = op.attrib['id']
		return ops

	def urlopen(self, request):
		if self.opener is None:
			raise Exception("No URL opener defined in geonetwork module!!")
		else:
			return self.opener.open(request)