from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TRI:P AI Engine Prototype")

# --- Schemas ---

class OnboardingRequest(BaseModel):
    user_id: str
    travel_style: str  # Activity, Relax, Foodie, Shopping, Culture
    companion_type: str # Solo, Couple, Family, Group
    budget_range: str  # Economy, Standard, Luxury
    duration: int      # Days
    region: str        # City or Region name

class Place(BaseModel):
    place_id: str
    name: str
    category: str
    estimated_cost: float
    visit_time: str
    travel_time_from_prev: Optional[int] = 0 # Minutes
    description: str

class DayPlan(BaseModel):
    day: int
    places: List[Place]

class ItineraryResponse(BaseModel):
    itinerary_id: str
    user_id: str
    days: List[DayPlan]
    total_cost: float
    budget_limit: float
    budget_exceeded: bool
    alternatives: Optional[List[Dict]] = []

class ItineraryUpdateRequest(BaseModel):
    action: str  # reorder, add, remove
    day: int
    place_id: str
    target_index: Optional[int] = None
    new_place_data: Optional[Dict] = None

# --- Mock Database / Cache ---
in_memory_profiles = {}
in_memory_itineraries = {} # Store generated itineraries
in_memory_shares = {}      # Store shared itinerary access

# --- AI Core Logic ---

def calculate_travel_time(p1_id: str, p2_id: str):
    """
    Google Maps Distance Matrix API 시뮬레이션
    """
    # 실제 구현 시 거리 기반 계산 로직 추가
    return 30 # 기본 30분 가정

def get_budget_limit(budget_range: str, duration: int):
    """
    예산대에 따른 총 한도 설정 (Simulated)
    """
    limits = {
        "Economy": 50000,
        "Standard": 150000,
        "Luxury": 500000
    }
    return limits.get(budget_range, 150000) * duration

def suggest_alternatives(category: str, current_cost: float):
    """
    예산 초과 시 더 저렴한 대안 추천 (Simulated)
    """
    # 실제로는 DB에서 해당 카테고리의 저렴한 POI를 검색
    return [
        {"name": "길거리 토스트", "estimated_cost": 5000, "desc": "가성비 좋은 식사 대안"},
        {"name": "공립 박물관", "estimated_cost": 0, "desc": "무료로 즐길 수 있는 문화 공간"}
    ]

def get_tour_api_data(region: str, style: str):
    """
    한국관광공사 TourAPI 4.0을 시뮬레이션하여 지역 기반 관광지 데이터를 가져옴
    """
    # 실제 구현 시 requests.get("https://apis.data.go.kr/...") 사용
    # 여기서는 샘플 데이터를 반환함
    mock_data = [
        {"id": "p1", "name": "해운대 해수욕장", "cat": "Activity", "cost": 0, "desc": "부산의 대표적인 해변"},
        {"id": "p2", "name": "감천문화마을", "cat": "Culture", "cost": 0, "desc": "알록달록한 계단식 마을"},
        {"id": "p3", "name": "더베이101", "cat": "Foodie", "cost": 30000, "desc": "야경과 함께 즐기는 맥주와 치킨"},
        {"id": "p4", "name": "태종대", "cat": "Relax", "cost": 5000, "desc": "해안 절경이 아름다운 공원"},
        {"id": "p5", "name": "신세계 센텀시티", "cat": "Shopping", "cost": 100000, "desc": "세계 최대 규모의 백화점"}
    ]
    # 스타일 기반 필터링 (간단한 예시)
    filtered = [p for p in mock_data if p["cat"] == style or style == "All"]
    return filtered if filtered else mock_data

def optimize_itinerary(user_prefs: Dict, poi_list: List) -> List[DayPlan]:
    """
    사용자 선호도와 POI 리스트를 기반으로 최적의 동선 및 일정을 생성
    (실제로는 TSP 알고리즘이나 LLM을 사용하여 고도화)
    """
    days = []
    duration = user_prefs["duration"]
    # 간단한 분배 로직
    per_day = len(poi_list) // duration if len(poi_list) >= duration else 1
    
    for i in range(duration):
        day_places = []
        start_idx = i * per_day
        end_idx = start_idx + per_day if i < duration - 1 else len(poi_list)
        
        for idx, p in enumerate(poi_list[start_idx:end_idx]):
            day_places.append(Place(
                place_id=p["id"],
                name=p["name"],
                category=p["cat"],
                estimated_cost=p["cost"],
                visit_time=f"{10 + idx*3}:00", # 단순 시간 할당
                description=p["desc"]
            ))
        days.append(DayPlan(day=i+1, places=day_places))
    return days

# --- Endpoints ---

@app.post("/onboarding", status_code=201)
async def create_profile(req: OnboardingRequest):
    in_memory_profiles[req.user_id] = req.dict()
    return {"message": "Profile created successfully", "user_id": req.user_id}

@app.post("/itinerary/generate", response_model=ItineraryResponse)
async def generate_itinerary(user_id: str):
    if user_id not in in_memory_profiles:
        raise HTTPException(status_code=404, detail="User profile not found. Please complete onboarding first.")
    
    profile = in_memory_profiles[user_id]
    
    # 1. 외부 API 데이터 수집 (Simulated)
    poi_candidates = get_tour_api_data(profile["region"], profile["travel_style"])
    
    # 2. AI 기반 일정 최적화 (Simulated)
    optimized_days = optimize_itinerary(profile, poi_candidates)
    
    # 3. 전체 비용 및 예산 체크
    total_cost = sum(place.estimated_cost for day in optimized_days for place in day.places)
    budget_limit = get_budget_limit(profile["budget_range"], profile["duration"])
    budget_exceeded = total_cost > budget_limit
    alternatives = suggest_alternatives("General", total_cost) if budget_exceeded else []
    
    itinerary_id = f"it_釜山_{user_id}"
    response = ItineraryResponse(
        itinerary_id=itinerary_id,
        user_id=user_id,
        days=optimized_days,
        total_cost=total_cost,
        budget_limit=budget_limit,
        budget_exceeded=budget_exceeded,
        alternatives=alternatives
    )
    in_memory_itineraries[itinerary_id] = response
    return response

@app.put("/itinerary/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(itinerary_id: str, req: ItineraryUpdateRequest):
    if itinerary_id not in in_memory_itineraries:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    itinerary = in_memory_itineraries[itinerary_id]
    user_id = itinerary.user_id
    profile = in_memory_profiles[user_id]
    
    target_day_idx = req.day - 1
    if target_day_idx >= len(itinerary.days):
        raise HTTPException(status_code=400, detail="Invalid day")
    
    target_day = itinerary.days[target_day_idx]
    
    if req.action == "reorder":
        places = target_day.places
        p_idx = next((i for i, p in enumerate(places) if p.place_id == req.place_id), None)
        if p_idx is not None and req.target_index is not None:
            p = places.pop(p_idx)
            places.insert(req.target_index, p)
            for idx, place in enumerate(places):
                place.visit_time = f"{10 + idx*3}:00"
                if idx > 0:
                    place.travel_time_from_prev = calculate_travel_time(places[idx-1].place_id, place.place_id)
    
    elif req.action == "remove":
        target_day.places = [p for p in target_day.places if p.place_id != req.place_id]
    
    elif req.action == "add" and req.new_place_data:
        new_p = Place(**req.new_place_data)
        target_day.places.append(new_p)
    
    # 전체 비용 및 예산 재계산
    itinerary.total_cost = sum(place.estimated_cost for day in itinerary.days for place in day.places)
    itinerary.budget_exceeded = itinerary.total_cost > itinerary.budget_limit
    itinerary.alternatives = suggest_alternatives("General", itinerary.total_cost) if itinerary.budget_exceeded else []
    
    return itinerary

@app.post("/itinerary/{itinerary_id}/share")
async def share_itinerary(itinerary_id: str):
    if itinerary_id not in in_memory_itineraries:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    share_code = f"share_{itinerary_id[-5:]}"
    in_memory_shares[share_code] = itinerary_id
    return {"share_link": f"https://tri-p.com/shared/{share_code}", "share_code": share_code}

@app.get("/shared/{share_code}", response_model=ItineraryResponse)
async def get_shared_itinerary(share_code: str):
    if share_code not in in_memory_shares:
        raise HTTPException(status_code=404, detail="Shared link expired or invalid")
    
    it_id = in_memory_shares[share_code]
    return in_memory_itineraries[it_id]

@app.get("/itinerary/{itinerary_id}/export")
async def export_itinerary(itinerary_id: str, format: str = "pdf"):
    if itinerary_id not in in_memory_itineraries:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    itinerary = in_memory_itineraries[itinerary_id]
    # 실제 구현 시 reportlab 이나 fpdf 등을 사용하여 PDF 생성
    return {
        "format": format,
        "filename": f"itinerary_{itinerary_id}.{format}",
        "content_summary": f"Day count: {len(itinerary.days)}, Total cost: {itinerary.total_cost}",
        "download_url": f"https://tri-p.com/downloads/{itinerary_id}.{format}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
