from django.conf.urls import patterns, url

from imagr_app import views


urlpatterns = patterns('',
    url(r'^$', views.front_page, name='front_page'),

    # Alternate root page here, perhaps?
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'imagr_app/login.html'}),
    url(r'^album/(?P<album_id>\d+)$', views.album_page, name='album_page'),
    url(r'^photo/(?P<photo_id>\d+)$', views.photo_page, name='photo_page'),
    url(r'^stream$', views.stream, name='stream'),
    url(r'^submit_photo$', views.upload_photo, name='submit_photo'),
    url(r'^create_album$', views.create_album, name='create_album'),
    url(r'^edit_album/(?P<album_id>\d+)$', views.edit_album, name='edit_album'),
    url(r'^edit_photo/(?P<photo_id>\d+)$', views.edit_photo, name='edit_photo'),
    url(r'^followers$', views.follow_page, name='followers'),
)

