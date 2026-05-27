from bson import ObjectId
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status
from storage.gridfs_service import GridFSService
from storage.file_metadata import FileMetadataService

class DownloadService:
    @staticmethod
    def download_resume(resume_id: str, user_email: str) -> StreamingResponse:
        # 1. Fetch metadata & check ownership
        metadata = FileMetadataService.get_metadata(resume_id, user_email)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied."
            )

        gridfs_file_id = metadata.get("gridfs_file_id")
        if not gridfs_file_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File content not found in database."
            )

        # 2. Retrieve GridFS file stream
        try:
            grid_out = GridFSService.get_grid_out(ObjectId(gridfs_file_id))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve file from DB: {str(e)}"
            )

        # 3. Stream Response
        filename = metadata.get("filename", "resume.pdf")
        media_type = metadata.get("file_type") or "application/pdf"
        
        # Set Content-Disposition to attachment to trigger browser download
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        return StreamingResponse(
            grid_out,
            media_type=media_type,
            headers=headers
        )
