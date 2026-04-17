import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import json
import os

# ==========================================
# 1. 페이지 설정 및 보안 로드
# ==========================================
st.set_page_config(page_title="Glowuprizz PB Dashboard", page_icon="🚀", layout="wide")
st.title("인플루언서 리스트")

# Secrets에서 API 키 가져오기 (배포 환경용)
yt_key = st.secrets.get("YOUTUBE_KEY", "")
# 사이드바에서 키가 없을 경우를 대비한 입력창
with st.sidebar:
    st.header("🔑 API 설정")
    if not yt_key:
        yt_key = st.text_input("YouTube API Key 입력", type="password")
        st.warning("Secrets 설정이 되어있지 않아 수동 입력이 필요합니다.")
    else:
        st.success("✅ YouTube API 연동 중")
    st.markdown("---")
    st.info("이 대시보드는 대표님의 인플루언서 리스트 컨펌을 위해 구축되었습니다.")

# ==========================================
# 2. 데이터 세팅 (자사/외부/벤더/소속사)
# ==========================================
yt_data = [
    # 🏢 자사 - 전속
    {"구분": "자사", "세부유형": "전속", "이름": "심장에박현서", "URL": "https://youtube.com/channel/UCo4m81FJ-dT8MqijBlhbN2A", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "생각없이사는연", "URL": "https://youtube.com/channel/UCyVEhwFJ1HF66JqjxMkc-Uw", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "예보링", "URL": "https://youtube.com/channel/UCby6TnEm4xha2NIncRxC2EQ", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "미지수", "URL": "https://youtube.com/channel/UC-BS_A5wCxoCp06thW_V8wA", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 부재중", "URL": "https://youtube.com/channel/UC5Ida86tt8QKa4Myw7idxNg", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "매일제히", "URL": "https://youtube.com/channel/UCWWnWFPkfXMIjxNhBu5qVtg", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "채널주인 여깄음", "URL": "https://youtube.com/channel/UC9kUsuu1Giqa9V855EWa7-A", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "핏블리 FITVELY", "URL": "https://youtube.com/channel/UC3hRpIQ4x5niJDwjajQSVPg", "추천제품": "", "아이디어": ""},
    {"구분": "자사", "세부유형": "전속", "이름": "재넌", "URL": "https://youtube.com/channel/UCem8l1w4OWhkqpoOg1SB4_w", "추천제품": "쏙쉐이크 어퍼볼캡", "아이디어": "잦은 먹방과 바쁜 일상 속 쏙쉐이크로 간편하게 식단 관리하고 어퍼 볼캡으로 캐주얼룩을 연출하는 브이로그"},
    {"구분": "자사", "세부유형": "전속", "이름": "살빼조", "URL": "https://www.youtube.com/@dietjo311", "추천제품": "쏙쉐이크", "아이디어": "일상 브이로그 아침 루틴에서 쏙쉐이크를 간편한 식사 대용으로 보여주기"},
    
    # 🏢 자사 - 파트너십
    {"구분": "자사", "세부유형": "파트너십", "이름": "매드브로 MadBros", "URL": "https://youtube.com/channel/UCiTcv_AxQQSx77yGikHHDZw", "추천제품": "볼캡 쏙쉐이크", "아이디어": "쓰줍맨 활동 시 볼캡 착용 바쁜 일정 중 쏙쉐이크로 간편하게 에너지를 채우는 모습 노출"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "독고독채널", "URL": "https://youtube.com/channel/UCEUSANZNPXY1JsBoqhQIgxQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "자사", "세부유형": "파트너십", "이름": "김승배", "URL": "https://youtube.com/channel/UCPDiMzJdYb0Q-LxoP7W1j7g", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "자사", "세부유형": "파트너십", "이름": "kiu기우쌤", "URL": "https://youtube.com/channel/UCIZ5rCTYJ0s16FgT7OetVEQ", "추천제품": "솔브 모델링팩 괄사크림", "아이디어": "셀프케어 루틴으로 제품 활용"},
    {"구분": "자사", "세부유형": "파트너십", "이름": "비타민신지니 VitaminJINY", "URL": "https://youtube.com/channel/UC9trbyGOOjJmMea3w6c-e2A", "추천제품": "솔브 괄사크림", "아이디어": "붓기 승모근 체형교정 마사지에 솔브 괄사크림을 사용해 즉각적인 변화를 시연"},

    # 🏢 자사 - 프로젝트 협업
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "잡식맨 JOBXICMAN", "URL": "https://youtube.com/channel/UCVILvX9vIp-vMFGmCYJtG3A", "추천제품": "쏙쉐이크 어퍼볼캡", "아이디어": ""},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "아이뽀 i4", "URL": "https://youtube.com/channel/UC6jtibPJUrtufKBZCm6gbIg", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "자사", "세부유형": "프로젝트 협업", "이름": "대생이", "URL": "https://youtube.com/channel/UChE5nZAIhWS5vYTRjsUgRpQ", "추천제품": "어퍼 볼캡 체크셔츠", "아이디어": ""},

    # 🌍 외부 - 외부
    {"구분": "외부", "세부유형": "외부", "이름": "조재원", "URL": "https://youtube.com/channel/UC2o_y872S6YvaO1K8EYnoxg", "추천제품": "쏙쉐이크", "아이디어": "동금여사님과 쏙쉐이크 얼먹 먹방"},
    {"구분": "외부", "세부유형": "외부", "이름": "송대익", "URL": "https://youtube.com/channel/UCreFV1bKkKE6ufPtd5XeEJw", "추천제품": "쏙쉐이크", "아이디어": "자취방에서 생긴 일 영상에서 바쁜 자취 생활 중 쏙쉐이크로 간편하게 식사를 챙기는 모습을 자연스럽게 노출"},
    {"구분": "외부", "세부유형": "외부", "이름": "엄지렐라 Umjirella", "URL": "https://youtube.com/channel/UCLXafJ8yYXeUN_eHai-6Pgw", "추천제품": "어퍼 볼캡 체크셔츠", "아이디어": "엄지훈 캐릭터로 커플룩 소구"},
    {"구분": "외부", "세부유형": "외부", "이름": "숏박스", "URL": "https://youtube.com/channel/UC1B6SalAoiJD7eHfMUA9QrA", "추천제품": "어퍼 볼캡 체크셔츠", "아이디어": "스케치코미디 속 다양한 일상에서 캐릭터들이 어퍼 볼캡 체크셔츠를 착용하여 친근하고 자연스러운 스타일 연출"},
    {"구분": "외부", "세부유형": "외부", "이름": "김선태", "URL": "https://youtube.com/channel/UCt-BApVtJGrvF5pCgbiNVeg", "추천제품": "어퍼 볼캡 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "하루의하루[HARU]", "URL": "https://youtube.com/channel/UCpQxvEhfR60LR4s7PV48qIw", "추천제품": "솔브 멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "찰스엔터", "URL": "https://youtube.com/channel/UCCZ-gBdN59pF39tbm16xvdQ", "추천제품": "쏙쉐이크", "아이디어": "브이로그에 쏙쉐이크 출연"},
    {"구분": "외부", "세부유형": "외부", "이름": "침착맨", "URL": "https://youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ", "추천제품": "쏙쉐이크 어퍼 체크셔츠", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "랄랄ralral", "URL": "https://youtube.com/channel/UCEX1cZB5TL7jyKejXdTXCKA", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "오늘의 주우재", "URL": "https://youtube.com/channel/UCw-kXdzxMdMdLNI0ZlFFbmA", "추천제품": "어퍼 볼캡 체크셔츠", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "자유부인 한가인", "URL": "https://youtube.com/channel/UCvnVUhn95YfQazC_bc2lU6w", "추천제품": "솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "핫이슈지", "URL": "https://youtube.com/channel/UCdMeT09aEFDCH0NghWV41HQ", "추천제품": "솔브 멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "주둥이방송", "URL": "https://youtube.com/channel/UC9ta639M37zzWKwo7kKc80A", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "RISABAE", "URL": "https://youtube.com/channel/UC9kmlDcqksaOnCkC_qzGacA", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "고기남자", "URL": "https://youtube.com/channel/UCT3CumbFIJiW33uq0UI3zlg", "추천제품": "쏙쉐이크", "아이디어": "맛있는 요리 먹방 후 가볍게 쏙쉐이크로 식사하며 몸을 관리하는 모습을 보여준다"},
    {"구분": "외부", "세부유형": "외부", "이름": "사내뷰공업 beautyfool", "URL": "https://youtube.com/channel/UCeS6R89S32mSOxTNoEqrN7g", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "쓰까르", "URL": "https://youtube.com/channel/UCX14ZlyF0-tgVcDxLj-4ytA", "추천제품": "멜브 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "융덕 Yungduck", "URL": "https://youtube.com/channel/UC_zXObQdOXbUGe8IyVRcpSw", "추천제품": "멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "우정잉", "URL": "https://youtube.com/channel/UCW945UjEs6Jm3rVNvPEALdg", "추천제품": "멜브 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "망구 MANGOO", "URL": "https://youtube.com/channel/UCII-TCayU-6gkfzfgJKsFZw", "추천제품": "멜브 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "시네 si-ne", "URL": "https://youtube.com/channel/UC0-yyrDjTJ1YFzmV12vEp0Q", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "와코", "URL": "https://youtube.com/channel/UC8NmKAjUM0K4TZqNgboNEWA", "추천제품": "솔브 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "yeondukong 연두콩", "URL": "https://youtube.com/channel/UCAUbDYDwV34yk6pYiZg_CzA", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "젼언니 jeon_unni", "URL": "https://youtube.com/channel/UCyar0OYt0LoPzkkWcQAo6OA", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "Jiwon 지원", "URL": "https://youtube.com/channel/UCURnLWTrLZVv_KiVaeZakog", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "아인이놀아주기", "URL": "https://youtube.com/channel/UCKbsO2vQ9artnn2P-HLnYgQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민와와", "URL": "https://youtube.com/channel/UCJt-9Ku_D1Un6brccoTzglg", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "보현Bohyun", "URL": "https://youtube.com/channel/UCZkNETnsbFXG8h7RPQyBtNw", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "민가든", "URL": "https://youtube.com/channel/UCr_QBNzvSm_a7mreIpTregw", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "모르는지", "URL": "https://youtube.com/channel/UCDITZg2t7QPjwx_CYFmP_aw", "추천제품": "쏙쉐이크 멜브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "최종시안", "URL": "https://youtube.com/channel/UC_1ETgrcrLjHOP0YJmkWLVQ", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "진짜팥[RealPot]", "URL": "https://youtube.com/channel/UCLiiqZrEaA2nvDNC4v9Noiw", "추천제품": "솔브 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "이리유 iliyu", "URL": "https://youtube.com/channel/UCRFh2MoRiD-whPn0QuOzMFQ", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "기몌민", "URL": "https://youtube.com/channel/UC78welXHRpNJJfiB2zg5BSQ", "추천제품": "멜브 솔브 어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "홍또기", "URL": "https://youtube.com/channel/UCsjNYWQvbzb_4z4t_sL1y6w", "추천제품": "어퍼", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "람누끼", "URL": "https://youtube.com/channel/UC8fizCcGKHfrQKfvGtFiOiw", "추천제품": "멜브 솔브 어퍼 쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "유플라 yoofla", "URL": "https://youtube.com/channel/UCxlqra6Gb7BvpOaZaqD-duQ", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "허진희여사", "URL": "https://youtube.com/channel/UCsK4opmMoeLsRsZU54ghvtQ", "추천제품": "멜브 립타투", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "냥이아빠", "URL": "https://youtube.com/channel/UC5AAf4_zZxk-mCl46TogZQQ", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "외부", "이름": "김민지 KIMMINGEE", "URL": "https://youtube.com/channel/UCB9jzo97ZxA5Kl6JDfX0UPw", "추천제품": "멜브 립타투", "아이디어": ""},

    # 🌍 외부 - 기동
    {"구분": "외부", "세부유형": "기동", "이름": "김크리스탈 KimCrystal", "URL": "https://youtube.com/channel/UCcNYkzLMSkSiYaiAYjUNzRg", "추천제품": "멜브 솔브", "아이디어": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "다인이공", "URL": "https://youtube.com/channel/UCs7Bw5CQK82AHhyMQ59NZWA", "추천제품": "쏙쉐이크", "아이디어": ""},
    {"구분": "외부", "세부유형": "기동", "이름": "김밍 KIMMING", "URL": "https://youtube.com/channel/UCTjwlF8Y8hxR85JPUoZv-6A", "추천제품": "멜브 솔브 어퍼 쏙쉐이크", "아이디어": ""}
]
df_yt = pd.DataFrame(yt_data)

# 벤더사 인스타그램 데이터 (프로필 사진 불필요, 표 형태로 출력)
vendor_data = [
    {"분류": "1억 이상", "이름": "한스스타일", "URL": "https://www.instagram.com/hansstyle_hanna/", "추천제품": "솔브"},
    {"분류": "1억 이상", "이름": "11AM", "URL": "https://www.instagram.com/he11o_yeojin/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "강지혜", "URL": "https://www.instagram.com/hairstyle_jihye/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "츄니토리", "URL": "https://www.instagram.com/chunytory/", "추천제품": "솔브"},
    {"분류": "1억~1억 이상", "이름": "헤이가가", "URL": "https://www.instagram.com/hey_gaga_/", "추천제품": "솔브"},
    {"분류": "4,000~7,000만 평균", "이름": "뚜뜨", "URL": "https://www.instagram.com/mintoute_/", "추천제품": "쏙쉐이크(다양한 레시피 콘텐츠)"},
    {"분류": "4,000~7,000만 평균", "이름": "아뜨와지효", "URL": "https://www.instagram.com/atoi_jihyo/", "추천제품": "솔브"},
    {"분류": "3,000~5,000만 평균", "이름": "엔젤루밍", "URL": "https://www.instagram.com/ryu_angel/", "추천제품": "솔브 모델링팩"},
    {"분류": "3,000~5,000만 평균", "이름": "캘러리아", "URL": "https://www.instagram.com/hyo_kate_olivia/", "추천제품": "딸이랑 립타투 립시럽, 어머님은 젤리미스트"},
    {"분류": "3,000~5,000만 평균", "이름": "리미샵", "URL": "https://www.instagram.com/limi_unni/", "추천제품": "솔브"}
]
df_vendor = pd.DataFrame(vendor_data)

# 소속사 데이터 (샌드박스, 트레져헌터)
agency_data = [
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "linakeemz", "구독자": "119,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "1__xixx", "구독자": "43,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "lee_dan2", "구독자": "157,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "from.suason", "구독자": "152,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "ziyoo_days", "구독자": "50,000", "단가": "2,080,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "alisswlle", "구독자": "74,000", "단가": "1,950,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "인스타그램 릴스", "이름": "s0la._.c", "구독자": "54,000", "단가": "1,300,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "유튜브 쇼츠", "이름": "무찌", "구독자": "179,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "유튜브 쇼츠", "이름": "히루히루 HeeRu", "구독자": "127,000", "단가": "2,600,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "유튜브 쇼츠", "이름": "채울렛chaeullet", "구독자": "87,800", "단가": "1,950,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "유튜브 쇼츠", "이름": "후Hoo", "구독자": "53,200", "단가": "1,300,000", "비고": ""},
    {"소속": "샌드박스", "플랫폼/유형": "유튜브 쇼츠", "이름": "송타민", "구독자": "20,800", "단가": "910,000", "비고": "솔브 광고비 손익분기점 매출 290만 예상"},
    {"소속": "트레져헌터", "플랫폼/유형": "유튜브 커머스", "이름": "버터와여름이네", "구독자": "22.96만명", "단가": "RS 30%", "비고": "추천: 솔브 / 담당자: 박예은 매니저 yeeun_p@treasurehunter.co.kr"}
]
df_agency = pd.DataFrame(agency_data)

# ==========================================
# 3. 영구 캐싱 로직 (API 절약용)
# ==========================================
CACHE_FILE = "profile_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f: return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f: json.dump(cache, f)

if 'img_cache' not in st.session_state:
    st.session_state.img_cache = load_cache()

def get_yt_profile_pic(url, api_key):
    if url in st.session_state.img_cache:
        return st.session_state.img_cache[url]
    if not api_key:
        return "https://via.placeholder.com/150?text=No+Key"
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        # (채널 ID 추출 및 이미지 URL 획득 로직)
        # ...
        img_url = "추출된_이미지_주소" 
        st.session_state.img_cache[url] = img_url
        save_cache(st.session_state.img_cache)
        return img_url
    except:
        return "https://via.placeholder.com/150?text=Error"

# ==========================================
# 4. 화면 구성 (탭 인터페이스)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🏢 자사", "🌍 외부", "🤝 벤더사", "🏢 소속사"])

with tab1:
    st.header("자사 크리에이터 (전속/파트너십/프로젝트)")
    # (드래그 가능한 갤러리 구현 함수 호출)
    # draw_gallery(df_yt[df_yt['구분'] == '자사'])

with tab3:
    st.dataframe(df_vendor, use_container_width=True)

with tab4:
    st.dataframe(df_agency, use_container_width=True)
