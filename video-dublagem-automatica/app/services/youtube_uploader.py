import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import file as oauth_file
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.urllib3 import Request as UrllibRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import pickle

logger = logging.getLogger(__name__)

from app.config.settings import CREDENTIALS_DIR, YOUTUBE_CREDENTIALS_FILE


class YouTubeError(Exception):
    """Raised when YouTube operations fail"""
    pass


class YouTubeUploader:
    """Handles video upload to YouTube using official API"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize YouTube uploader with credentials
        
        Args:
            credentials_file: Path to OAuth2 credentials file
        """
        self.credentials_file = credentials_file or YOUTUBE_CREDENTIALS_FILE
        self.youtube = None
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with YouTube API
        
        Raises:
            YouTubeError: If authentication fails
        """
        try:
            logger.info("Authenticating with YouTube API")
            
            # Check for existing token
            token_file = Path(CREDENTIALS_DIR) / "token.pickle"
            credentials = None
            
            if token_file.exists():
                with open(token_file, 'rb') as token:
                    credentials = pickle.load(token)
                    logger.debug("Loaded credentials from token file")
            
            # If no valid credentials, authenticate
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    logger.info("Refreshing credentials")
                    credentials.refresh(UrllibRequest())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise YouTubeError(
                            f"Credentials file not found: {self.credentials_file}\n"
                            "Please download OAuth2 credentials from Google Cloud Console"
                        )
                    
                    logger.info(f"Starting OAuth2 flow with {self.credentials_file}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        self.SCOPES
                    )
                    credentials = flow.run_local_server(port=8080)
                
                # Save credentials for future use
                with open(token_file, 'wb') as token:
                    pickle.dump(credentials, token)
                    logger.debug("Saved credentials to token file")
            
            # Build YouTube API client
            self.youtube = build(
                self.API_SERVICE_NAME,
                self.API_VERSION,
                credentials=credentials
            )
            
            logger.info("Successfully authenticated with YouTube API")
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise YouTubeError(f"Failed to authenticate with YouTube: {str(e)}")

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category_id: str = "22",  # 22 = People & Blogs
        privacy_status: str = "public",
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file to upload
            title: Video title
            description: Video description
            tags: List of tags/keywords
            category_id: YouTube category ID
            privacy_status: 'public', 'private', or 'unlisted'
            thumbnail_path: Optional path to custom thumbnail
            
        Returns:
            Dictionary with upload info including video ID and URL
        """
        try:
            if not self.youtube:
                raise YouTubeError("Not authenticated with YouTube API")
            
            if not os.path.exists(video_path):
                raise YouTubeError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            logger.info(f"Uploading video: {title} ({file_size / (1024**3):.2f} GB)")
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id,
                    'defaultLanguage': 'pt-BR',
                    'defaultAudioLanguage': 'pt'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False,
                    'embeddable': True,
                    'publicStatsViewable': True
                },
                'processingDetails': {
                    'processStatus': 'unspecified'
                }
            }
            
            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                chunksize=10 * 1024 * 1024,  # 10MB chunks
                resumable=True,
                mimetype='video/mp4'
            )
            
            logger.info("Starting resumable upload")
            
            # Execute upload with progress tracking
            request = self.youtube.videos().insert(
                part='snippet,status,processingDetails',
                body=body,
                media_body=media,
                notifySubscribers=False,
                onBehalfOfContentOwner=None,
                onBehalfOfContentOwnerChannel=None,
                stabilize=False
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    percent_complete = 100.0 * status.progress()
                    logger.info(f"Upload progress: {percent_complete:.1f}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            
            # Upload thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    self._set_video_thumbnail(video_id, thumbnail_path)
                except Exception as e:
                    logger.warning(f"Failed to upload thumbnail: {str(e)}")
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'privacy_status': privacy_status,
                'file_size': file_size
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise YouTubeError(f"YouTube API error: {str(e)}")
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise YouTubeError(f"Failed to upload video: {str(e)}")

    def _set_video_thumbnail(self, video_id: str, thumbnail_path: str) -> None:
        """
        Set video thumbnail
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
        """
        try:
            logger.info(f"Setting thumbnail for video {video_id}")
            
            media = MediaFileUpload(
                thumbnail_path,
                mimetype='image/jpeg',
                resumable=False
            )
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            
            response = request.execute()
            logger.info("Thumbnail set successfully")
            
        except Exception as e:
            logger.error(f"Error setting thumbnail: {str(e)}")
            raise

    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get authenticated user's channel information
        
        Returns:
            Dictionary with channel information
        """
        try:
            if not self.youtube:
                raise YouTubeError("Not authenticated with YouTube API")
            
            logger.info("Retrieving channel information")
            
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            )
            
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                channel_info = {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscribers': channel['statistics'].get('subscriberCount', 'hidden'),
                    'view_count': channel['statistics'].get('viewCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0)
                }
                
                logger.info(f"Channel info retrieved: {channel_info['title']}")
                return channel_info
            else:
                raise YouTubeError("No channel found")
                
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise YouTubeError(f"Failed to get channel info: {str(e)}")

    def update_video_metadata(
        self,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        privacy_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update video metadata after upload
        
        Args:
            video_id: YouTube video ID
            title: New title
            description: New description
            tags: New tags
            privacy_status: New privacy status
            
        Returns:
            Dictionary with updated metadata
        """
        try:
            if not self.youtube:
                raise YouTubeError("Not authenticated with YouTube API")
            
            logger.info(f"Updating metadata for video {video_id}")
            
            # Get current video metadata
            request = self.youtube.videos().list(
                part='snippet,status',
                id=video_id
            )
            
            response = request.execute()
            
            if not response['items']:
                raise YouTubeError(f"Video not found: {video_id}")
            
            video = response['items'][0]
            
            # Update fields
            if title:
                video['snippet']['title'] = title
            if description:
                video['snippet']['description'] = description
            if tags:
                video['snippet']['tags'] = tags
            if privacy_status:
                video['status']['privacyStatus'] = privacy_status
            
            # Upload updated metadata
            update_request = self.youtube.videos().update(
                part='snippet,status',
                body=video
            )
            
            update_response = update_request.execute()
            
            logger.info(f"Video metadata updated successfully")
            
            return {
                'video_id': video_id,
                'title': update_response['snippet']['title'],
                'description': update_response['snippet']['description'],
                'privacy_status': update_response['status']['privacyStatus']
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise YouTubeError(f"Failed to update metadata: {str(e)}")
