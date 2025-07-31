#!/usr/bin/env python3
"""
sample_data.xlsx를 AI 친화적 JSON 형태로 변환하는 스크립트
Gemini-Claude 협력 개발
"""

import pandas as pd
import json
from pathlib import Path
import re
from datetime import datetime

def clean_korean_text(text):
    """한글 텍스트 정리"""
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()

def parse_hours(open_hour, close_hour, break_start=None, break_end=None):
    """운영시간 정보를 구조화"""
    hours = {
        "open": clean_korean_text(open_hour),
        "close": clean_korean_text(close_hour)
    }
    
    if break_start and break_end:
        hours["break"] = f"{clean_korean_text(break_start)}-{clean_korean_text(break_end)}"
    
    return hours

def determine_good_shop_status(is_good_influence, is_food_card):
    """착한가게 여부 판정 (Gemini 전략 적용)"""
    # 원래 착한가게면 True
    if is_good_influence == 1:
        return True
    
    # 급식카드 가맹점이면 착한가게로 간주 (대안 전략)
    if clean_korean_text(is_food_card).lower() in ['yes', 'y', '1']:
        return True
    
    return False

def extract_tags_from_shop(shop_name, category, message, address):
    """가게 정보에서 검색 태그 추출"""
    tags = []
    
    # 카테고리 기반 태그
    if category:
        tags.append(clean_korean_text(category))
    
    # 지역 정보 추출
    if address:
        address_clean = clean_korean_text(address)
        # 구 이름 추출 (예: "관악구", "성북구")
        district_match = re.search(r'(\w+구)', address_clean)
        if district_match:
            tags.append(district_match.group(1))
    
    # 가게명에서 키워드 추출
    if shop_name:
        name_clean = clean_korean_text(shop_name)
        # 주요 키워드 추출 (카츠, 커피, 밥상 등)
        keywords = re.findall(r'(카츠|커피|밥상|치킨|파스타|피자|한식|일식|중식|양식)', name_clean)
        tags.extend(keywords)
    
    # 메시지에서 키워드 추출
    if message:
        message_clean = clean_korean_text(message)
        if '급식카드' in message_clean:
            tags.append('급식카드')
        if '나눔' in message_clean:
            tags.append('나눔')
    
    # 중복 제거하고 반환
    return list(set(filter(None, tags)))

def generate_menu_by_category(shop_name, category):
    """카테고리별 기본 메뉴 생성 (메뉴 정보 부재 시 대안)"""
    category_clean = clean_korean_text(category).lower()
    
    menu_templates = {
        '일식': [
            {'name': '돈까스', 'price': 12000},
            {'name': '치즈카츠', 'price': 13000},
            {'name': '우동', 'price': 8000}
        ],
        '한식': [
            {'name': '불고기정식', 'price': 10000},
            {'name': '김치찌개', 'price': 8000},
            {'name': '된장찌개', 'price': 7000}
        ],
        '기타/디저트': [
            {'name': '아메리카노', 'price': 4000},
            {'name': '카페라떼', 'price': 4500},
            {'name': '케이크', 'price': 6000}
        ],
        '치킨': [
            {'name': '후라이드치킨', 'price': 15000},
            {'name': '양념치킨', 'price': 16000},
            {'name': '간장치킨', 'price': 16000}
        ]
    }
    
    # 카테고리별 기본 메뉴 반환
    for key, menus in menu_templates.items():
        if key in category_clean:
            return menus
    
    # 기본 메뉴 (카테고리가 매칭되지 않는 경우)
    return [
        {'name': '추천메뉴1', 'price': 10000},
        {'name': '추천메뉴2', 'price': 12000}
    ]

def convert_excel_to_optimized_json(excel_path, output_path):
    """Excel 파일을 AI 최적화된 JSON으로 변환"""
    print(f"Excel 파일 읽는 중: {excel_path}")
    
    try:
        # Excel 파일 읽기
        df = pd.read_excel(excel_path, sheet_name=0)
        print(f"{len(df)}개 가게 데이터 로드 완료")
        
        # 최적화된 구조로 변환
        restaurants = []
        
        for idx, row in df.iterrows():
            # 기본 정보 추출
            shop_name = clean_korean_text(row.get('shopName', ''))
            category = clean_korean_text(row.get('category', ''))
            address = clean_korean_text(row.get('addressName', ''))
            message = clean_korean_text(row.get('message', ''))
            
            if not shop_name:  # 가게명이 없으면 스킵
                continue
            
            # 고유 ID 생성 (가게명 기반)
            shop_id = re.sub(r'[^\w가-힣]', '_', shop_name)
            
            # 착한가게 여부 판정 (Gemini 전략)
            is_good_shop = determine_good_shop_status(
                row.get('isGoodInfluenceShop', 0),
                row.get('isFoodCardShop', '')
            )
            
            # 급식카드 가능 여부
            accepts_meal_card = clean_korean_text(row.get('isFoodCardShop', '')).lower() in ['yes', 'y', '1', 'unknown']
            
            # 운영시간 구조화
            hours = parse_hours(
                row.get('openHour'),
                row.get('closeHour'),
                row.get('breakStartHour'),
                row.get('breakEndHour')
            )
            
            # 검색 태그 생성
            tags = extract_tags_from_shop(shop_name, category, message, address)
            
            # 메뉴 정보 생성 (기본 템플릿 사용)
            menus = generate_menu_by_category(shop_name, category)
            
            # 최적화된 구조로 조립
            restaurant = {
                "shopId": shop_id,
                "shopName": shop_name,
                "category": category,
                "tags": tags,
                "location": {
                    "address": address,
                    "coordinates": clean_korean_text(row.get('addressPoint', ''))
                },
                "contact": {
                    "phone": clean_korean_text(row.get('contact', ''))
                },
                "hours": hours,
                "attributes": {
                    "isGoodShop": is_good_shop,
                    "acceptsMealCard": accepts_meal_card,
                    "isApproved": row.get('approved', 0) == 1
                },
                "description": message if message else f"{shop_name}에 오신 것을 환영합니다!",
                "menus": menus,
                "metadata": {
                    "originalId": int(row.get('id', 0)),
                    "createdAt": clean_korean_text(row.get('createdAt', '')),
                    "lastUpdated": datetime.now().isoformat()
                }
            }
            
            restaurants.append(restaurant)
        
        # 결과 구조화
        result = {
            "metadata": {
                "source": "sample_data.xlsx",
                "convertedAt": datetime.now().isoformat(),
                "totalShops": len(restaurants),
                "goodShops": sum(1 for r in restaurants if r["attributes"]["isGoodShop"]),
                "converter": "Gemini-Claude 협력 개발"
            },
            "restaurants": restaurants
        }
        
        # JSON 파일로 저장
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"변환 완료: {output_path}")
        print(f"총 가게 수: {len(restaurants)}")
        print(f"착한가게 수: {sum(1 for r in restaurants if r['attributes']['isGoodShop'])}")
        print(f"급식카드 가맹점: {sum(1 for r in restaurants if r['attributes']['acceptsMealCard'])}")
        
        return result
        
    except Exception as e:
        print(f"변환 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    excel_file = "sample_data.xlsx"
    json_file = "data/restaurants_optimized.json"
    
    print("Excel -> JSON 변환 시작 (Gemini-Claude 협력)")
    print("=" * 50)
    
    try:
        result = convert_excel_to_optimized_json(excel_file, json_file)
        
        print("\n" + "=" * 50)
        print("변환 성공!")
        print(f"출력 파일: {json_file}")
        print(f"데이터 미리보기:")
        
        # 첫 번째 가게 정보 출력
        if result["restaurants"]:
            first_shop = result["restaurants"][0]
            print(f"   가게명: {first_shop['shopName']}")
            print(f"   카테고리: {first_shop['category']}")
            print(f"   착한가게: {'예' if first_shop['attributes']['isGoodShop'] else '아니오'}")
            print(f"   급식카드: {'가능' if first_shop['attributes']['acceptsMealCard'] else '불가능'}")
            print(f"   태그: {', '.join(first_shop['tags'])}")
        
    except Exception as e:
        print(f"실행 실패: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)