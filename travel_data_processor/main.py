import json
from data_extractor import DataExtractor
from nlp_processor import NLPProcessor
from geocoder import Geocoder
from vision_processor import VisionProcessor

def convert_to_geojson(geocoded_itinerary):
    """
    추출된 장소 데이터를 지도 표시용 GeoJSON으로 변환합니다.
    """
    features = []
    for point in geocoded_itinerary:
        if point.get('lat') and point.get('lng'):
            feature = {
                "type": "Feature",
                "properties": {
                    "order": point['order'],
                    "place_name": point['place_name'],
                    "description": point['description'],
                    "address": point['formatted_address']
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [point['lng'], point['lat']]
                }
            }
            features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def main():
    # 1. API Keys (사용자 입력 필요)
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
    
    # 2. 분석 대상 유튜브 URL
    target_url = "https://www.youtube.com/watch?v=EXAMPLE_VIDEO_ID"
    
    # 3. 데이터 추출
    extractor = DataExtractor()
    transcript = extractor.get_youtube_transcript(target_url)
    print(f"Transcript Extracted (Length: {len(transcript)})")
    
    # 4. NLP 기반 장소 추출
    nlp = NLPProcessor(OPENAI_API_KEY)
    raw_itinerary = nlp.extract_places(transcript)
    print("NLP Extraction Completed")
    
    # 5. Vision AI 기반 보조 데이터 추출 (영상 프레임이 있는 경우)
    vision = VisionProcessor(OPENAI_API_KEY)
    # 예시: 영상에서 추출한 랜드마크 이미지 경로
    landmark_images = ["frame1.jpg", "frame2.jpg"]
    # vision_results = vision.analyze_video_frames(landmark_images)
    # print("Vision Analysis Completed")
    
    # 6. Geocoding
    geocoder = Geocoder(GOOGLE_MAPS_API_KEY)
    geocoded_data = geocoder.geocode_places(raw_itinerary)
    print("Geocoding Completed")
    
    # 6. GeoJSON 변환 및 저장
    geojson_data = convert_to_geojson(geocoded_data)
    with open('travel_route.geojson', 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_content_is_ascii=False, indent=2)
    
    print("Success: travel_route.geojson saved.")

if __name__ == "__main__":
    main()
