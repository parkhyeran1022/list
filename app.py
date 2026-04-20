import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from streamlit_gsheets import GSheetsConnection
import json
import os
from datetime import datetime

# ==========================================
# 1. 페이지 설정 및 보안 로드
# ==========================================
st.set_page_config(page_title="Glowuprizz PB Dashboard", page_icon="🚀", layout="wide")
st.title("🚀 인플루언서 데이터 통합 시스템 (v5.0)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1rstN-Wpgen0gua78qI4lkt0OZhISw6pwLR8yJgR7G1s/edit?gid=0#gid=0"
yt_key = st.secrets.get("YOUTUBE_KEY", "")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# ==========================================
# 2. 캐싱 및 유튜브 통계 로직 (롱폼 10개 기준)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "profile_cache_v5.json")

def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    with open(CACHE_FILE, "r", encoding='utf-8') as f: return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding='utf-8') as f: json.dump(cache, f, ensure_ascii=False)

if 'full_cache' not in st.session_state:
    st.session_state.full_cache = load_cache()

def get_yt_stats_and_pic(url, api_key):
    """최근 10개 롱폼 평균 조회수, ER, 프로필 사진 획득"""
    if url in st.session_state.full_cache:
        return st.session_state.full_cache[url]
    
    default_res = {"pic": "https://via.placeholder.com/300x300.png?text=Glowuprizz", "views": 0, "er": 0.0}
    if not api_key or "youtube" not in url: return default_res
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        # 1. 채널 ID 획득
        if '/channel/' in url: c_id = url.split('/channel/')[1].split('/')[0].split('?')[0]
        elif '@' in url:
            res = youtube.search().list(part="snippet", q='@'+url.split('@')[1].split('/')[0], type="channel", maxResults=1).execute()
            c_id = res['items'][0]['snippet']['channelId']
        else: return default_res
        
        # 2. 채널 정보(프사) 획득
        c_res = youtube.channels().list(part="snippet,contentDetails", id=c_id).execute()
        pic = c_res['items'][0]['snippet']['thumbnails']['medium']['url']
        uploads_playlist_id = c_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 3. 최신 영상 20개 가져와서 롱폼(Shorts 제외) 10개 필터링
        v_res = youtube.playlistItems().list(part="contentDetails", playlistId=uploads_playlist_id, maxResults=20).execute()
        video_ids = [item['contentDetails']['videoId'] for item in v_res['items']]
        
        # 영상 상세 정보(길이, 통계) 조회
        v_details = youtube.videos().list(part="contentDetails,statistics", id=','.join(video_ids)).execute()
        
        long_form_stats = []
        for v in v_details['items']:
            duration = v['contentDetails']['duration'] # PT1M30S 형태
            if 'M' in duration or 'H' in duration: # 1분 이상인 경우만 포함
                views = int(v['statistics'].get('viewCount', 0))
                likes = int(v['statistics'].get('likeCount', 0))
                comments = int(v['statistics'].get('commentCount', 0))
                er = ((likes + comments) / views * 100) if views > 0 else 0
                long_form_stats.append({'views': views, 'er': er})
            if len(long_form_stats) >= 10: break
            
        avg_views = int(sum(d['views'] for d in long_form_stats) / len(long_form_stats)) if long_form_stats else 0
        avg_er = sum(d['er'] for d in long_form_stats) / len(long_form_stats) if long_form_stats else 0.0
        
        res_data = {"pic": pic, "views": avg_views, "er": round(avg_er, 2)}
        st.session_state.full_cache[url] = res_data
        save_cache(st.session_state.full_cache)
        return res_data
    except:
        return default_res

# ==========================================
# 3. 마스터 데이터 (누락 0% - 84명 전체)
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
    {"구분": "자사", "세부유형": "파트너십", "이름": "비타민신지니", "URL": "https://youtube.com/channel/UC9trbyGOOjJmMea3w6c-e2A", "추천제품": "솔브 괄사크림", "아이디어": "마사지 시연"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "잡식맨", "URL": "https://youtube.com/channel/UCVILvX9vIp-vMFGmCYJtG3A", "추천제품": "쏙쉐이크", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "아이뽀 i4", "URL": "https://youtube.com/channel/UC6jtibPJUrtufKBZCm6gbIg", "추천제품": "멜브 솔브", "아이디어": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "대생이", "URL": "https://youtube.com/channel/UChE5nZAIhWS5vYTRjsUgRpQ", "추천제품": "어퍼 체크셔츠", "아이디어": "-"},
    
    # --- 외부 (43명) ---
    {"구분": "외부", "세부유형": "외부", "이름": "조재원", "URL": "https://youtube.com/channel/UC2o_y872S6YvaO1K8EYnoxg", "추천제품": "쏙쉐이크", "아이디어": "동금여사님 먹방"},
    {"구분": "외부", "세부유형": "외부", "이름": "송대익", "URL": "https://youtube.com/channel/UCreFV1bKkKE6ufPtd5XeEJw", "추천제품": "쏙쉐이크", "아이디어": "자취 생활 노출"},
    {"구분": "외부", "세부유형": "외부", "이름": "엄지렐라", "URL": "https://youtube.com/channel/UCLXafJ8yYXeUN_eHai-6Pgw", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "숏박스", "URL": "https://youtube.com/channel/UC1B6SalAoiJD7eHfMUA9QrA", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "김선태", "URL": "https://youtube.com/channel/UCt-BApVtJGrvF5pCgbiNVeg", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "하루의하루", "URL": "https://youtube.com/channel/UCpQxvEhfR60LR4s7PV48qIw", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "찰스엔터", "URL": "https://youtube.com/channel/UCCZ-gBdN59pF39tbm16xvdQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "침착맨", "URL": "https://youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "랄랄", "URL": "https://youtube.com/channel/UCEX1cZB5TL7jyKejXdTXCKA", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "오늘의 주우재", "URL": "https://youtube.com/channel/UCw-kXdzxMdMdLNI0ZlFFbmA", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "자유부인 한가인", "URL": "https://youtube.com/channel/UCvnVUhn95YfQazC_bc2lU6w", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "핫이슈지", "URL": "https://youtube.com/channel/UCdMeT09aEFDCH0NghWV41HQ", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "주둥이방송", "URL": "https://youtube.com/channel/UC9ta639M37zzWKwo7kKc80A", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "RISABAE", "URL": "https://youtube.com/channel/UC9kmlDcqksaOnCkC_qzGacA", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "고기남자", "URL": "https://youtube.com/channel/UCT3CumbFIJiW33uq0UI3zlg", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "사내뷰공업", "URL": "https://youtube.com/channel/UCeS6R89S32mSOxTNoEqrN7g", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "쓰까르", "URL": "https://youtube.com/channel/UCX14ZlyF0-tgVcDxLj-4ytA", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "융덕", "URL": "https://youtube.com/channel/UC_zXObQdOXbUGe8IyVRcpSw", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "우정잉", "URL": "https://youtube.com/channel/UCW945UjEs6Jm3rVNvPEALdg", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "망구", "URL": "https://youtube.com/channel/UCII-TCayU-6gkfzfgJKsFZw", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "시네", "URL": "https://youtube.com/channel/UC0-yyrDjTJ1YFzmV12vEp0Q", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "와코", "URL": "https://youtube.com/channel/UC8NmKAjUM0K4TZqNgboNEWA", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "연두콩", "URL": "https://youtube.com/channel/UCAUbDYDwV34yk6pYiZg_CzA", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "젼언니", "URL": "https://youtube.com/channel/UCyar0OYt0LoPzkkWcQAo6OA", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "지원", "URL": "https://youtube.com/channel/UCURnLWTrLZVv_KiVaeZakog", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "아인이놀아주기", "URL": "https://youtube.com/channel/UCKbsO2vQ9artnn2P-HLnYgQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민와와", "URL": "https://youtube.com/channel/UCJt-9Ku_D1Un6brccoTzglg", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "보현", "URL": "https://youtube.com/channel/UCZkNETnsbFXG8h7RPQyBtNw", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민가든", "URL": "https://youtube.com/channel/UCr_QBNzvSm_a7mreIpTregw", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "모르는지", "URL": "https://youtube.com/channel/UCDITZg2t7QPjwx_CYFmP_aw", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "최종시안", "URL": "https://youtube.com/channel/UC_1ETgrcrLjHOP0YJmkWLVQ", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "진짜팥", "URL": "https://youtube.com/channel/UCLiiqZrEaA2nvDNC4v9Noiw", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "이리유", "URL": "https://youtube.com/channel/UCRFh2MoRiD-whPn0QuOzMFQ", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "기몌민", "URL": "https://youtube.com/channel/UC78welXHRpNJJfiB2zg5BSQ", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "홍또기", "URL": "https://youtube.com/channel/UCsjNYWQvbzb_4z4t_sL1y6w", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "람누끼", "URL": "https://youtube.com/channel/UC8fizCcGKHfrQKfvGtFiOiw", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "유플라", "URL": "https://youtube.com/channel/UCxlqra6Gb7BvpOaZaqD-duQ", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "허진희여사", "URL": "https://youtube.com/channel/UCsK4opmMoeLsRsZU54ghvtQ", "추천제품": "립타투", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "냥이아빠", "URL": "https://youtube.com/channel/UC5AAf4_zZxk-mCl46TogZQQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "김민지", "URL": "https://youtube.com/channel/UCB9jzo97ZxA5Kl6JDfX0UPw", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "김크리스탈", "URL": "https://youtube.com/channel/UCcNYkzLMSkSiYaiAYjUNzRg", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "다인이공", "URL": "https://youtube.com/channel/UCs7Bw5CQK82AHhyMQ59NZWA", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "김밍", "URL": "https://youtube.com/channel/UCTjwlF8Y8hxR85JPUoZv-6A", "추천제품": "멜브", "아이디어": ""},

    # --- 벤더사 (10명) ---
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "한스스타일", "URL": "https://www.instagram.com/hansstyle_hanna/", "추천제품": "솔브", "상세 정보": "인스타 공구"},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "11AM", "URL": "https://www.instagram.com/he11o_yeojin/", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "강지혜", "URL": "https://www.instagram.com/hairstyle_jihye/", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "츄니토리", "URL": "https://www.instagram.com/chunytory/", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "헤이가가", "URL": "https://www.instagram.com/hey_gaga_/", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "뚜뜨", "URL": "https://www.instagram.com/mintoute_/", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "아뜨와지효", "URL": "https://www.instagram.com/atoi_jihyo/", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "엔젤루밍", "URL": "https://www.instagram.com/ryu_angel/", "추천제품": "모델링팩", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "캘러리아", "URL": "https://www.instagram.com/hyo_kate_olivia/", "추천제품": "미스트", "상세 정보": ""},
    {"구분": "벤더사", "세부유형": "공구팀", "이름": "리미샵", "URL": "https://www.instagram.com/limi_unni/", "추천제품": "솔브", "상세 정보": ""},

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
# 3. 데이터 로드 및 시트 동기화 (ER/조회수 포함)
# ==========================================
def load_and_sync_data():
    master_df = pd.DataFrame(raw_data)
    
    # 기본 통계값 컬럼 생성
    master_df['평균조회수'] = 0
    master_df['ER'] = 0.0
    
    # 구글 시트 기존 상태 불러오기
    if conn:
        try:
            sheet_df = conn.read(worksheet="Sheet1")
            if not sheet_df.empty and '이름' in sheet_df.columns:
                status_map = dict(zip(sheet_df['이름'], sheet_df['컨펌상태']))
                master_df['컨펌상태'] = master_df['이름'].map(status_map).fillna('대기')
            else: master_df['컨펌상태'] = '대기'
        except: master_df['컨펌상태'] = '대기'
    else: master_df['컨펌상태'] = '대기'

    # 실시간 유튜브 데이터 업데이트 (자사 제외 외부만)
    for idx, row in master_df.iterrows():
        if row['구분'] == '외부' and 'youtube' in row['URL']:
            stats = get_yt_stats_and_pic(row['URL'], yt_key)
            master_df.at[idx, '평균조회수'] = stats['views']
            master_df.at[idx, 'ER'] = stats['er']
        elif row['구분'] == '자사':
            master_df.at[idx, '평균조회수'] = 0
            master_df.at[idx, 'ER'] = 0.0

    # 번호 부여 및 열 순서 재배치 (요청사항 반영)
    # 순서: 번호, 구분, 세부유형, 이름, 평균조회수, ER, 상세 정보, 추천제품, URL, 컨펌상태
    master_df.insert(0, '번호', range(1, len(master_df) + 1))
    cols_order = ['번호', '구분', '세부유형', '이름', '평균조회수', 'ER', '상세 정보', '추천제품', 'URL', '컨펌상태']
    return master_df[cols_order]

if 'df_master' not in st.session_state:
    with st.spinner("유튜브 실시간 통계를 분석하는 중입니다... 잠시만 기다려주세요."):
        st.session_state.df_master = load_and_sync_data()

# ==========================================
# 4. 개별 컨펌 및 일괄 처리 로직
# ==========================================
def _apply_bulk_status(target_df, new_status):
    updated = False
    for idx in target_df.index:
        chk_key = f"chk_{idx}"
        if st.session_state.get(chk_key, False):
            st.session_state.df_master.at[idx, '컨펌상태'] = new_status
            st.session_state[chk_key] = False
            updated = True
    if updated:
        if conn:
            try:
                conn.update(worksheet="Sheet1", data=st.session_state.df_master)
                st.success("✅ 구글 시트에 즉시 반영되었습니다!")
            except: st.error("시트 저장 실패")
        st.rerun()

def bulk_action_ui(target_df, title):
    st.subheader(title)
    c1, c2, c3, c4, _ = st.columns([1.5, 1.5, 1.5, 1.5, 4])
    with c1: 
        if st.button("☑️ 선택 승인", key=f"bulk_app_{title}"): _apply_bulk_status(target_df, "승인 ✅")
    with c2: 
        if st.button("☑️ 선택 반려", key=f"bulk_rej_{title}"): _apply_bulk_status(target_df, "반려 ❌")
    with c3: 
        if st.button("☑️ 선택 보류", key=f"bulk_wait_{title}"): _apply_bulk_status(target_df, "보류 ⏳")

def draw_gallery_with_confirm(df_subset, num_cols=8):
    # 정렬 로직: 평균조회수 기준 내림차순
    df_clean = df_subset.sort_values('평균조회수', ascending=False).reset_index(drop=True)
    cols = st.columns(num_cols)
    options = ["대기", "승인 ✅", "반려 ❌", "보류 ⏳"]
    
    for i, row in df_clean.iterrows():
        # 원본 인덱스 찾기
        idx = st.session_state.df_master[st.session_state.df_master['이름'] == row['이름']].index[0]
        
        with cols[i % num_cols]:
            with st.container(border=True):
                c_chk, c_sel = st.columns([1, 2.5])
                with c_chk: st.checkbox("S", key=f"chk_{idx}", label_visibility="collapsed")
                with c_sel:
                    cur_st = st.session_state.df_master.at[idx, '컨펌상태']
                    new_st = st.selectbox("S", options, index=options.index(cur_st) if cur_st in options else 0, key=f"sel_{idx}", label_visibility="collapsed")
                    if new_st != cur_st:
                        st.session_state.df_master.at[idx, '컨펌상태'] = new_st
                
                stats = get_yt_profile_pic(row['URL'], yt_key) if isinstance(stats := get_yt_stats_and_pic(row['URL'], yt_key), dict) else {"pic":""}
                st.markdown(f'<div style="width: 100%; aspect-ratio: 1/1; overflow: hidden; border-radius: 6px; margin-bottom: 5px;"><img src="{stats.get("pic")}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                
                # 프사 밑에 통계 정보 표시
                st.markdown(f"**{row['이름']}**")
                if row['구분'] == '외부':
                    st.markdown(f"<p style='margin:0; font-size:12px; color:blue;'>📈 {row['평균조회수']:,}회 / ER {row['ER']}%</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='margin:0; font-size:12px; color:gray;'>📈 - / -</p>", unsafe_allow_html=True)
                
                st.caption(f"{row['세부유형']}")
                with st.expander("📝"): st.write(row['상세 정보'])
                if row['URL'] != '-': st.link_button("🔗", row['URL'], use_container_width=True)

# ==========================================
# 5. 화면 구성
# ==========================================
tab0, tab1, tab2, tab3, tab4 = st.tabs(["📊 통합 컨펌", "🏢 자사", "🌍 외부", "🤝 벤더사", "🏢 소속사"])

with tab0:
    st.header("📋 전체 리스트 통합 컨펌")
    # 컬럼 설정 (순서 및 링크 열기)
    edited_df = st.data_editor(
        st.session_state.df_master,
        column_config={
            "번호": st.column_config.NumberColumn("No.", width="small", disabled=True),
            "평균조회수": st.column_config.NumberColumn("평균조회수", format="%d회"),
            "ER": st.column_config.NumberColumn("ER", format="%.2f%%"),
            "URL": st.column_config.LinkColumn("링크"),
            "컨펌상태": st.column_config.SelectboxColumn("결정", options=["대기", "승인 ✅", "반려 ❌", "보류 ⏳"])
        },
        use_container_width=True, hide_index=True, key="main_editor"
    )
    st.session_state.df_master = edited_df
    
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("💾 구글 시트 저장", type="primary"):
            if conn:
                try:
                    conn.update(worksheet="Sheet1", data=st.session_state.df_master)
                    st.success("✅ 저장 성공!")
                except Exception as e: st.error(f"실패: {e}")
    with c2: st.link_button("📂 구글 시트 바로가기", SHEET_URL)

with tab1:
    df_our = st.session_state.df_master[st.session_state.df_master['구분']=='자사']
    bulk_action_ui(df_our, "자사 리스트")
    c_s1, _ = st.columns([1, 3])
    num_our = c_s1.slider("가로 배치", 2, 8, 8, key="s_our")
    for sub in ["전속", "파트너십", "프로젝트 협업"]:
        st.markdown(f"##### 💎 {sub}")
        draw_gallery_with_confirm(df_our[df_our['세부유형']==sub], num_cols=num_our)

with tab2:
    df_ext = st.session_state.df_master[st.session_state.df_master['구분']=='외부']
    bulk_action_ui(df_ext, "외부 리스트 (조회수순 정렬)")
    c_s2, _ = st.columns([1, 3])
    num_ext = c_s2.slider("가로 배치", 2, 8, 8, key="s_ext")
    draw_gallery_with_confirm(df_ext, num_cols=num_ext)

with tab3:
    st.header("🤝 벤더사 리스트")
    df_vn = st.session_state.df_master[st.session_state.df_master['구분']=='벤더사']
    st.dataframe(df_vn, use_container_width=True, hide_index=True, column_config={"URL": st.column_config.LinkColumn("인스타")})

with tab4:
    st.header("🏢 소속사 리스트")
    # 담당자 연락처 100% 복구
    st.info("**📞 담당자 연락처**\n\n* **샌드박스:** AD2 l BD l 허현지님 (hjhuh@sandbox.co.kr)\n* **트레져헌터:** 숏폼사업팀 박예은 매니저님 (yeeun_p@treasurehunter.co.kr)")
    df_ag = st.session_state.df_master[st.session_state.df_master['구분'].isin(['샌드박스', '트레져헌터'])]
    st.dataframe(df_ag, use_container_width=True, hide_index=True, column_config={"URL": st.column_config.LinkColumn("채널")})
