#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import traceback
import json

def analyze_excel_file(file_path):
    """Excel 파일의 모든 시트를 분석하는 함수"""
    results = {
        "file_name": file_path,
        "total_sheets": 0,
        "sheets": {},
        "user_related_info": []
    }
    
    try:
        # pandas로 모든 시트 이름 확인
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        results["total_sheets"] = len(sheet_names)
        
        print("=== Excel 파일 분석 결과 ===")
        print(f"파일명: {file_path}")
        print(f"총 시트 수: {len(sheet_names)}")
        print("\n=== 모든 시트 이름 ===")
        for i, sheet in enumerate(sheet_names):
            print(f"{i+1}. {sheet}")

        print("\n" + "="*60)

        # 각 시트별 상세 분석
        for sheet_name in sheet_names:
            print(f"\n=== 시트: {sheet_name} ===")
            sheet_info = {
                "name": sheet_name,
                "rows": 0,
                "columns": 0,
                "column_list": [],
                "column_details": {},
                "user_related_columns": [],
                "sample_data": []
            }
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_info["rows"] = len(df)
                sheet_info["columns"] = len(df.columns)
                sheet_info["column_list"] = list(df.columns)
                
                print(f"행 수: {len(df)}")
                print(f"열 수: {len(df.columns)}")
                
                # 컬럼 정보 출력
                print(f"\n컬럼 목록:")
                for i, col in enumerate(df.columns):
                    print(f"  {i+1}. {col}")
                
                # 각 컬럼의 데이터 타입과 샘플 데이터
                print(f"\n컬럼별 상세 정보:")
                for col in df.columns:
                    non_null_count = df[col].count()
                    null_count = len(df) - non_null_count
                    
                    col_info = {
                        "dtype": str(df[col].dtype),
                        "non_null_count": int(non_null_count),
                        "null_count": int(null_count),
                        "sample_values": [],
                        "unique_count": 0
                    }
                    
                    print(f"  {col}:")
                    print(f"     - 데이터 타입: {df[col].dtype}")
                    print(f"     - 유효 데이터: {non_null_count}개, 빈 데이터: {null_count}개")
                    
                    # null이 아닌 샘플 값들 출력
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        sample_values = non_null_values.head(3).tolist()
                        col_info["sample_values"] = [str(val) for val in sample_values]
                        col_info["unique_count"] = int(non_null_values.nunique())
                        
                        print(f"     - 샘플 값: {sample_values}")
                        if len(non_null_values) > 3:
                            print(f"     - 고유값 수: {non_null_values.nunique()}개")
                    else:
                        print(f"     - 샘플 값: (모든 값이 비어있음)")
                    
                    sheet_info["column_details"][col] = col_info
                
                # 처음 3행 미리보기
                print(f"\n처음 3행 미리보기:")
                if len(df) > 0:
                    preview = df.head(3)
                    sample_rows = []
                    for idx, row in preview.iterrows():
                        row_data = {}
                        print(f"  행 {idx + 1}:")
                        for col in df.columns:
                            value = row[col]
                            if pd.isna(value):
                                value = "(빈값)"
                                row_data[col] = None
                            else:
                                row_data[col] = str(value)
                            print(f"    {col}: {value}")
                        sample_rows.append(row_data)
                        print()
                    sheet_info["sample_data"] = sample_rows
                else:
                    print("  (데이터가 없습니다)")
                    
                # user 관련 정보 확인
                user_keywords = ['user', '사용자', '유저', 'customer', '고객', 'member', '회원']
                user_related_cols = []
                for col in df.columns:
                    col_lower = col.lower()
                    for keyword in user_keywords:
                        if keyword in col_lower:
                            user_related_cols.append(col)
                            break
                
                if user_related_cols:
                    sheet_info["user_related_columns"] = user_related_cols
                    print(f"\nUser 관련 컬럼 발견: {user_related_cols}")
                    results["user_related_info"].append({
                        "sheet": sheet_name,
                        "columns": user_related_cols
                    })
                    
            except Exception as e:
                print(f"시트 읽기 오류: {e}")
                sheet_info["error"] = str(e)
            
            results["sheets"][sheet_name] = sheet_info
            print("\n" + "-"*60)
            
        excel_file.close()
        
        # 전체 요약 출력
        print("\n" + "="*60)
        print("=== 전체 분석 요약 ===")
        print(f"총 {len(sheet_names)}개 시트 분석 완료")
        
        if results["user_related_info"]:
            print("\nUser 관련 정보 요약:")
            for info in results["user_related_info"]:
                print(f"  - {info['sheet']} 시트: {info['columns']}")
        else:
            print("\nUser 관련 컬럼을 찾지 못했습니다.")
            
        # 결과를 JSON 파일로 저장
        with open('excel_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n분석 결과가 excel_analysis_result.json 파일로 저장되었습니다.")
        
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        traceback.print_exc()
        
    return results

if __name__ == "__main__":
    file_path = "sample_data_copy.xlsx"  # 복사본 사용
    analyze_excel_file(file_path)