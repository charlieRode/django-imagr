from django.forms import ModelForm
from imagr_app.models import Album
from imagr_app.models import Photo
from imagr_app.models import ImagrUser


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'photos', 'cover', 'published']


class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['photo_data', 'title', 'description', 'published']


class EditPhotoForm(ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'published']


class FollowForm(ModelForm):
    class Meta:
        model = ImagrUser
        fields = ['following']
