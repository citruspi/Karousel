import os
import datetime
from flask import abort, request, g
from werkzeug import secure_filename
from . import config, PhotoModel, AlbumModel, AuthenticatedResource

class PhotosResource (AuthenticatedResource):

    def post (self):

        album = request.form.get('album')
        file = request.files.get('file')

        if not album or not file:

            abort(400)

        if AlbumModel.select().where(AlbumModel.id == album).count() != 1:

            abort(404)

        album = AlbumModel.get(AlbumModel.id == album)

        filename = secure_filename(file.filename)

        photo = PhotoModel.create(
            name = filename,
            size = 0,
            album = album,
            user = g.user
        )

        path = os.path.join(config.get('Photos', 'ProcessingDirectory'), str(photo.id))
        file.save(path)

        photo.size = os.stat(path).st_size
        photo.save()

        return {'id': photo.id, 'name': photo.name, 'date': photo.uploaded.strftime("%Y-%m-%d %H:%M:%S"), 'size': photo.size}
