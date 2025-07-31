#!/usr/bin/env python3
"""
sample_data.xlsx의 실제 가게-메뉴 매핑 확인
"""

import pandas as pd

def check_sample_data():
    """sample_data.xlsx의 가게-메뉴 매핑 확인"""
    
    print("=== sample_data.xlsx 가게-메뉴 분석 ===")
    
    try:
        df = pd.read_excel('sample_data.xlsx')
        print(f"총 행수: {len(df)}")
        print(f"컬럼: {list(df.columns)}")
        
        print("\n=== 가게별 실제 정보 ===")
        for idx, row in df.iterrows():
            shop_name = row.get('shopName', '')
            category = row.get('category', '')
            address = row.get('addressName', '')
            is_good = row.get('isGoodInfluenceShop', '')
            is_food_card = row.get('isFoodCardShop', '')
            
            print(f"{idx+1:2d}. {shop_name} ({category}) - 착한가게:{is_good}, 급식카드:{is_food_card}")
            print(f"    주소: {address}")
            print()
        
        print("\n=== 카테고리별 그룹화 ===")
        category_groups = df.groupby('category')
        for category, group in category_groups:
            shops = []
            for _, row in group.iterrows():
                shop_name = row.get('shopName', '')
                shops.append(shop_name)
            
            print(f"• {category}: {', '.join(shops)}")
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_sample_data()