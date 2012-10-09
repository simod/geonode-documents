from django.conf.urls.defaults import patterns, url
from django.views.i18n import javascript_catalog

urlpatterns = patterns('documents.views',
	(r'^$','documents'),
	(r'^(?P<docid>\d+)$', 'documentdetail'),
	url(r'^new/?$', 'upload_document', name='document-upload'),
	(r'^newmap$', 'newmaptpl'),
	url(r'^search/?$', 'documents_search_page', name='documents_search'),
    url(r'^search/api/?$', 'documents_search', name='documents_search_api'),
    url(r'^(?P<docid>\d+)/ajax-permissions$', 'ajax_document_permissions', name='ajax_document_permissions'),
    url(r'^resources/search/api/?$', 'resources_search', name='resources_search'),
)