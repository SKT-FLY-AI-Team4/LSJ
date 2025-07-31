#!/usr/bin/env python3
"""
식품안전처 영양정보 API 테스트 v2
웹사이트에서 발견한 실제 JSON API 엔드포인트 테스트
"""

import requests
import json
from typing import Dict, List, Optional

class FoodSafetyNutritionAPIv2:
    """식품안전처 영양정보 API 클라이언트 v2"""
    
    def __init__(self):
        self.base_url = "https://various.foodsafetykorea.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://various.foodsafetykorea.go.kr/nutrient/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def test_discovered_apis(self):
        """웹사이트에서 발견한 API 엔드포인트들 테스트"""
        
        print("=== 발견된 실제 API 엔드포인트 테스트 ===\n")
        
        # 웹사이트에서 발견한 실제 API 엔드포인트들
        api_tests = [
            {
                "name": "월별 검색 API",
                "endpoint": "/nutrient/info/steady/listJson.do",
                "method": "POST",
                "params": {
                    "searchText": "치킨",
                    "searchProcCode": "",
                    "searchLogType": "month",
                    "searchMonth": "202407"
                }
            },
            {
                "name": "음식 첫 번째 리스트",
                "endpoint": "/nutrient/general/food/firstList.do", 
                "method": "POST",
                "params": {
                    "searchText": "치킨"
                }
            },
            {
                "name": "일반 음식 검색",
                "endpoint": "/nutrient/general/food/firstList.do",
                "method": "GET",
                "params": {
                    "q": "치킨",
                    "keyword": "치킨"
                }
            }
        ]
        
        for test in api_tests:
            self.test_api_call(test)
    
    def test_api_call(self, test_config: Dict):
        """개별 API 호출 테스트"""
        
        name = test_config["name"]
        endpoint = test_config["endpoint"]
        method = test_config["method"]
        params = test_config["params"]
        
        full_url = self.base_url + endpoint
        
        print(f"테스트: {name}")
        print(f"URL: {full_url}")
        print(f"Method: {method}")
        print(f"Params: {params}")
        
        try:
            if method.upper() == "POST":
                response = self.session.post(full_url, data=params, timeout=15)
            else:
                response = self.session.get(full_url, params=params, timeout=15)
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"JSON 응답 성공!")
                    
                    # 응답 구조 분석
                    if isinstance(json_data, dict):
                        print(f"응답 Keys: {list(json_data.keys())}")
                        
                        # 실제 데이터가 있는지 확인
                        for key, value in json_data.items():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"  - {key}: {len(value)}개 항목")
                                if isinstance(value[0], dict):
                                    print(f"    첫 번째 항목 Keys: {list(value[0].keys())}")
                                    # 첫 번째 항목 내용 일부 출력
                                    for item_key, item_value in list(value[0].items())[:3]:
                                        print(f"      {item_key}: {item_value}")
                            elif not isinstance(value, (list, dict)):
                                print(f"  - {key}: {value}")
                    
                    elif isinstance(json_data, list):
                        print(f"배열 응답: {len(json_data)}개 항목")
                        if len(json_data) > 0 and isinstance(json_data[0], dict):
                            print(f"첫 번째 항목 Keys: {list(json_data[0].keys())}")
                    
                    print("JSON 응답 내용:")
                    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500] + "...")
                    
                except ValueError as e:
                    content_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"JSON 파싱 실패: {e}")
                    print(f"응답 내용: {content_preview}")
            else:
                print(f"요청 실패: {response.status_code}")
                print(f"응답: {response.text[:200]}...")
        
        except Exception as e:
            print(f"오류 발생: {e}")
        
        print("-" * 60 + "\n")
    
    def test_various_food_searches(self):
        """다양한 음식으로 검색 테스트"""
        
        print("=== 다양한 음식 검색 테스트 ===\n")
        
        foods = ["치킨", "불고기", "김치찌개", "라면", "비빔밥"]
        
        for food in foods:
            # 가장 유망해 보이는 엔드포인트 테스트
            test_config = {
                "name": f"{food} 검색",
                "endpoint": "/nutrient/general/food/firstList.do",
                "method": "POST", 
                "params": {"searchText": food}
            }
            self.test_api_call(test_config)

def main():
    """메인 테스트 함수"""
    
    api = FoodSafetyNutritionAPIv2()
    
    # 1. 발견된 API들 테스트
    api.test_discovered_apis()
    
    # 2. 다양한 음식으로 검색 테스트  
    api.test_various_food_searches()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    main()