from django.conf.urls.defaults import patterns, url
from documents.models import Document
from documents.views import documentdetail,newmaptpl,upload_document

info_dict = {
	'queryset': Document.objects.all(),
	}

urlpatterns = patterns('',
	(r'^(?P<docid>\d+)$', documentdetail),
    (r'^upload/(?P<mapid>\d+)/?$', upload_document),
	url(r'^upload/?$', 'documents.views.upload_document', name='document-upload'),
	(r'^newmap$', newmaptpl),
	url(r'^search/?$', 'documents.views.documents_search_page', name='documents_search'),
    url(r'^search/api/?$', 'documents.views.documents_search', name='documents_search_api'),
    url(r'^(?P<docid>\d+)/ajax-permissions$', 'documents.views.ajax_document_permissions', name='ajax_document_permissions'),
)