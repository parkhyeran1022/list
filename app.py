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
st.title("🚀 인플루언서 통합 컨펌 및 관리 시스템")

# Secrets 데이터 로드
yt_key = st.secrets.get("YOUTUBE_KEY", "")
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ 구글 시트 연결 설정을 확인해주세요.")
    conn = None

# ==========================================
# 2. 데이터 세팅 (누락 0% - 80여명 전체 명단)
# ==========================================

# [1] 자사 데이터 (18명)
yt_data_our = [
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
    {"구분": "자사", "세부유형": "파트너십", "이름": "비타민신지니 VitaminJINY", "URL": "https://youtube.com/channel/UC9trbyGOOjJmMea3w6c-e2A", "추천제품": "솔브 괄사크림", "아이디어": "붓기 마사지 시연"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "잡식맨 JOBXICMAN", "URL": "https://youtube.com/channel/UCVILvX9vIp-vMFGmCYJtG3A", "추천제품": "쏙쉐이크 어퍼볼캡", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "아이뽀 i4", "URL": "https://youtube.com/channel/UC6jtibPJUrtufKBZCm6gbIg", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "대생이", "URL": "https://youtube.com/channel/UChE5nZAIhWS5vYTRjsUgRpQ", "추천제품": "어퍼 볼캡 체크셔츠", "아이디어": "-"}
]

# [2] 외부 데이터 (43명)
yt_data_ext = [
    {"구분": "외부", "세부유형": "외부", "이름": "조재원", "URL": "https://youtube.com/channel/UC2o_y872S6YvaO1K8EYnoxg", "추천제품": "쏙쉐이크", "아이디어": "동금여사님 먹방"},
    {"구분": "외부", "세부유형": "외부", "이름": "송대익", "URL": "https://youtube.com/channel/UCreFV1bKkKE6ufPtd5XeEJw", "추천제품": "쏙쉐이크", "아이디어": "자취 생활 노출"},
    {"구분": "외부", "세부유형": "외부", "이름": "엄지렐라", "URL": "https://youtube.com/channel/UCLXafJ8yYXeUN_eHai-6Pgw", "추천제품": "어퍼 체크셔츠", "아이디어": "엄지훈 캐릭터 활용"},
    {"구분": "외부", "세부유형": "외부", "이름": "숏박스", "URL": "https://youtube.com/channel/UC1B6SalAoiJD7eHfMUA9QrA", "추천제품": "어퍼 볼캡", "아이디어": "스케치코미디 연출"},
    {"구분": "외부", "세부유형": "외부", "이름": "김선태", "URL": "https://youtube.com/channel/UCt-BApVtJGrvF5pCgbiNVeg", "추천제품": "쏙쉐이크 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "하루의하루", "URL": "https://youtube.com/channel/UCpQxvEhfR60LR4s7PV48qIw", "추천제품": "솔브 멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "찰스엔터", "URL": "https://youtube.com/channel/UCCZ-gBdN59pF39tbm16xvdQ", "추천제품": "쏙쉐이크", "아이디어": "브이로그 출연"},
    {"구분": "외부", "세부유형": "외부", "이름": "침착맨", "URL": "https://youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ", "추천제품": "쏙쉐이크 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "랄랄", "URL": "https://youtube.com/channel/UCEX1cZB5TL7jyKejXdTXCKA", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "오늘의 주우재", "URL": "https://youtube.com/channel/UCw-kXdzxMdMdLNI0ZlFFbmA", "추천제품": "어퍼 볼캡", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "자유부인 한가인", "URL": "https://youtube.com/channel/UCvnVUhn95YfQazC_bc2lU6w", "추천제품": "솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "핫이슈지", "URL": "https://youtube.com/channel/UCdMeT09aEFDCH0NghWV41HQ", "추천제품": "솔브 멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "주둥이방송", "URL": "https://youtube.com/channel/UC9ta639M37zzWKwo7kKc80A", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "RISABAE", "URL": "https://youtube.com/channel/UC9kmlDcqksaOnCkC_qzGacA", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "고기남자", "URL": "https://youtube.com/channel/UCT3CumbFIJiW33uq0UI3zlg", "추천제품": "쏙쉐이크", "아이디어": "먹방 후 관리"},
    {"구분": "외부", "세부유형": "외부", "이름": "사내뷰공업", "URL": "https://youtube.com/channel/UCeS6R89S32mSOxTNoEqrN7g", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "쓰까르", "URL": "https://youtube.com/channel/UCX14ZlyF0-tgVcDxLj-4ytA", "추천제품": "멜브 쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "융덕", "URL": "https://youtube.com/channel/UC_zXObQdOXbUGe8IyVRcpSw", "추천제품": "멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "우정잉", "URL": "https://youtube.com/channel/UCW945UjEs6Jm3rVNvPEALdg", "추천제품": "멜브 쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "망구 MANGOO", "URL": "https://youtube.com/channel/UCII-TCayU-6gkfzfgJKsFZw", "추천제품": "멜브 쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "시네 si-ne", "URL": "https://youtube.com/channel/UC0-yyrDjTJ1YFzmV12vEp0Q", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "와코", "URL": "https://youtube.com/channel/UC8NmKAjUM0K4TZqNgboNEWA", "추천제품": "솔브 쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "연두콩", "URL": "https://youtube.com/channel/UCAUbDYDwV34yk6pYiZg_CzA", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "젼언니", "URL": "https://youtube.com/channel/UCyar0OYt0LoPzkkWcQAo6OA", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "지원", "URL": "https://youtube.com/channel/UCURnLWTrLZVv_KiVaeZakog", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "아인이놀아주기", "URL": "https://youtube.com/channel/UCKbsO2vQ9artnn2P-HLnYgQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "민와와", "URL": "https://youtube.com/channel/UCJt-9Ku_D1Un6brccoTzglg", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "보현", "URL": "https://youtube.com/channel/UCZkNETnsbFXG8h7RPQyBtNw", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "민가든", "URL": "https://youtube.com/channel/UCr_QBNzvSm_a7mreIpTregw", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "모르는지", "URL": "https://youtube.com/channel/UCDITZg2t7QPjwx_CYFmP_aw", "추천제품": "쏙쉐이크 멜브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "최종시안", "URL": "https://youtube.com/channel/UC_1ETgrcrLjHOP0YJmkWLVQ", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "진짜팥", "URL": "https://youtube.com/channel/UCLiiqZrEaA2nvDNC4v9Noiw", "추천제품": "솔브 쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "이리유", "URL": "https://youtube.com/channel/UCRFh2MoRiD-whPn0QuOzMFQ", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "기몌민", "URL": "https://youtube.com/channel/UC78welXHRpNJJfiB2zg5BSQ", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "홍또기", "URL": "https://youtube.com/channel/UCsjNYWQvbzb_4z4t_sL1y6w", "추천제품": "어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "람누끼", "URL": "https://youtube.com/channel/UC8fizCcGKHfrQKfvGtFiOiw", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "유플라", "URL": "https://youtube.com/channel/UCxlqra6Gb7BvpOaZaqD-duQ", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "허진희여사", "URL": "https://youtube.com/channel/UCsK4opmMoeLsRsZU54ghvtQ", "추천제품": "멜브 립타투", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "냥이아빠", "URL": "https://youtube.com/channel/UC5AAf4_zZxk-mCl46TogZQQ", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "외부", "이름": "김민지", "URL": "https://youtube.com/channel/UCB9jzo97ZxA5Kl6JDfX0UPw", "추천제품": "멜브 립타투", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "김크리스탈", "URL": "https://youtube.com/channel/UCcNYkzLMSkSiYaiAYjUNzRg", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "다인이공", "URL": "https://youtube.com/channel/UCs7Bw5CQK82AHhyMQ59NZWA", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "외부", "세부유형": "기동", "이름": "김밍 KIMMING", "URL": "https://youtube.com/channel/UCTjwlF8Y8hxR85JPUoZv-6A", "추천제품": "멜브 솔브 어퍼", "아이디어": "-"}
]

# [3] 벤더사 데이터 (10명)
vendor_data = [
    {"분류": "1억 이상", "이름": "한스스타일", "URL": "https://www.instagram.com/hansstyle_hanna/", "추천제품": "솔브"},
    {"분류": "1억 이상", "이름": "11AM", "URL": "https://www.instagram.com/he11o_yeojin/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "강지혜", "URL": "https://www.instagram.com/hairstyle_jihye/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "츄니토리", "URL": "https://www.instagram.com/chunytory/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "헤이가가", "URL": "https://www.instagram.com/hey_gaga_/", "추천제품": "솔브"},
    {"분류": "4,000~7,000만 평균", "이름": "뚜뜨", "URL": "https://www.instagram.com/mintoute_/", "추천제품": "쏙쉐이크"},
    {"분류": "4,000~7,000만 평균", "이름": "아뜨와지효", "URL": "https://www.instagram.com/atoi_jihyo/", "추천제품": "솔브"},
    {"분류": "3,000~5,000만 평균", "이름": "엔젤루밍", "URL": "https://www.instagram.com/ryu_angel/", "추천제품": "솔브 모델링팩"},
    {"분류": "3,000~5,000만 평균", "이름": "캘러리아", "URL": "https://www.instagram.com/hyo_kate_olivia/", "추천제품": "립타투 미스트"},
    {"분류": "3,000~5,000만 평균", "이름": "리미샵", "URL": "https://www.instagram.com/limi_unni/", "추천제품": "솔브"}
]

# [4] 소속사 데이터 (13명)
agency_data = [
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "linakeemz", "URL": "https://www.instagram.com/linakeemz/", "구독자": "119,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "1__xixx", "URL": "https://www.instagram.com/1__xixx/", "구독자": "43,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "lee_dan2", "URL": "https://www.instagram.com/lee_dan2/", "구독자": "157,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "from.suason", "URL": "https://www.instagram.com/from.suason/", "구독자": "152,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "ziyoo_days", "URL": "https://www.instagram.com/ziyoo_days/", "구독자": "50,000", "단가": "2,080,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "alisswlle", "URL": "https://www.instagram.com/alisswlle/", "구독자": "74,000", "단가": "1,950,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "릴스", "이름": "s0la._.c", "URL": "https://www.instagram.com/s0la._.c/", "구독자": "54,000", "단가": "1,300,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "쇼츠", "이름": "무찌", "URL": "https://www.youtube.com/@muzzi_youtube", "구독자": "179,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "쇼츠", "이름": "히루히루 HeeRu", "URL": "https://www.youtube.com/@heeruheeru", "구독자": "127,000", "단가": "2,600,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "쇼츠", "이름": "채울렛chaeullet", "URL": "https://www.youtube.com/@chaeullet", "구독자": "87,800", "단가": "1,950,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "쇼츠", "이름": "후Hoo", "URL": "https://www.youtube.com/@Hoo_short", "구독자": "53,200", "단가": "1,300,000", "비고": "RS 30%"},
    {"소속": "샌드박스", "플랫폼": "쇼츠", "이름": "송타민", "URL": "https://www.youtube.com/@songtamin", "구독자": "20,800", "단가": "910,000", "비고": "RS 30% / 손익 290만"},
    {"소속": "트레져헌터", "플랫폼": "유튜브", "이름": "버터와여름이네", "URL": "https://www.youtube.com/@butterfamilyS", "구독자": "22.96만", "단가": "RS 30%", "비고": "솔브 전달완료"}
]

# ==========================================
# 3. 데이터 통합 및 번호 부여 함수
# ==========================================
def get_unified_df():
    # 1. 자사/외부
    df_our = pd.DataFrame(yt_data_our).copy()
    df_ext = pd.DataFrame(yt_data_ext).copy()
    df_yt = pd.concat([df_our, df_ext], ignore_index=True)
    df_yt['상세 정보'] = df_yt['아이디어'].fillna('-')
    
    # 2. 벤더사
    df_vn = pd.DataFrame(vendor_data).copy()
    df_vn['구분'] = '벤더사'
    df_vn = df_vn.rename(columns={'분류': '세부유형'})
    df_vn['추천제품'] = df_vn['추천제품'].fillna('-')
    df_vn['상세 정보'] = "인스타그램 공동구매 추진"
    
    # 3. 소속사 (단가/구독자 통합)
    df_ag = pd.DataFrame(agency_data).copy()
    df_ag = df_ag.rename(columns={'소속': '구분', '플랫폼': '세부유형'})
    df_ag['추천제품'] = '솔브/멜브'
    df_ag['상세 정보'] = df_ag.apply(lambda x: f"구독자: {x.get('구독자','-')} / 단가: {x.get('단가','-')} ({x.get('비고','-')})", axis=1)

    # 4. 전체 합치기 (필요한 열 규격화)
    cols = ['구분', '세부유형', '이름', 'URL', '추천제품', '상세 정보']
    df_combined = pd.concat([df_yt[cols], df_vn[cols], df_ag[cols]], ignore_index=True)
    
    # ⭐ [번호] 열 맨 앞에 삽입 (지서님 요청!)
    if '번호' not in df_combined.columns:
        df_combined.insert(0, '번호', range(1, len(df_combined) + 1))
    
    # 세션 상태 활용
    if 'confirmation_db' not in st.session_state:
        df_combined['컨펌상태'] = '대기'
        st.session_state.confirmation_db = df_combined
    elif len(st.session_state.confirmation_db) != len(df_combined):
        df_combined['컨펌상태'] = '대기'
        st.session_state.confirmation_db = df_combined
    
    return st.session_state.confirmation_db

# ==========================================
# 4. 이미지 및 갤러리 로직
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "profile_cache.json")

def load_cache():
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w", encoding='utf-8') as f: json.dump({}, f)
        return {}
    with open(CACHE_FILE, "r", encoding='utf-8') as f: return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding='utf-8') as f: json.dump(cache, f, ensure_ascii=False, indent=4)

if 'img_cache' not in st.session_state: st.session_state.img_cache = load_cache()

def get_yt_profile_pic(url, api_key):
    if url in st.session_state.img_cache: return st.session_state.img_cache[url]
    if not api_key or "instagram" in url or "youtube" not in url: 
        return "https://via.placeholder.com/300x300.png?text=Glowuprizz"
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

def draw_gallery(df_subset):
    """모든 명단을 갤러리 카드로 보여주는 함수"""
    df_clean = df_subset.reset_index(drop=True)
    cols = st.columns(4)
    for i, row in df_clean.iterrows():
        with cols[i % 4]:
            with st.container(border=True):
                pic_url = get_yt_profile_pic(row['URL'], yt_key)
                st.markdown(f'<div style="width: 100%; aspect-ratio: 1/1; overflow: hidden; border-radius: 8px; margin-bottom: 10px;"><img src="{pic_url}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                st.subheader(row['이름'])
                st.caption(f"{row.get('구분', '인플루언서')} | {row.get('세부유형', row.get('분류', row.get('플랫폼', '')))}")
                st.markdown(f"**🎯 추천:** {row.get('추천제품', '-')}")
                with st.expander("💡 상세 정보"):
                    # 아이디어 혹은 상세 정보 표시
                    content = row.get('아이디어', row.get('상세 정보', '내용 없음'))
                    st.write(content if content else "내용 없음")
                if row['URL'] != '-': st.link_button("링크 이동", row['URL'], use_container_width=True)

# ==========================================
# 5. 화면 탭 구성
# ==========================================
tabs = st.tabs(["📊 통합 컨펌", "🏢 자사", "🌍 외부", "🤝 벤더사", "🏢 소속사"])

with tabs[0]:
    st.header("📋 전체 리스트 통합 컨펌")
    st.markdown("##### 1. 컨펌 상태 변경 ➜ 2. 구글 시트 저장 버튼 클릭")
    unified_df = get_unified_df()
    edited_df = st.data_editor(
        unified_df,
        column_config={
            "번호": st.column_config.NumberColumn("No.", width="small", disabled=True),
            "URL": st.column_config.LinkColumn("링크"),
            "컨펌상태": st.column_config.SelectboxColumn("결정", options=["대기", "승인 ✅", "반려 ❌"])
        },
        use_container_width=True, hide_index=True
    )
    if st.button("💾 구글 시트에 컨펌 결과 저장하기"):
        if conn:
            try:
                # 시트 탭 이름이 'Sheet1'이 맞는지 꼭 확인하세요!
                conn.update(worksheet="Sheet1", data=edited_df)
                st.success("✅ 구글 시트 저장 완료!")
            except Exception as e:
                st.error(f"❌ 저장 실패 원인: {e}")
        else:
            st.error("구글 시트 연결이 안 되어있습니다.")

with tabs[1]:
    st.header("🏢 자사 크리에이터")
    df_our = pd.DataFrame(yt_data_our)
    for sub in ["전속", "파트너십", "프로젝트 협업"]:
        st.subheader(f"💎 {sub}")
        draw_gallery(df_our[df_our['세부유형']==sub])
        st.divider()

with tabs[2]:
    st.header("🌍 외부 크리에이터")
    draw_gallery(pd.DataFrame(yt_data_ext))

with tabs[3]:
    st.header("🤝 벤더사 (Instagram)")
    draw_gallery(pd.DataFrame(vendor_data).assign(구분='벤더사'))

with tabs[4]:
    st.header("🏢 소속사 협업 리스트")
    st.info("**📞 담당자:** 샌드박스 허현지님 / 트레져헌터 박예은 매니저님")
    # 소속사 데이터 갤러리용으로 가공
    df_agency_gal = pd.DataFrame(agency_data).rename(columns={'소속':'구분', '플랫폼':'세부유형'})
    df_agency_gal['아이디어'] = df_agency_gal.apply(lambda x: f"구독자: {x['구독자']} / 단가: {x['단가']} / {x['비고']}", axis=1)
    draw_gallery(df_agency_gal)
