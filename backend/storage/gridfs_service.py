import gridfs
from bson import ObjectId
from database.mongodb import db

class GridFSService:
    @staticmethod
    def get_fs():
        if db is not None:
            return gridfs.GridFS(db)
        return None

    @classmethod
    def save_file(cls, file_data: bytes, filename: str, content_type: str) -> ObjectId:
        fs = cls.get_fs()
        if fs is None:
            raise Exception("Database/GridFS offline")
        # GridFS put accepts content_type as an extra attribute or via contentType argument
        file_id = fs.put(file_data, filename=filename, contentType=content_type)
        return file_id

    @classmethod
    def read_file(cls, file_id: ObjectId) -> bytes:
        fs = cls.get_fs()
        if fs is None:
            raise Exception("Database/GridFS offline")
        grid_out = fs.get(file_id)
        return grid_out.read()

    @classmethod
    def get_grid_out(cls, file_id: ObjectId):
        fs = cls.get_fs()
        if fs is None:
            raise Exception("Database/GridFS offline")
        return fs.get(file_id)

    @classmethod
    def delete_file(cls, file_id: ObjectId):
        fs = cls.get_fs()
        if fs is None:
            return
        try:
            fs.delete(file_id)
        except Exception as e:
            print(f"Failed to delete GridFS file {file_id}: {e}")
