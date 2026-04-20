import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from streamlit_gsheets import GSheetsConnection
import json
import os

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="Glowuprizz PB Dashboard", page_icon="🚀", layout="wide")
st.title("🚀 인플루언서 컨펌 리스트")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1rstN-Wpgen0gua78qI4lkt0OZhISw6pwLR8yJgR7G1s/edit?gid=0#gid=0"
yt_key = st.secrets.get("YOUTUBE_KEY", "")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# ==========================================
# 2. 실시간 유튜브 API (롱폼/쇼츠 구분 분석)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_yt_data(url, api_key, is_shorts=False):
    res = {"pic": "https://via.placeholder.com/300x300.png?text=Glowuprizz", "views": 0, "er": 0.0}
    if not api_key or "youtube" not in url: return res
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        if '/channel/' in url: c_id = url.split('/channel/')[1].split('/')[0].split('?')[0]
        elif '@' in url:
            handle = '@' + url.split('@')[1].split('/')[0].split('?')[0]
            search_res = youtube.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
            c_id = search_res['items'][0]['snippet']['channelId']
        else: return res

        c_res = youtube.channels().list(part="snippet,contentDetails", id=c_id).execute()
        res["pic"] = c_res['items'][0]['snippet']['thumbnails']['medium']['url']
        uploads_id = c_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        v_res = youtube.playlistItems().list(part="contentDetails", playlistId=uploads_id, maxResults=25).execute()
        v_ids = [i['contentDetails']['videoId'] for i in v_res['items']]
        v_details = youtube.videos().list(part="contentDetails,statistics", id=','.join(v_ids)).execute()
        
        target_stats = []
        for v in v_details['items']:
            dur = v['contentDetails']['duration']
            is_long = 'H' in dur or ('M' in dur and dur != 'PT1M')
            
            v_count = int(v['statistics'].get('viewCount', 0))
            l_count = int(v['statistics'].get('likeCount', 0))
            c_count = int(v['statistics'].get('commentCount', 0))
            er_val = ((l_count + c_count) / v_count * 100) if v_count > 0 else 0
            
            if is_shorts and not is_long:
                target_stats.append({'v': v_count, 'e': er_val})
            elif not is_shorts and is_long:
                target_stats.append({'v': v_count, 'e': er_val})
                
            if len(target_stats) >= 10: break
            
        if target_stats:
            res["views"] = int(sum(s['v'] for s in target_stats) / len(target_stats))
            res["er"] = round(sum(s['e'] for s in target_stats) / len(target_stats), 2)
        return res
    except: return res

def fmt_v(v):
    if pd.isna(v) or v == 0: return "-"
    if v >= 10000: return f"{v/10000:.1f}만".replace(".0만", "만")
    return f"{int(v):,}"

# ==========================================
# 3. 0% 누락 전체 리스트 (84명)
# ==========================================
RAW_LIST = [
    # [자사 18명]
    {"구분": "자사", "세부유형": "전속", "이름": "심장에박현서", "URL": "https://youtube.com/channel/UCo4m81FJ-dT8MqijBlhbN2A", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "생각없이사는연", "URL": "https://youtube.com/channel/UCyVEhwFJ1HF66JqjxMkc-Uw", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "예보링", "URL": "https://youtube.com/channel/UCby6TnEm4xha2NIncRxC2EQ", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "미지수", "URL": "https://youtube.com/channel/UC-BS_A5wCxoCp06thW_V8wA", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 부재중", "URL": "https://youtube.com/channel/UC5Ida86tt8QKa4Myw7idxNg", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "매일제히", "URL": "https://youtube.com/channel/UCWWnWFPkfXMIjxNhBu5qVtg", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 여깄음", "URL": "https://youtube.com/channel/UC9kUsuu1Giqa9V855EWa7-A", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "핏블리 FITVELY", "URL": "https://youtube.com/channel/UC3hRpIQ4x5niJDwjajQSVPg", "추천제품": "-", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "전속", "이름": "재넌", "URL": "https://youtube.com/channel/UCem8l1w4OWhkqpoOg1SB4_w", "추천제품": "쏙쉐이크 어퍼볼캡", "상세 정보": "먹방 식단관리 노출"},
    {"구분": "자사", "세부유형": "전속", "이름": "살빼조", "URL": "https://www.youtube.com/@dietjo311", "추천제품": "쏙쉐이크", "상세 정보": "아침 루틴 식사 대용 노출"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "매드브로 MadBros", "URL": "https://youtube.com/channel/UCiTcv_AxQQSx77yGikHHDZw", "추천제품": "볼캡 쏙쉐이크", "상세 정보": "쓰줍맨 활동 시 착용"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "독고독채널", "URL": "https://youtube.com/channel/UCEUSANZNPXY1JsBoqhQIgxQ", "추천제품": "쏙쉐이크", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "김승배", "URL": "https://youtube.com/channel/UCPDiMzJdYb0Q-LxoP7W1j7g", "추천제품": "쏙쉐이크", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "kiu기우쌤", "URL": "https://youtube.com/channel/UCIZ5rCTYJ0s16FgT7OetVEQ", "추천제품": "솔브 모델링팩", "상세 정보": "셀프케어 루틴"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "비타민신지니", "URL": "https://youtube.com/channel/UC9trbyGOOjJmMea3w6c-e2A", "추천제품": "솔브 괄사크림", "상세 정보": "마사지 시연"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "잡식맨", "URL": "https://youtube.com/channel/UCVILvX9vIp-vMFGmCYJtG3A", "추천제품": "쏙쉐이크", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "아이뽀 i4", "URL": "https://youtube.com/channel/UC6jtibPJUrtufKBZCm6gbIg", "추천제품": "멜브 솔브", "상세 정보": "-"},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "대생이", "URL": "https://youtube.com/channel/UChE5nZAIhWS5vYTRjsUgRpQ", "추천제품": "어퍼 체크셔츠", "상세 정보": "-"},
    
    # [외부 43명]
    {"구분": "외부", "세부유형": "외부", "이름": "조재원", "URL": "https://youtube.com/channel/UC2o_y872S6YvaO1K8EYnoxg", "추천제품": "쏙쉐이크", "상세 정보": "동금여사님 먹방"},
    {"구분": "외부", "세부유형": "외부", "이름": "송대익", "URL": "https://youtube.com/channel/UCreFV1bKkKE6ufPtd5XeEJw", "추천제품": "쏙쉐이크", "상세 정보": "자취 생활 노출"},
    {"구분": "외부", "세부유형": "외부", "이름": "엄지렐라", "URL": "https://youtube.com/channel/UCLXafJ8yYXeUN_eHai-6Pgw", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "숏박스", "URL": "https://youtube.com/channel/UC1B6SalAoiJD7eHfMUA9QrA", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "김선태", "URL": "https://youtube.com/channel/UCt-BApVtJGrvF5pCgbiNVeg", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "하루의하루", "URL": "https://youtube.com/channel/UCpQxvEhfR60LR4s7PV48qIw", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "찰스엔터", "URL": "https://youtube.com/channel/UCCZ-gBdN59pF39tbm16xvdQ", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "침착맨", "URL": "https://youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "랄랄", "URL": "https://youtube.com/channel/UCEX1cZB5TL7jyKejXdTXCKA", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "오늘의 주우재", "URL": "https://youtube.com/channel/UCw-kXdzxMdMdLNI0ZlFFbmA", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "자유부인 한가인", "URL": "https://youtube.com/channel/UCvnVUhn95YfQazC_bc2lU6w", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "핫이슈지", "URL": "https://youtube.com/channel/UCdMeT09aEFDCH0NghWV41HQ", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "주둥이방송", "URL": "https://youtube.com/channel/UC9ta639M37zzWKwo7kKc80A", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "RISABAE", "URL": "https://youtube.com/channel/UC9kmlDcqksaOnCkC_qzGacA", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "고기남자", "URL": "https://youtube.com/channel/UCT3CumbFIJiW33uq0UI3zlg", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "사내뷰공업", "URL": "https://youtube.com/channel/UCeS6R89S32mSOxTNoEqrN7g", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "쓰까르", "URL": "https://youtube.com/channel/UCX14ZlyF0-tgVcDxLj-4ytA", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "융덕", "URL": "https://youtube.com/channel/UC_zXObQdOXbUGe8IyVRcpSw", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "우정잉", "URL": "https://youtube.com/channel/UCW945UjEs6Jm3rVNvPEALdg", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "망구", "URL": "https://youtube.com/channel/UCII-TCayU-6gkfzfgJKsFZw", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "시네", "URL": "https://youtube.com/channel/UC0-yyrDjTJ1YFzmV12vEp0Q", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "와코", "URL": "https://youtube.com/channel/UC8NmKAjUM0K4TZqNgboNEWA", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "연두콩", "URL": "https://youtube.com/channel/UCAUbDYDwV34yk6pYiZg_CzA", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "젼언니", "URL": "https://youtube.com/channel/UCyar0OYt0LoPzkkWcQAo6OA", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "지원", "URL": "https://youtube.com/channel/UCURnLWTrLZVv_KiVaeZakog", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "아인이놀아주기", "URL": "https://youtube.com/channel/UCKbsO2vQ9artnn2P-HLnYgQ", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민와와", "URL": "https://youtube.com/channel/UCJt-9Ku_D1Un6brccoTzglg", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "보현", "URL": "https://youtube.com/channel/UCZkNETnsbFXG8h7RPQyBtNw", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민가든", "URL": "https://youtube.com/channel/UCr_QBNzvSm_a7mreIpTregw", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "모르는지", "URL": "https://youtube.com/channel/UCDITZg2t7QPjwx_CYFmP_aw", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "최종시안", "URL": "https://youtube.com/channel/UC_1ETgrcrLjHOP0YJmkWLVQ", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "진짜팥", "URL": "https://youtube.com/channel/UCLiiqZrEaA2nvDNC4v9Noiw", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "이리유", "URL": "https://youtube.com/channel/UCRFh2MoRiD-whPn0QuOzMFQ", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "기몌민", "URL": "https://youtube.com/channel/UC78welXHRpNJJfiB2zg5BSQ", "추천제품": "솔브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "홍또기", "URL": "https://youtube.com/channel/UCsjNYWQvbzb_4z4t_sL1y6w", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "람누끼", "URL": "https://youtube.com/channel/UC8fizCcGKHfrQKfvGtFiOiw", "추천제품": "어퍼", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "유플라", "URL": "https://youtube.com/channel/UCxlqra6Gb7BvpOaZaqD-duQ", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "허진희여사", "URL": "https://youtube.com/channel/UCsK4opmMoeLsRsZU54ghvtQ", "추천제품": "립타투", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "냥이아빠", "URL": "https://youtube.com/channel/UC5AAf4_zZxk-mCl46TogZQQ", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "김민지", "URL": "https://youtube.com/channel/UCB9jzo97ZxA5Kl6JDfX0UPw", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "김크리스탈", "URL": "https://youtube.com/channel/UCcNYkzLMSkSiYaiAYjUNzRg", "추천제품": "멜브", "상세 정보": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "다인이공", "URL": "https://youtube.com/channel/UCs7Bw5CQK82AHhyMQ59NZWA", "추천제품": "쏙쉐이크", "상세 정보": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "김밍", "URL": "https://youtube.com/channel/UCTjwlF8Y8hxR85JPUoZv-6A", "추천제품": "멜브", "상세 정보": ""},
    
    # [벤더 10명]
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
    
    # [소속사 13명]
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "linakeemz", "URL": "https://www.instagram.com/linakeemz/", "추천제품": "솔브", "상세 정보": "11.9만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "1__xixx", "URL": "https://www.instagram.com/1__xixx/", "추천제품": "솔브", "상세 정보": "4.3만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "lee_dan2", "URL": "https://www.instagram.com/lee_dan2/", "추천제품": "솔브", "상세 정보": "15.7만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "from.suason", "URL": "https://www.instagram.com/from.suason/", "추천제품": "솔브", "상세 정보": "15.2만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "ziyoo_days", "URL": "https://www.instagram.com/ziyoo_days/", "추천제품": "솔브", "상세 정보": "5만/208만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "alisswlle", "URL": "https://www.instagram.com/alisswlle/", "추천제품": "솔브", "상세 정보": "7.4만/195만/RS30%"},
    {"구분": "샌드박스", "세부유형": "릴스", "이름": "s0la._.c", "URL": "https://www.instagram.com/s0la._.c/", "추천제품": "솔브", "상세 정보": "5.4만/130만/RS30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "무찌", "URL": "https://www.youtube.com/@muzzi_youtube", "추천제품": "솔브", "상세 정보": "17.9만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "히루히루", "URL": "https://www.youtube.com/@heeruheeru", "추천제품": "솔브", "상세 정보": "12.7만/260만/RS30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "채울렛", "URL": "https://www.youtube.com/@chaeullet", "추천제품": "솔브", "상세 정보": "8.7만/195만/RS30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "후Hoo", "URL": "https://www.youtube.com/@Hoo_short", "추천제품": "솔브", "상세 정보": "5.3만/130만/RS30%"},
    {"구분": "샌드박스", "세부유형": "쇼츠", "이름": "송타민", "URL": "https://www.youtube.com/@songtamin", "추천제품": "솔브", "상세 정보": "2만/91만/RS30%"},
    {"구분": "트레져헌터", "세부유형": "유튜브", "이름": "버터와여름이네", "URL": "https://www.youtube.com/@butterfamilyS", "추천제품": "솔브", "상세 정보": "22.96만/RS30%/전달완료"}
]

# ==========================================
# 4. 데이터 로드, 정렬 및 시트 동기화
# ==========================================
def load_and_sync_data():
    master_df = pd.DataFrame(RAW_LIST)
    master_df['평균조회수'] = 0
    master_df['ER'] = 0.0
    
    if conn:
        try:
            sheet_df = conn.read(worksheet="Sheet1")
            if not sheet_df.empty and '이름' in sheet_df.columns:
                status_map = dict(zip(sheet_df['이름'], sheet_df['컨펌상태']))
                master_df['컨펌상태'] = master_df['이름'].map(status_map).fillna('대기')
            else: master_df['컨펌상태'] = '대기'
        except: master_df['컨펌상태'] = '대기'
    else: master_df['컨펌상태'] = '대기'

    for idx, row in master_df.iterrows():
        if 'youtube' in row['URL']:
            is_shorts = row['구분'] in ['샌드박스', '트레져헌터']
            stats = fetch_yt_data(row['URL'], yt_key, is_shorts=is_shorts)
            master_df.at[idx, '평균조회수'] = stats['views']
            master_df.at[idx, 'ER'] = stats['er']

    master_df['조회수'] = master_df['평균조회수'].apply(fmt_v)
    master_df['ER_표시'] = master_df['ER'].apply(lambda x: f"{x:.2f}%" if x > 0 else "-")

    pinned = ["심장에박현서", "생각없이사는연", "예보링", "미지수", "채널주인 부재중", "매일제히", "채널주인 여깄음", "핏블리 FITVELY"]
    df_pinned = master_df[master_df['이름'].isin(pinned)].copy()
    df_pinned['sort_order'] = df_pinned['이름'].apply(lambda x: pinned.index(x))
    df_pinned = df_pinned.sort_values('sort_order').drop(columns=['sort_order'])
    
    df_others = master_df[~master_df['이름'].isin(pinned)].copy()
    df_others = df_others.sort_values('평균조회수', ascending=False)
    
    final_df = pd.concat([df_pinned, df_others], ignore_index=True)
    final_df.insert(0, '번호', range(1, len(final_df) + 1))
    
    cols = ['번호', '구분', '세부유형', '이름', '조회수', 'ER_표시', '상세 정보', '추천제품', 'URL', '컨펌상태', '평균조회수', 'ER']
    return final_df[cols]

if 'df_master' not in st.session_state:
    with st.spinner("🚀 유튜브 최신 데이터를 분석 중입니다. 잠시만 기다려주세요..."):
        st.session_state.df_master = load_and_sync_data()

# ==========================================
# 5. UI 유틸리티 (일괄 처리 & 갤러리)
# ==========================================
def _apply_bulk(target_df, status):
    count = 0
    for idx in target_df.index:
        if st.session_state.get(f"chk_{idx}", False):
            st.session_state.df_master.at[idx, '컨펌상태'] = status
            st.session_state[f"chk_{idx}"] = False 
            count += 1
    if count > 0:
        if conn:
            try:
                conn.update(worksheet="Sheet1", data=st.session_state.df_master.drop(columns=['평균조회수', 'ER'], errors='ignore'))
                st.success(f"✅ {count}명 상태 업데이트 및 시트 저장 완료!")
            except: pass
        st.rerun()

def draw_gallery_custom(df_subset, num_cols=8):
    if '평균조회수' in df_subset.columns:
        df_clean = df_subset.sort_values('평균조회수', ascending=False).reset_index(drop=True)
    else: df_clean = df_subset.reset_index(drop=True)
        
    cols = st.columns(num_cols)
    opts = ["대기", "승인 ✅", "반려 ❌", "보류 ⏳"]
    
    for i, row in df_clean.iterrows():
        master_idx = st.session_state.df_master[st.session_state.df_master['이름'] == row['이름']].index[0]
        
        with cols[i % num_cols]:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                with c1: st.checkbox("S", key=f"chk_{master_idx}", label_visibility="collapsed")
                with c2:
                    cur = st.session_state.df_master.at[master_idx, '컨펌상태']
                    new = st.selectbox("S", opts, index=opts.index(cur) if cur in opts else 0, key=f"sel_{master_idx}", label_visibility="collapsed")
                    if new != cur: st.session_state.df_master.at[master_idx, '컨펌상태'] = new

                is_shorts = row['구분'] in ['샌드박스', '트레져헌터']
                stats = fetch_yt_data(row['URL'], yt_key, is_shorts=is_shorts)
                pic_url = stats.get('pic', "https://via.placeholder.com/300x300.png?text=Glowuprizz")
                
                st.markdown(f'<div style="width: 100%; aspect-ratio: 1/1; overflow: hidden; border-radius: 4px; margin-bottom: 5px;"><img src="{pic_url}" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                st.markdown(f"**{row['이름']}**")
                
                # 통계 표시
                st.markdown(f"<p style='margin-bottom:2px; font-size:11px; color:#1f77b4;'>📈 {row.get('조회수', '-')} / ER {row.get('ER_표시', '-')}</p>", unsafe_allow_html=True)
                
                # ⭐ 추천제품 복구! (0% 누락)
                st.markdown(f"<p style='margin-bottom:5px; font-size:12px;'>🎯 <b>추천:</b> {row.get('추천제품', '-')}</p>", unsafe_allow_html=True)
                
                with st.expander("📝"): st.write(row['상세 정보'])
                if row['URL'] != '-': st.link_button("🔗", row['URL'], use_container_width=True)

# ==========================================
# 6. 탭 화면 구성
# ==========================================
tab0, tab1, tab2, tab3, tab4 = st.tabs(["📊 통합 컨펌", "🏢 자사", "🌍 외부", "🤝 벤더사", "🏢 소속사"])

with tab0:
    st.header("📋 전체 리스트 통합 컨펌")
    st.info("💡 지정된 전속 멤버는 최상단에 고정되며, 이외 명단은 평균 조회수 순으로 정렬되어 있습니다.")
    display_df = st.session_state.df_master.drop(columns=['평균조회수', 'ER'])
    
    edited_df = st.data_editor(
        display_df,
        column_config={
            "번호": st.column_config.NumberColumn("No.", width="small", disabled=True),
            "URL": st.column_config.LinkColumn("링크"),
            "컨펌상태": st.column_config.SelectboxColumn("결정", options=["대기", "승인 ✅", "반려 ❌", "보류 ⏳"])
        },
        use_container_width=True, hide_index=True, key="main_editor"
    )
    st.session_state.df_master['컨펌상태'] = edited_df['컨펌상태']
    
    c_save, c_link = st.columns([1, 4])
    with c_save:
        if st.button("💾 구글 시트 저장", type="primary"):
            if conn:
                try:
                    conn.update(worksheet="Sheet1", data=display_df)
                    st.success("✅ 구글 시트 저장 성공!")
                except Exception as e: st.error(f"실패: {e}")
    with c_link: st.link_button("📂 원본 시트 열기", SHEET_URL)

with tab1:
    st.header("🏢 자사 크리에이터")
    c_sl, c_b1, c_b2, c_b3 = st.columns([2, 1, 1, 1])
    n_our = c_sl.slider("배치", 4, 8, 8, key="sl_our")
    df_our = st.session_state.df_master[st.session_state.df_master['구분']=='자사']
    if c_b1.button("모두 승인", key="b_a_o"): _apply_bulk(df_our, "승인 ✅")
    if c_b2.button("모두 반려", key="b_r_o"): _apply_bulk(df_our, "반려 ❌")
    if c_b3.button("모두 보류", key="b_w_o"): _apply_bulk(df_our, "보류 ⏳")
    
    for sub in ["전속", "파트너십", "프로젝트 협업"]:
        st.markdown(f"**💎 {sub}**")
        draw_gallery_custom(df_our[df_our['세부유형']==sub], num_cols=n_our)

with tab2:
    st.header("🌍 외부 크리에이터 (조회수순)")
    c_sl, c_b1, c_b2, c_b3 = st.columns([2, 1, 1, 1])
    n_ext = c_sl.slider("배치", 4, 8, 8, key="sl_ext")
    df_ext = st.session_state.df_master[st.session_state.df_master['구분']=='외부']
    if c_b1.button("모두 승인", key="b_a_e"): _apply_bulk(df_ext, "승인 ✅")
    if c_b2.button("모두 반려", key="b_r_e"): _apply_bulk(df_ext, "반려 ❌")
    if c_b3.button("모두 보류", key="b_w_e"): _apply_bulk(df_ext, "보류 ⏳")
    draw_gallery_custom(df_ext, num_cols=n_ext)

with tab3:
    st.header("🤝 벤더사 리스트")
    df_vn = st.session_state.df_master[st.session_state.df_master['구분']=='벤더사'].drop(columns=['평균조회수', 'ER', '조회수', 'ER_표시'], errors='ignore')
    st.dataframe(df_vn, use_container_width=True, hide_index=True, column_config={"URL": st.column_config.LinkColumn("Instagram 링크")})

with tab4:
    st.header("🏢 소속사 협업 리스트")
    st.info("**📞 담당자:** 샌드박스 허현지님(hjhuh@sandbox.co.kr) / 트레져헌터 박예은님(yeeun_p@treasurehunter.co.kr)")
    df_ag = st.session_state.df_master[st.session_state.df_master['구분'].isin(['샌드박스', '트레져헌터'])].drop(columns=['평균조회수', 'ER'], errors='ignore')
    st.dataframe(df_ag, use_container_width=True, hide_index=True, column_config={"URL": st.column_config.LinkColumn("채널 링크")})
