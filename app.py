import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from streamlit_gsheets import GSheetsConnection
import json
import os

# ==========================================
# 1. 페이지 설정 및 보안 로드
# ==========================================
st.set_page_config(page_title="Glowuprizz PB Dashboard", page_icon="🚀", layout="wide")
st.title("🚀 인플루언서 컨펌 관리 시스템")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1rstN-Wpgen0gua78qI4lkt0OZhISw6pwLR8yJgR7G1s/edit?gid=0#gid=0"
yt_key = st.secrets.get("YOUTUBE_KEY", "")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# ==========================================
# 2. 마스터 데이터 (누락 0% - 84명 전체)
# ==========================================
raw_data = [
    # --- 자사 (18명) ---
    {"구분": "자사", "세부유형": "전속", "이름": "심장에박현서", "URL": "https://youtube.com/channel/UCo4m81FJ-dT8MqijBlhbN2A", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "생각없이사는연", "URL": "https://youtube.com/channel/UCyVEhwFJ1HF66JqjxMkc-Uw", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "예보링", "URL": "https://youtube.com/channel/UCby6TnEm4xha2NIncRxC2EQ", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "미지수", "URL": "https://youtube.com/channel/UC-BS_A5wCxoCp06thW_V8wA", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 부재중", "URL": "https://youtube.com/channel/UC5Ida86tt8QKa4Myw7idxNg", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "매일제히", "URL": "https://youtube.com/channel/UCWWnWFPkfXMIjxNhBu5qVtg", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 여깄음", "URL": "https://youtube.com/channel/UC9kUsuu1Giqa9V855EWa7-A", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "핏블리 FITVELY", "URL": "https://youtube.com/channel/UC3hRpIQ4x5niJDwjajQSVPg", "추천제품": "-", "아이디어": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "재넌", "URL": "https://youtube.com/channel/UCem8l1w4OWhkqpoOg1SB4_w", "추천제품": "쏙쉐이크 어퍼볼캡", "아이디어": "잦은 먹방 속 쏙쉐이크 식단관리 노출"},
    {"구분": "자사", "세부유형": "전속", "이름": "살빼조", "URL": "https://www.youtube.com/@dietjo311", "추천제품": "쏙쉐이크", "아이디어": "아침 루틴 식사 대용 노출"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "매드브로 MadBros", "URL": "https://youtube.com/channel/UCiTcv_AxQQSx77yGikHHDZw", "추천제품": "볼캡 쏙쉐이크", "아이디어": "쓰줍맨 활동 시 착용"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "독고독채널", "URL": "https://youtube.com/channel/UCEUSANZNPXY1JsBoqhQIgxQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "김승배", "URL": "https://youtube.com/channel/UCPDiMzJdYb0Q-LxoP7W1j7g", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "kiu기우쌤", "URL": "https://youtube.com/channel/UCIZ5rCTYJ0s16FgT7OetVEQ", "추천제품": "솔브 모델링팩", "아이디어": "셀프케어 루틴"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "비타민신지니", "URL": "https://youtube.com/channel/UC9trbyGOOjJmMea3w6c-e2A", "추천제품": "솔브 괄사크림", "아이디어": "붓기 마사지 시연"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "잡식맨", "URL": "https://youtube.com/channel/UCVILvX9vIp-vMFGmCYJtG3A", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "아이뽀 i4", "URL": "https://youtube.com/channel/UC6jtibPJUrtufKBZCm6gbIg", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "대생이", "URL": "https://youtube.com/channel/UChE5nZAIhWS5vYTRjsUgRpQ", "추천제품": "어퍼 체크셔츠", "아이디어": "-"},
    
    # --- 외부 (43명) ---
    {"구분": "외부", "세부유형": "외부", "이름": "조재원", "URL": "https://youtube.com/channel/UC2o_y872S6YvaO1K8EYnoxg", "추천제품": "쏙쉐이크", "아이디어": "동금여사님 먹방"},
    {"구분": "외부", "세부유형": "외부", "이름": "송대익", "URL": "https://youtube.com/channel/UCreFV1bKkKE6ufPtd5XeEJw", "추천제품": "쏙쉐이크", "아이디어": "자취 생활 노출"},
    {"구분": "외부", "세부유형": "외부", "이름": "엄지렐라", "URL": "https://youtube.com/channel/UCLXafJ8yYXeUN_eHai-6Pgw", "추천제품": "어퍼", "아이디어": "엄지훈 캐릭터 활용"},
    {"구분": "외부", "세부유형": "외부", "이름": "숏박스", "URL": "https://youtube.com/channel/UC1B6SalAoiJD7eHfMUA9QrA", "추천제품": "어퍼", "아이디어": "스케치코미디 연출"},
    {"구분": "외부", "세부유형": "외부", "이름": "김선태", "URL": "https://youtube.com/channel/UCt-BApVtJGrvF5pCgbiNVeg", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "하루의하루", "URL": "https://youtube.com/channel/UCpQxvEhfR60LR4s7PV48qIw", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "찰스엔터", "URL": "https://youtube.com/channel/UCCZ-gBdN59pF39tbm16xvdQ", "추천제품": "쏙쉐이크", "아이디어": "브이로그 출연"},
    {"구분": "외부", "세부유형": "외부", "이름": "침착맨", "URL": "https://youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "랄랄", "URL": "https://youtube.com/channel/UCEX1cZB5TL7jyKejXdTXCKA", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "오늘의 주우재", "URL": "https://youtube.com/channel/UCw-kXdzxMdMdLNI0ZlFFbmA", "추천제품": "어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "자유부인 한가인", "URL": "https://youtube.com/channel/UCvnVUhn95YfQazC_bc2lU6w", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "핫이슈지", "URL": "https://youtube.com/channel/UCdMeT09aEFDCH0NghWV41HQ", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "주둥이방송", "URL": "https://youtube.com/channel/UC9ta639M37zzWKwo7kKc80A", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "RISABAE", "URL": "https://youtube.com/channel/UC9kmlDcqksaOnCkC_qzGacA", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "고기남자", "URL": "https://youtube.com/channel/UCT3CumbFIJiW33uq0UI3zlg", "추천제품": "쏙쉐이크", "아이디어": "먹방 후 관리"},
    {"구분": "외부", "세부유형": "외부", "이름": "사내뷰공업", "URL": "https://youtube.com/channel/UCeS6R89S32mSOxTNoEqrN7g", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "쓰까르", "URL": "https://youtube.com/channel/UCX14ZlyF0-tgVcDxLj-4ytA", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "융덕", "URL": "https://youtube.com/channel/UC_zXObQdOXbUGe8IyVRcpSw", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "우정잉", "URL": "https://youtube.com/channel/UCW945UjEs6Jm3rVNvPEALdg", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "망구", "URL": "https://youtube.com/channel/UCII-TCayU-6gkfzfgJKsFZw", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "시네", "URL": "https://youtube.com/channel/UC0-yyrDjTJ1YFzmV12vEp0Q", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "와코", "URL": "https://youtube.com/channel/UC8NmKAjUM0K4TZqNgboNEWA", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "연두콩", "URL": "https://youtube.com/channel/UCAUbDYDwV34yk6pYiZg_CzA", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "젼언니", "URL": "https://youtube.com/channel/UCyar0OYt0LoPzkkWcQAo6OA", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "지원", "URL": "https://youtube.com/channel/UCURnLWTrLZVv_KiVaeZakog", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "아인이놀아주기", "URL": "https://youtube.com/channel/UCKbsO2vQ9artnn2P-HLnYgQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "민와와", "URL": "https://youtube.com/channel/UCJt-9Ku_D1Un6brccoTzglg", "추천제품": "어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "보현", "URL": "https://youtube.com/channel/UCZkNETnsbFXG8h7RPQyBtNw", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "민가든", "URL": "https://youtube.com/channel/UCr_QBNzvSm_a7mreIpTregw", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "모르는지", "URL": "https://youtube.com/channel/UCDITZg2t7QPjwx_CYFmP_aw", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "최종시안", "URL": "https://youtube.com/channel/UC_1ETgrcrLjHOP0YJmkWLVQ", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "진짜팥", "URL": "https://youtube.com/channel/UCLiiqZrEaA2nvDNC4v9Noiw", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "이리유", "URL": "https://youtube.com/channel/UCRFh2MoRiD-whPn0QuOzMFQ", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "기몌민", "URL": "https://youtube.com/channel/UC78welXHRpNJJfiB2zg5BSQ", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "홍또기", "URL": "https://youtube.com/channel/UCsjNYWQvbzb_4z4t_sL1y6w", "추천제품": "어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "람누끼", "URL": "https://youtube.com/channel/UC8fizCcGKHfrQKfvGtFiOiw", "추천제품": "어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "유플라", "URL": "https://youtube.com/channel/UCxlqra6Gb7BvpOaZaqD-duQ", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "허진희여사", "URL": "https://youtube.com/channel/UCsK4opmMoeLsRsZU54ghvtQ", "추천제품": "립타투", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "냥이아빠", "URL": "https://youtube.com/channel/UC5AAf4_zZxk-mCl46TogZQQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "김민지", "URL": "https://youtube.com/channel/UCB9jzo97ZxA5Kl6JDfX0UPw", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "김크리스탈", "URL": "https://youtube.com/channel/UCcNYkzLMSkSiYaiAYjUNzRg", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "다인이공", "URL": "https://youtube.com/channel/UCs7Bw5CQK82AHhyMQ59NZWA", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "김밍", "URL": "https://youtube.com/channel/UCTjwlF8Y8hxR85JPUoZv-6A", "추천제품": "멜브", "아이디어": "-"},

    # --- 벤더사 (10명) ---
    {"구분": "벤더사", "세부유형": "1억 이상", "이름": "한스스타일", "URL": "https://www.instagram.com/hansstyle_hanna/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "1억 이상", "이름": "11AM", "URL": "https://www.instagram.com/he11o_yeojin/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "규모급", "이름": "강지혜", "URL": "https://www.instagram.com/hairstyle_jihye/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "규모급", "이름": "츄니토리", "URL": "https://www.instagram.com/chunytory/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "규모급", "이름": "헤이가가", "URL": "https://www.instagram.com/hey_gaga_/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "중대형", "이름": "뚜뜨", "URL": "https://www.instagram.com/mintoute_/", "추천제품": "쏙쉐이크", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "중대형", "이름": "아뜨와지효", "URL": "https://www.instagram.com/atoi_jihyo/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "평균급", "이름": "엔젤루밍", "URL": "https://www.instagram.com/ryu_angel/", "추천제품": "모델링팩", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "평균급", "이름": "캘러리아", "URL": "https://www.instagram.com/hyo_kate_olivia/", "추천제품": "미스트", "상세 정보": "인스타 공구 타겟"},
    {"구분": "벤더사", "세부유형": "평균급", "이름": "리미샵", "URL": "https://www.instagram.com/limi_unni/", "추천제품": "솔브", "상세 정보": "인스타 공구 타겟"},

    # --- 소속사 (13명) ---
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "linakeemz", "URL": "https://www.instagram.com/linakeemz/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 11.9만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "1__xixx", "URL": "https://www.instagram.com/1__xixx/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 4.3만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "lee_dan2", "URL": "https://www.instagram.com/lee_dan2/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 15.7만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "from.suason", "URL": "https://www.instagram.com/from.suason/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 15.2만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "ziyoo_days", "URL": "https://www.instagram.com/ziyoo_days/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 5만 / 단가: 208만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "alisswlle", "URL": "https://www.instagram.com/alisswlle/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 7.4만 / 단가: 195만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "s0la._.c", "URL": "https://www.instagram.com/s0la._.c/", "추천제품": "솔브/멜브", "상세 정보": "구독자: 5.4만 / 단가: 130만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "무찌", "URL": "https://www.youtube.com/@muzzi_youtube", "추천제품": "솔브/멜브", "상세 정보": "구독자: 17.9만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "히루히루", "URL": "https://www.youtube.com/@heeruheeru", "추천제품": "솔브/멜브", "상세 정보": "구독자: 12.7만 / 단가: 260만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "채울렛", "URL": "https://www.youtube.com/@chaeullet", "추천제품": "솔브/멜브", "상세 정보": "구독자: 8.7만 / 단가: 195만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "후Hoo", "URL": "https://www.youtube.com/@Hoo_short", "추천제품": "솔브/멜브", "상세 정보": "구독자: 5.3만 / 단가: 130만 / RS 30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "송타민", "URL": "https://www.youtube.com/@songtamin", "추천제품": "솔브/멜브", "상세 정보": "구독자: 2만 / 단가: 91만 / RS 30%"},
    {"구분": "트레져헌터", "세부유형": "유튜브", "이름": "버터와여름이네", "URL": "https://www.youtube.com/@butterfamilyS", "추천제품": "솔브", "상세 정보": "구독자: 22.96만 / RS 30% / 솔브 전달완료"},
]

# ==========================================
# 3. 데이터 로드 및 시트 동기화
# ==========================================
def load_and_sync_data():
    master_df = pd.DataFrame(raw_data)
    
    # "아이디어" 열이 있는 데이터는 "상세 정보"로 통일
    if '아이디어' in master_df.columns:
        master_df['상세 정보'] = master_df['상세 정보'].fillna(master_df['아이디어'])
    
    # 구글 시트 기존 상태 불러오기
    if conn:
        try:
            sheet_df = conn.read(worksheet="Sheet1")
            if not sheet_df.empty and '이름' in sheet_df.columns and '컨펌상태' in sheet_df.columns:
                status_map = dict(zip(sheet_df['이름'], sheet_df['컨펌상태']))
                master_df['컨펌상태'] = master_df['이름'].map(status_map).fillna('대기')
            else:
                master_df['컨펌상태'] = '대기'
        except:
            master_df['컨펌상태'] = '대기'
    else:
        master_df['컨펌상태'] = '대기'
    
    master_df.insert(0, '번호', range(1, len(master_df) + 1))
    return master_df

if 'df_master' not in st.session_state:
    st.session_state.df_master = load_and_sync_data()

# ==========================================
# 4. 이미지 캐싱 로직
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "profile_cache.json")

def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    with open(CACHE_FILE, "r") as f: return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f: json.dump(cache, f)

if 'img_cache' not in st.session_state: st.session_state.img_cache = load_cache()

def get_yt_profile_pic(url, api_key):
    if url in st.session_state.img_cache: return st.session_state.img_cache[url]
    if not api_key or "youtube" not in url: return "https://via.placeholder.com/300x300.png?text=Glowuprizz"
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        if '/channel/' in url: c_id = url.split('/channel/')[1].split('/')[0].split('?')[0]
        elif '@' in url:
            handle = '@' + url.split('@')[1].split('/')[0].split('?')[0]
            res = youtube.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
            c_id = res['items'][0]['snippet']['channelId']
        else: return "https://via.placeholder.com/300x300.png?text=Glowuprizz"
        c_res = youtube.channels().list(part="snippet", id=c_id).execute()
        img_url = c_res['items'][0]['snippet']['thumbnails']['medium']['url']
        st.session_state.img_cache[url] = img_url
        save_cache(st.session_state.img_cache)
        return img_url
    except: return "https://via.placeholder.com/300x300.png?text=Not+Found"

# ==========================================
# 5. 선택/일괄 컨펌 로직 및 갤러리 UI
# ==========================================
def _apply_bulk_status(target_df, new_status):
    updated = False
    for idx in target_df.index:
        chk_key = f"chk_{idx}"
        # 체크박스가 선택된 항목만 상태 업데이트!
        if st.session_state.get(chk_key, False):
            st.session_state.df_master.at[idx, '컨펌상태'] = new_status
            st.session_state[chk_key] = False # 처리 후 체크박스 해제
            updated = True
    
    if updated:
        if conn: # 구글 시트에 즉시 반영
            try:
                conn.update(worksheet="Sheet1", data=st.session_state.df_master)
                st.success(f"✅ 선택한 프로필들이 '{new_status}' 처리되어 구글 시트에 반영되었습니다!")
            except Exception as e:
                st.error(f"구글 시트 연동 실패: {e}")
        st.rerun()

def bulk_action_ui(target_df, title):
    st.subheader(title)
    c1, c2, c3, c4, _ = st.columns([1.5, 1.5, 1.5, 1.5, 4])
    with c1:
        if st.button("☑️ 선택 항목 승인", key=f"bulk_app_{title}"):
            _apply_bulk_status(target_df, "승인 ✅")
    with c2:
        if st.button("☑️ 선택 항목 반려", key=f"bulk_rej_{title}"):
            _apply_bulk_status(target_df, "반려 ❌")
    with c3:
        if st.button("☑️ 선택 항목 보류", key=f"bulk_wait_{title}"):
            _apply_bulk_status(target_df, "보류 ⏳")

def draw_gallery_with_confirm(df_subset, num_cols=8):
    df_clean = df_subset.reset_index(drop=True)
    cols = st.columns(num_cols)
    options = ["대기", "승인 ✅", "반려 ❌", "보류 ⏳"]
    
    for i, row in df_clean.iterrows():
        idx = st.session_state.df_master[st.session_state.df_master['이름'] == row['이름']].index[0]
        
        with cols[i % num_cols]:
            with st.container(border=True):
                # ⭐ 프로필 위에 체크박스와 개별 상태 변경 드롭다운 배치
                c_chk, c_sel = st.columns([1, 2.5])
                with c_chk:
                    st.checkbox("선택", key=f"chk_{idx}", label_visibility="collapsed")
                with c_sel:
                    current_status = st.session_state.df_master.at[idx, '컨펌상태']
                    if current_status not in options: current_status = "대기"
                    new_status = st.selectbox(
                        "상태", options, index=options.index(current_status),
                        key=f"status_{idx}", label_visibility="collapsed"
                    )
                    if new_status != current_status:
                        st.session_state.df_master.at[idx, '컨펌상태'] = new_status
                
                pic_url = get_yt_profile_pic(row.get('URL', '-'), yt_key)
                st.markdown(f'<div style="width: 100%; aspect-ratio: 1/1; overflow: hidden; border-radius: 6px; margin-bottom: 8px;"><img src="{pic_url}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                st.markdown(f"**{row['이름']}**")
                st.caption(f"{row.get('세부유형','')}")
                st.markdown(f"<small>🎯 {row.get('추천제품', '-')}</small>", unsafe_allow_html=True)
                with st.expander("📝"):
                    st.write(row.get('상세 정보', '내용 없음'))
                if row.get('URL', '-') != '-': st.link_button("🔗", row['URL'], use_container_width=True)

# ==========================================
# 6. 화면 구성
# ==========================================
tabs = st.tabs(["📊 통합 컨펌", "🏢 자사", "🌍 외부", "🤝 벤더사", "🏢 소속사"])

with tabs[0]:
    st.header("📋 전체 리스트 통합 컨펌")
    edited_df = st.data_editor(
        st.session_state.df_master,
        column_config={
            "번호": st.column_config.NumberColumn("No.", width="small", disabled=True),
            "URL": st.column_config.LinkColumn("링크"),
            "컨펌상태": st.column_config.SelectboxColumn("결정", options=["대기", "승인 ✅", "반려 ❌", "보류 ⏳"])
        },
        use_container_width=True, hide_index=True, key="main_editor"
    )
    st.session_state.df_master = edited_df
    
    col_save, col_link = st.columns([1, 4])
    with col_save:
        if st.button("💾 구글 시트 저장", type="primary"):
            if conn:
                try:
                    conn.update(worksheet="Sheet1", data=st.session_state.df_master)
                    st.success("✅ 구글 시트 업데이트 완료!")
                except Exception as e: st.error(f"❌ 저장 실패: {e}")
    with col_link:
        st.link_button("📂 구글 시트 바로가기", SHEET_URL)

with tabs[1]:
    st.header("🏢 자사 크리에이터")
    # 짧은 슬라이더, 기본값 8
    col_sl, _ = st.columns([1, 3])
    with col_sl: num_cols_our = st.slider("가로 배치 조절", 2, 8, 8, key="slider_our")
    
    df_our = st.session_state.df_master[st.session_state.df_master['구분']=='자사']
    bulk_action_ui(df_our, "☑️ 자사 리스트 일괄 처리")
    
    for sub in ["전속", "파트너십", "프로젝트 협업"]:
        st.markdown(f"##### 💎 {sub}")
        draw_gallery_with_confirm(df_our[df_our['세부유형']==sub], num_cols=num_cols_our)
        st.divider()

with tabs[2]:
    st.header("🌍 외부 크리에이터")
    # 짧은 슬라이더, 기본값 8
    col_sl, _ = st.columns([1, 3])
    with col_sl: num_cols_ext = st.slider("가로 배치 조절", 2, 8, 8, key="slider_ext")
    
    df_ext = st.session_state.df_master[st.session_state.df_master['구분']=='외부']
    bulk_action_ui(df_ext, "☑️ 외부 리스트 일괄 처리")
    draw_gallery_with_confirm(df_ext, num_cols=num_cols_ext)

with tabs[3]:
    st.header("🤝 벤더사 리스트")
    df_vn = st.session_state.df_master[st.session_state.df_master['구분']=='벤더사']
    st.dataframe(df_vn, use_container_width=True, hide_index=True)

with tabs[4]:
    st.header("🏢 소속사 협업 리스트")
    # 연락처 100% 복구
    st.info("**📞 소속사 담당자 연락처**\n\n* **샌드박스:** AD2 l BD l 허현지님 (hjhuh@sandbox.co.kr)\n* **트레져헌터:** 숏폼사업팀 박예은 매니저님 (yeeun_p@treasurehunter.co.kr)")
    df_ag = st.session_state.df_master[st.session_state.df_master['구분'].isin(['샌드박스', '트레져헌터'])]
    st.dataframe(df_ag, use_container_width=True, hide_index=True)
