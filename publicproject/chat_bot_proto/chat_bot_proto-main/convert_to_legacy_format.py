#!/usr/bin/env python3
"""
새로운 restaurants_optimized.json을 기존 test_data.json 형태로 변환
기존 코드와의 호환성 유지
"""

import json
from pathlib import Path

def convert_to_legacy_format(optimized_file, legacy_file):
    """최적화된 형태를 기존 형태로 변환"""
    print(f"변환 시작: {optimized_file} -> {legacy_file}")
    
    # 최적화된 JSON 읽기
    with open(optimized_file, 'r', encoding='utf-8') as f:
        optimized_data = json.load(f)
    
    # 기존 형태로 변환
    legacy_data = {
        "shops": {},
        "menus": {}
    }
    
    menu_id = 1
    
    for idx, restaurant in enumerate(optimized_data["restaurants"], 1):
        # 가게 정보 변환
        shop_data = {
            "id": idx,
            "name": restaurant["shopName"],
            "category": restaurant["category"],
            "is_good_influence_shop": restaurant["attributes"]["isGoodShop"],
            "is_food_card_shop": "Y" if restaurant["attributes"]["acceptsMealCard"] else "N",
            "address": restaurant["location"]["address"],
            "open_hour": restaurant["hours"]["open"],
            "close_hour": restaurant["hours"]["close"],
            "owner_message": restaurant["description"],
            "ordinary_discount": False  # 기본값
        }
        
        legacy_data["shops"][str(idx)] = shop_data
        
        # 메뉴 정보 변환
        for menu in restaurant["menus"]:
            menu_data = {
                "id": menu_id,
                "shop_id": idx,
                "name": menu["name"],
                "price": menu["price"],
                "description": f"{menu['name']} - {restaurant['shopName']}의 대표메뉴",
                "category": restaurant["category"],
                "is_popular": True  # 기본값
            }
            
            legacy_data["menus"][str(menu_id)] = menu_data
            menu_id += 1
    
    # 파일 저장
    with open(legacy_file, 'w', encoding='utf-8') as f:
        json.dump(legacy_data, f, ensure_ascii=False, indent=2)
    
    print(f"변환 완료!")
    print(f"가게 수: {len(legacy_data['shops'])}")
    print(f"메뉴 수: {len(legacy_data['menus'])}")
    
    return legacy_data

def main():
    optimized_file = "data/restaurants_optimized.json"
    legacy_file = "rag/test_data_new.json"
    
    # 변환 실행
    result = convert_to_legacy_format(optimized_file, legacy_file)
    
    # 기존 파일 백업 후 교체
    original_file = "rag/test_data.json"
    backup_file = "rag/test_data_backup.json"
    
    # 백업
    import shutil
    shutil.copy2(original_file, backup_file)
    print(f"기존 파일 백업: {backup_file}")
    
    # 교체
    shutil.copy2(legacy_file, original_file)
    print(f"새 데이터로 교체 완료: {original_file}")

if __name__ == "__main__":
    main()