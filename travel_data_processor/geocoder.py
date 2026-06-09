import googlemaps

class Geocoder:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)

    def geocode_places(self, itinerary_data):
        """
        장소명 리스트를 받아 좌표(lat, lng)를 추가한 리스트를 반환합니다.
        """
        geocoded_itinerary = []
        for item in itinerary_data.get('itinerary', []):
            try:
                # 장소명을 기반으로 지오코딩 실행
                geocode_result = self.gmaps.geocode(item['place_name'])
                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    item['lat'] = location['lat']
                    item['lng'] = location['lng']
                    item['formatted_address'] = geocode_result[0]['formatted_address']
                else:
                    item['lat'], item['lng'], item['formatted_address'] = None, None, "Not Found"
                
                geocoded_itinerary.append(item)
            except Exception as e:
                item['error'] = str(e)
                geocoded_itinerary.append(item)
        
        return geocoded_itinerary
