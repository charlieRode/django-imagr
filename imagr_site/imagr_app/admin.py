from django.contrib import admin
from imagr_app.models import ImagrUser
from imagr_app.models import Album
from imagr_app.models import Photo

admin.site.register(ImagrUser)
admin.site.register(Album)
admin.site.register(Photo)
