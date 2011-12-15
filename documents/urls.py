from django.conf.urls.defaults import patterns, url
from documents.models import Document

info_dict = {
	'queryset': Document.objects.all(),
	}

urlpatterns = patterns('documents.views',
	(r'^$','documents'),
	(r'^(?P<docid>\d+)$', 'documentdetail'),
    (r'^upload/(?P<mapid>\d+)/?$', 'upload_document'),
	url(r'^upload/?$', 'upload_document', name='document-upload'),
	(r'^newmap$', 'newmaptpl'),
	url(r'^search/?$', 'documents_search_page', name='documents_search'),
    url(r'^search/api/?$', 'documents_search', name='documents_search_api'),
    url(r'^(?P<docid>\d+)/ajax-permissions$', 'ajax_document_permissions', name='ajax_document_permissions'),
)