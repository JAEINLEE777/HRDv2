import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 가상 직원 데이터
EMPLOYEES = [
    {"name": "김철수", "department": "영업", "position": "과장"},
    {"name": "이영희", "department": "마케팅", "position": "대리"},
    {"name": "박민준", "department": "인사", "position": "차장"},
    {"name": "정수진", "department": "개발", "position": "선임"},
    {"name": "최재훈", "department": "재무", "position": "부장"},
    {"name": "강지영", "department": "영업", "position": "사원"},
    {"name": "윤서연", "department": "마케팅", "position": "과장"},
    {"name": "임동훈", "department": "개발", "position": "책임"},
    {"name": "한미래", "department": "인사", "position": "대리"},
    {"name": "송태양", "department": "재무", "position": "사원"}
]

# 샘플 데이터 생성 함수
def generate_sample_data(start_date=datetime(2024, 1, 1), end_date=datetime(2024, 12, 31)):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    competencies = ['직무', 'Global', 'SKValues']
    
    data = []
    for employee in EMPLOYEES:
        for date in date_range:
            if np.random.random() > 0.3:  # 70% 확률로 학습 기록 생성
                for competency in competencies:
                    if np.random.random() > 0.5:  # 50% 확률로 각 역량 영역 학습
                        hours = np.random.randint(1, 5)
                        data.append({
                            '날짜': date.strftime('%Y-%m-%d'),
                            '직원': employee['name'],
                            '부서': employee['department'],
                            '직급': employee['position'],
                            '직무역량': competency,
                            '학습시간': hours
                        })
    
    return pd.DataFrame(data)

# 데이터를 TXT 파일로 저장하는 함수
def save_data_to_txt(data, filename='learning_data.txt'):
    data.to_csv(filename, sep='|', index=False)
    st.success(f'데이터가 {filename}에 저장되었습니다.')

# TXT 파일에서 데이터를 불러오는 함수
def load_data_from_txt(filename='learning_data.txt'):
    if os.path.exists(filename):
        data = pd.read_csv(filename, sep='|')
        data['날짜'] = pd.to_datetime(data['날짜'])
        st.success(f'{filename}에서 데이터를 불러왔습니다.')
        return data
    else:
        st.warning(f'{filename}이 존재하지 않습니다. 샘플 데이터를 생성합니다.')
        return generate_sample_data()

# 메인 앱
def main():
    st.title('직무역량별 월별 학습시간 이수현황 대시보드')

    # 데이터 로드 또는 생성
    if st.sidebar.button('새로운 샘플 데이터 생성'):
        df = generate_sample_data()
        save_data_to_txt(df)
    else:
        df = load_data_from_txt()

    # 데이터 전처리
    df['월'] = pd.to_datetime(df['날짜']).dt.to_period('M')
    monthly_data = df.groupby(['월', '직원', '부서', '직급', '직무역량'])['학습시간'].sum().reset_index()
    monthly_data['월'] = monthly_data['월'].astype(str)

    # 사이드바 - 월 선택
    months = sorted(monthly_data['월'].unique())
    selected_month = st.sidebar.selectbox('월 선택', months)

    # 사이드바 - 부서 선택
    departments = ['전체'] + sorted(monthly_data['부서'].unique())
    selected_department = st.sidebar.selectbox('부서 선택', departments)

    # 선택된 월과 부서의 데이터 필터링
    filtered_data = monthly_data[monthly_data['월'] == selected_month]
    if selected_department != '전체':
        filtered_data = filtered_data[filtered_data['부서'] == selected_department]

    # 차트 1: 직원별 총 학습시간 (직무역량별로 구분)
    st.subheader(f'{selected_month} 직원별 총 학습시간 (직무역량별)')
    pivot_data = filtered_data.pivot(index='직원', columns='직무역량', values='학습시간').fillna(0)
    st.bar_chart(pivot_data)

    # 차트 2: 월별 평균 학습시간 추이 (직무역량별)
    st.subheader('직무역량별 월별 평균 학습시간 추이')
    monthly_avg = monthly_data.groupby(['월', '직무역량'])['학습시간'].mean().unstack()
    st.line_chart(monthly_avg)

    # 통계 정보
    st.subheader(f'{selected_month} 통계')
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 평균 학습시간", f"{filtered_data['학습시간'].mean():.2f}시간")
    col2.metric("최대 학습시간", f"{filtered_data['학습시간'].max()}시간")
    col3.metric("최소 학습시간", f"{filtered_data['학습시간'].min()}시간")

    # 직무역량별 평균 학습시간
    st.subheader(f'{selected_month} 직무역량별 평균 학습시간')
    competency_avg = filtered_data.groupby('직무역량')['학습시간'].mean()
    st.bar_chart(competency_avg)

    # 부서별 평균 학습시간
    st.subheader(f'{selected_month} 부서별 평균 학습시간')
    department_avg = filtered_data.groupby('부서')['학습시간'].mean()
    st.bar_chart(department_avg)

    # 데이터 테이블
    st.subheader(f'{selected_month} 상세 데이터')
    st.dataframe(filtered_data)

    # 데이터 저장 버튼
    if st.button('현재 데이터를 TXT 파일로 저장'):
        save_data_to_txt(df)

if __name__ == '__main__':
    main()
