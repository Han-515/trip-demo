import openai
import json

class NLPProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def extract_places(self, text):
        """
        비정형 텍스트에서 여행 장소와 방문 순서를 추출하여 구조화된 JSON으로 반환합니다.
        """
        prompt = f"""
        다음 여행기 텍스트에서 방문한 장소들을 시간 순서대로 추출해 주세요.
        각 장소에 대해 이름과 간단한 설명(활동 내용)을 포함해야 합니다.
        결과는 반드시 다음 JSON 형식을 따라야 합니다:
        {{
            "itinerary": [
                {{ "order": 1, "place_name": "장소이름", "description": "설명" }},
                ...
            ]
        }}
        
        텍스트: {text[:4000]}  # API 제한을 고려한 텍스트 슬라이싱
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "너는 여행 일정 추출 전문가야."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
