import base64
import openai
import json

class VisionProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def _encode_image(self, image_path):
        """
        이미지 파일을 base64 문자열로 인코딩합니다.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_travel_image(self, image_path):
        """
        이미지(영상 프레임)에서 장소, 랜드마크, 텍스트(메뉴, 간판 등)를 분석합니다.
        """
        base64_image = self._encode_image(image_path)
        
        prompt = """
        이 이미지에서 여행 관련 정보를 추출해 주세요.
        1. 랜드마크나 장소 이름이 무엇인지?
        2. 간판이나 메뉴판에 적힌 텍스트가 무엇인지?
        3. 이 장소의 분위기나 특징은 어떤지?
        
        결과는 반드시 다음 JSON 형식을 따라야 합니다:
        {
            "detected_place": "장소 이름",
            "extracted_text": ["텍스트1", "텍스트2"],
            "features": "장소 설명/분위기"
        }
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            # JSON만 추출하기 위한 정규표현식이나 파싱 로직 추가 (필요 시)
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}

    def analyze_video_frames(self, image_paths):
        """
        여러 영상 프레임을 한 번에 분석하여 종합적인 여행 일정을 도출합니다.
        """
        # 여러 이미지를 분석하여 데이터의 신뢰도를 높이는 로직
        results = []
        for path in image_paths:
            analysis = self.analyze_travel_image(path)
            results.append(analysis)
        return results
