#!/usr/bin/env python3
"""
식품안전처 영양정보 API 테스트
실제 데이터 조회가 되는지 확인
"""

import requests
import json
from typing import Dict, List, Optional

class FoodSafetyNutritionAPI:
    """식품안전처 영양정보 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://various.foodsafetykorea.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def test_api_endpoints(self):
        """다양한 API 엔드포인트 테스트"""
        
        print("=== 식품안전처 영양정보 API 테스트 ===\n")
        
        # 테스트할 엔드포인트들
        endpoints = [
            "/nutrient/industry/openApi/info.do",
            "/nutrient/industry/openApi/search.do", 
            "/nutrient/industry/openApi/list.do",
            "/nutrient/api/search.do",
            "/nutrient/api/info.do"
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(endpoint)
    
    def test_endpoint(self, endpoint: str):
        """개별 엔드포인트 테스트"""
        
        full_url = self.base_url + endpoint
        print(f"테스트 중: {full_url}")
        
        try:
            # GET 요청
            response = self.session.get(full_url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"   응답 내용 (첫 200자): {content}")
                
                # JSON 응답인지 확인
                try:
                    json_data = response.json()
                    print(f"   JSON 응답 확인: {list(json_data.keys()) if isinstance(json_data, dict) else 'Array'}")
                except:
                    print("   HTML 또는 기타 형식 응답")
            else:
                print(f"   요청 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   오류 발생: {e}")
        
        print()
    
    def test_food_search(self, food_name: str = "치킨"):
        """음식 검색 테스트"""
        
        print(f"'{food_name}' 영양정보 검색 테스트")
        
        # 다양한 검색 방법 시도
        search_params = [
            {"q": food_name},
            {"food": food_name},
            {"keyword": food_name},
            {"search": food_name},
            {"foodNm": food_name}
        ]
        
        search_endpoints = [
            "/nutrient/industry/openApi/search.do",
            "/nutrient/api/search.do"
        ]
        
        for endpoint in search_endpoints:
            for params in search_params:
                self.test_search_request(endpoint, params)
    
    def test_search_request(self, endpoint: str, params: Dict):
        """검색 요청 테스트"""
        
        full_url = self.base_url + endpoint
        
        try:
            response = self.session.get(full_url, params=params, timeout=10)
            
            print(f"   {endpoint} + {params}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"   JSON 데이터 수신: {len(json_data) if isinstance(json_data, list) else 'Object'}")
                    
                    # 응답 구조 분석
                    if isinstance(json_data, dict):
                        print(f"   Keys: {list(json_data.keys())}")
                    elif isinstance(json_data, list) and len(json_data) > 0:
                        print(f"   첫 번째 항목 Keys: {list(json_data[0].keys()) if isinstance(json_data[0], dict) else 'Not Dict'}")
                        
                except:
                    content_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
                    print(f"   비 JSON 응답: {content_preview}")
            else:
                print(f"   요청 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   오류: {e}")
        
        print()

def main():
    """메인 테스트 함수"""
    
    api = FoodSafetyNutritionAPI()
    
    # 1. 기본 API 엔드포인트 테스트
    api.test_api_endpoints()
    
    # 2. 음식 검색 테스트
    api.test_food_search("치킨")
    api.test_food_search("불고기")
    api.test_food_search("김치찌개")
    
    print("=== 테스트 완료 ===")
    print("성공적인 응답이 있다면 해당 엔드포인트와 파라미터를 활용 가능합니다.")

if __name__ == "__main__":
    main()