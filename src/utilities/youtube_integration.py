"""
YouTube Integration - Integration with YouTube API for documentation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta


class YouTubeIntegration:
    """
    Integration with YouTube API for documenting development.
    """
    
    def __init__(self, channel_id: str = "@keepcontinuity", credentials_file: Optional[str] = None):
        """
        Initialize the YouTube integration.
        
        Args:
            channel_id: YouTube channel ID
            credentials_file: Path to credentials file
        """
        self.channel_id = channel_id
        self.credentials_file = credentials_file
        self.logger = logging.getLogger("continuity.youtube_integration")
        self.youtube = None
    
    def authenticate(self, client_secrets_file: Optional[str] = None) -> bool:
        """
        Authenticate with the YouTube API.
        
        Args:
            client_secrets_file: Path to client secrets file
            
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            # Use provided file or default
            client_secrets_file = client_secrets_file or self.credentials_file
            
            if not client_secrets_file or not os.path.exists(client_secrets_file):
                self.logger.error("Client secrets file not found")
                return False
            
            try:
                import google.oauth2.credentials
                import google_auth_oauthlib.flow
                import googleapiclient.discovery
                import googleapiclient.errors
            except ImportError:
                self.logger.error("Google API client libraries not installed")
                self.logger.info("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
                return False
            
            # Set up the OAuth flow
            scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_local_server(port=8080)
            
            # Build the YouTube API client
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=credentials)
            
            self.logger.info(f"Authenticated with YouTube API for channel {self.channel_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error authenticating with YouTube API: {e}")
            return False
    
    def create_development_playlist(self, title: str, description: str) -> Optional[str]:
        """
        Create a playlist for documenting development.
        
        Args:
            title: Playlist title
            description: Playlist description
            
        Returns:
            Playlist ID if successful, None otherwise
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return None
        
        try:
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "defaultLanguage": "pt-BR"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            )
            response = request.execute()
            
            playlist_id = response["id"]
            self.logger.info(f"Created playlist: {title} (ID: {playlist_id})")
            
            return playlist_id
        
        except Exception as e:
            self.logger.error(f"Error creating playlist: {e}")
            return None
    
    def schedule_development_stream(self, title: str, description: str, 
                                   start_time: Optional[datetime] = None,
                                   duration_minutes: int = 60) -> Optional[str]:
        """
        Schedule a live stream for documenting development.
        
        Args:
            title: Stream title
            description: Stream description
            start_time: Start time (default: 1 hour from now)
            duration_minutes: Duration in minutes
            
        Returns:
            Broadcast ID if successful, None otherwise
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return None
        
        try:
            # Default start time is 1 hour from now
            if not start_time:
                start_time = datetime.now() + timedelta(hours=1)
            
            # Calculate end time
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Format times for API
            start_time_str = start_time.isoformat() + "Z"
            end_time_str = end_time.isoformat() + "Z"
            
            request = self.youtube.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "scheduledStartTime": start_time_str,
                        "scheduledEndTime": end_time_str
                    },
                    "status": {
                        "privacyStatus": "public"
                    },
                    "contentDetails": {
                        "enableAutoStart": True,
                        "enableAutoStop": True
                    }
                }
            )
            response = request.execute()
            
            broadcast_id = response["id"]
            self.logger.info(f"Scheduled stream: {title} (ID: {broadcast_id})")
            
            return broadcast_id
        
        except Exception as e:
            self.logger.error(f"Error scheduling stream: {e}")
            return None
    
    def create_development_update(self, title: str, description: str, 
                                 tags: List[str] = None,
                                 video_file: Optional[str] = None) -> Optional[str]:
        """
        Create a development update video.
        
        Args:
            title: Video title
            description: Video description
            tags: Video tags
            video_file: Path to video file
            
        Returns:
            Video ID if successful, None otherwise
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return None
        
        if not video_file or not os.path.exists(video_file):
            self.logger.error(f"Video file not found: {video_file}")
            return None
        
        try:
            import googleapiclient.http
            
            # Set up the video metadata
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or ["continuity-protocol", "development", "update"],
                    "categoryId": "28"  # Science & Technology category
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            
            # Create the video insert request
            media = googleapiclient.http.MediaFileUpload(
                video_file,
                mimetype="video/*",
                resumable=True
            )
            
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            # Upload the video
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    self.logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response["id"]
            self.logger.info(f"Video uploaded: {title} (ID: {video_id})")
            
            return video_id
        
        except Exception as e:
            self.logger.error(f"Error uploading video: {e}")
            return None
    
    def add_video_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """
        Add a video to a playlist.
        
        Args:
            video_id: Video ID
            playlist_id: Playlist ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return False
        
        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            response = request.execute()
            
            self.logger.info(f"Added video {video_id} to playlist {playlist_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error adding video to playlist: {e}")
            return False
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the channel.
        
        Returns:
            Channel information if successful, None otherwise
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return None
        
        try:
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=self.channel_id
            )
            response = request.execute()
            
            if "items" in response and response["items"]:
                return response["items"][0]
            else:
                self.logger.error(f"Channel not found: {self.channel_id}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error getting channel info: {e}")
            return None
