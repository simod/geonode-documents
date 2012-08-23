import json
import unicodedata

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.models import User

from geonode.maps.models import Map
from geonode.people.models import Contact
from geonode.security.views import _perms_info
from geonode.security.models import AUTHENTICATED_USERS, ANONYMOUS_USERS

from documents.models import Document

imgtypes = ['jpg','jpeg','tif','tiff','png','gif']

DOCUMENT_LEV_NAMES = {
	Document.LEVEL_NONE	 : _('No Permissions'),
	Document.LEVEL_READ	 : _('Read Only'),
	Document.LEVEL_WRITE : _('Read/Write'),
	Document.LEVEL_ADMIN : _('Administrative')
}

def documents(request):
    if request.method == 'GET':
        return render_to_response('documents/documents.html', RequestContext(request))

def documentdetail(request, docid):
	"""
	The view that show details of each document
	"""
	document = get_object_or_404(Document, pk=docid)
	if not request.user.has_perm('documents.view_document', obj=document):
		return HttpResponse(loader.render_to_string('401.html',
			RequestContext(request, {'error_message':
				_("You are not allowed to view this document.")})), status=401)

	return render_to_response("documents/docinfo.html", RequestContext(request, {
		'permissions_json': json.dumps(_perms_info(document, DOCUMENT_LEV_NAMES)),
		'document': document,
		'imgtypes': imgtypes
	}))

def newmaptpl(request):
	config = default_map_config()[0]
	return render_to_response('documents/newmaptpl.html',RequestContext(request, {'config':json.dumps(config)}))

@login_required
def upload_document(request,mapid=None):
	if request.method == 'GET':
		return render_to_response('documents/document_upload.html',
								  RequestContext(request,{'mapid':mapid,}),
								  context_instance=RequestContext(request)
		)

	elif request.method == 'POST':
		mapid = str(request.POST['map'])
		file = request.FILES['file']
		title = request.POST['title']
		document = Document(title=title, file=file)
		if request.user.is_authenticated(): document.owner = request.user
		document.save()
		document.maps.add(Map.objects.get(id=mapid))
		return HttpResponse(json.dumps({'success': True,'redirect_to':'/maps/' + str(mapid)}))
		
#### DOCUMENTS SEARCHING ####

DEFAULT_MAPS_SEARCH_BATCH_SIZE = 10
MAX_MAPS_SEARCH_BATCH_SIZE = 25
@csrf_exempt
def documents_search(request):
	"""
	for ajax requests, the search returns a json structure 
	like this: 
	
	{
	'total': <total result count>,
	'next': <url for next batch if exists>,
	'prev': <url for previous batch if exists>,
	'query_info': {
		'start': <integer indicating where this batch starts>,
		'limit': <integer indicating the batch size used>,
		'q': <keywords used to query>,
	},
	'rows': [
	  {
		'title': <map title,
		'abstract': '...',
		'detail' : <url geonode detail page>,
		'owner': <name of the map's owner>,
		'owner_detail': <url of owner's profile page>,
		'last_modified': <date and time of last modification>
	  },
	  ...
	]}
	"""
	if request.method == 'GET':
		params = request.GET
	elif request.method == 'POST':
		params = request.POST
	else:
		return HttpResponse(status=405)

	# grab params directly to implement defaults as
	# opposed to panicy django forms behavior.
	query = params.get('q', '')
	try:
		start = int(params.get('start', '0'))
	except:
		start = 0
	try:
		limit = min(int(params.get('limit', DEFAULT_MAPS_SEARCH_BATCH_SIZE)),
					MAX_MAPS_SEARCH_BATCH_SIZE)
	except: 
		limit = DEFAULT_MAPS_SEARCH_BATCH_SIZE


	sort_field = params.get('sort', u'')
	sort_field = unicodedata.normalize('NFKD', sort_field).encode('ascii','ignore')	 
	sort_dir = params.get('dir', 'ASC')
	result = _documents_search(query, start, limit, sort_field, sort_dir)

	result['success'] = True
	return HttpResponse(json.dumps(result), mimetype="application/json")

def _documents_search(query, start, limit, sort_field, sort_dir):

	keywords = _split_query(query)

	documents = Document.objects
	for keyword in keywords:
		documents = documents.filter(
			  Q(title__icontains=keyword)
			| Q(type__icontains=keyword))

	if sort_field:
		order_by = ("" if sort_dir == "ASC" else "-") + sort_field
		documents = documents.order_by(order_by)

	documents_list = []

	for document in documents.all()[start:start+limit]:
		try:
			owner_name = Contact.objects.get(user=document.owner).name
		except:
			owner_name = document.owner.first_name + " " + document.owner.last_name

		mapdict = {
			'id' : document.id,
			'title' : document.title,
			'detail' : reverse('documents.views.documentdetail', args=(document.id,)),
			'owner' : owner_name,
			'owner_detail' : reverse('profile_detail', args=(document.owner.username,)),
			'maps': [(map.id,map.title) for map in document.maps.all()],
			'type': document.type
			}
		documents_list.append(mapdict)

	result = {'rows': documents_list,'total': documents.count()}

	result['query_info'] = {
		'start': start,
		'limit': limit,
		'q': query
	}
	if start > 0: 
		prev = max(start - limit, 0)
		params = urlencode({'q': query, 'start': prev, 'limit': limit})
		result['prev'] = reverse('documents.views.documents_search') + '?' + params

	next = start + limit + 1
	if next < documents.count():
		 params = urlencode({'q': query, 'start': next - 1, 'limit': limit})
		 result['next'] = reverse('documents.views.documents_search') + '?' + params
	
	return result

@csrf_exempt	
def documents_search_page(request):
	# for non-ajax requests, render a generic search page

	if request.method == 'GET':
		params = request.GET
	elif request.method == 'POST':
		params = request.POST
	else:
		return HttpResponse(status=405)

	return render_to_response('documents/document_search.html', RequestContext(request, {
		'init_search': json.dumps(params or {}),
		 "site" : settings.SITEURL
	}))

def _split_query(query):
	"""
	split and strip keywords, preserve space 
	separated quoted blocks.
	"""

	qq = query.split(' ')
	keywords = []
	accum = None
	for kw in qq: 
		if accum is None: 
			if kw.startswith('"'):
				accum = kw[1:]
			elif kw: 
				keywords.append(kw)
		else:
			accum += ' ' + kw
			if kw.endswith('"'):
				keywords.append(accum[0:-1])
				accum = None
	if accum is not None:
		keywords.append(accum)
	return [kw.strip() for kw in keywords if kw.strip()]

def ajax_document_permissions(request, docid):
	document = get_object_or_404(Document, pk=docid)

	if not request.method == 'POST':
		return HttpResponse(
			'You must use POST for editing document permissions',
			status=405,
			mimetype='text/plain'
		)

	if not request.user.has_perm("documents.change_document_permissions", obj=document):
		return HttpResponse(
			'You are not allowed to change permissions for this document',
			status=401,
			mimetype='text/plain'
		)

	spec = json.loads(request.raw_post_data)
	set_document_permissions(document, spec)

	return HttpResponse(
		"Permissions updated",
		status=200,
		mimetype='text/plain'
	)

def set_document_permissions(m, perm_spec):
	if "authenticated" in perm_spec:
		m.set_gen_level(AUTHENTICATED_USERS, perm_spec['authenticated'])
	if "anonymous" in perm_spec:
		m.set_gen_level(ANONYMOUS_USERS, perm_spec['anonymous'])
	users = [n for (n, p) in perm_spec['users']]
	m.get_user_levels().exclude(user__username__in = users + [m.owner]).delete()
	for username, level in perm_spec['users']:
		user = User.objects.get(username=username)
		m.set_user_level(user, level)
