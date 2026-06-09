from youtube_transcript_api import YouTubeTranscriptApi
import re

class DataExtractor:
    def get_youtube_transcript(self, video_url):
        """
        유튜브 URL에서 자막을 추출합니다.
        """
        try:
            video_id = self._extract_video_id(video_url)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text
        except Exception as e:
            return f"Error extracting transcript: {str(e)}"

    def _extract_video_id(self, url):
        """
        유튜브 URL에서 Video ID를 추출합니다.
        """
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            return video_id_match.group(1)
        return None
