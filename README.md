#django-imagr
============

This was produced by Charlie Rode, Ben Friedland, and Charles Gust


## Commands to set up the database ##

1. Enter PSQL with this command:
sudo -u postgres psql -U postgres postgres

2. From inside the PSQL, type in these commands:
postgres=# CREATE DATABASE imagr;

3. Create the user:
postgres=# CREATE role imagr login password 'imagr';

4. Set the owner to that user:
postgres=# ALTER database imagr OWNER to imagr;

5. Check your work:
postgres=# \l

6. Leave PSQL:
postgres=# \q

6. Migrate the database using Django's manage.py utility:
python manage.py migrate


Photo contains an image and meta-data associated with that image.

    Photos are owned by Users
    Meta-data includes a title and a description.
        A date_uploaded, date_modified and date_published field.
        They also have a 'published' field that takes one of three values
        ('private', 'shared', 'public')

Album contains Photos and provide meta-data about the collection of
    photos they contain.

    Albums are owned by Users
    Any album can contain many Photos and any Photo may be in
        more than one Album.
    Meta-data includes a title and a description.
        Also a date created, date modified and date published as well
        as a published field containing the same three options described for Photos
    Users are able to designate one contained photo as the 'cover' for
        the album.
    The albums created by a user may contain only Photos created by
        that same user.

ImagrUser is based off of the standard built-in Django User, with the
    following enhancements:

    Users are able to follow other users.
    Users are able to see a list of the users the follow and the
        list of users following them.
    Users have a 'date_joined' field and an 'active' field that allows
        disabling an account.




