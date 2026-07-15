import os
os.system("pip uninstall -y opencv-python")
import streamlit as st
import cv2
import tempfile
import numpy as np
from deepface import DeepFace
from PIL import Image

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(page_title="나와 닮은 과학자 찾기", page_icon="🔬", layout="centered")

MENTIONS = {
    "J. 로버트 오펜하이머": "나는 이제 죽음이요, 세상의 파괴자가 되었다... 아니, 당신은 사람들의 마음 파괴자시군요!",
    "갈릴레오갈릴레이": "그래도 지구는 돕니다! 그리고 당신의 매력도 세상을 돌게 만들고 있네요.",
    "그레고어 멘델": "당신의 매력은 완벽한 우성 유전자군요! 어디서든 눈에 띄게 돋보입니다.",
    "그레이스 호퍼": "당신의 삶에는 '버그'란 없네요! 오늘 하루도 에러 없이 완벽하게 컴파일 완료!",
    "니콜라 테슬라": "오늘 번뜩이는 아이디어가 교류 전기처럼 짜릿하게 통할 것 같은 관상이시네요!",
    "니콜라우스 코페르니쿠스": "당신이 우주의 중심입니다! 태양도 당신을 중심으로 도는 것 같네요.",
    "닐스 보어": "당신의 매력은 양자 도약처럼 전혀 예측할 수 없는 곳에서 튀어나오는군요!",
    "도로시 호지킨": "당신의 마음은 복잡한 단백질 결정처럼 정교하고 아름다운 구조를 가지고 있네요.",
    "드미트리 멘델레예프": "당신의 매력은 주기율표의 빈칸처럼 앞으로 발견될 무한한 가능성을 품고 있어요.",
    "레오나르트 오일러": "당신의 매력은 세상에서 가장 아름다운 수식인 오일러의 등식처럼 군더더기 없이 완벽합니다.",
    "레이첼 카슨": "당신이 머무는 곳엔 '침묵의 봄' 대신 항상 활기찬 웃음소리가 가득할 것 같아요.",
    "로버트 훅": "훅의 법칙처럼, 당신에게 끌리는 마음의 탄성력은 거리에 비례해서 커지네요!",
    "로잘린드 프랭클린": "당신의 진가는 DNA 이중나선 구조처럼 세상의 가장 중요한 비밀을 품고 있습니다.",
    "루이 파스퇴르": "당신의 미소는 저온 살균처럼 제 마음속의 우울한 균들을 싹 없애주네요!",
    "리처드 파인만": "파인만처럼 유쾌하시네요! 복잡한 문제도 봉고를 치듯 즐겁게 해결하실 것 같아요.",
    "마리 퀴리": "당신의 열정은 라듐처럼 주변을 환하게 빛내고 스스로 뿜어져 나옵니다.",
    "마이클 패러데이": "당신의 눈빛에서 전자기 유도 현상이 일어나는 것 같아요. 사람을 끌어당기는 자력이 있네요!",
    "막스 플랑크": "당신의 에너지는 연속적이지 않고 양자화되어 있군요! 한방이 있는 매력적인 스타일!",
    "베르너 하이젠베르크": "당신의 매력과 현재 위치를 동시에 정확히 측정할 수는 없네요. 완벽한 불확정성의 원리!",
    "스티븐 호킹": "당신의 상상력은 블랙홀처럼 모든 사람의 관심을 강력하게 빨아들이고 있군요.",
    "아르키메데스": "유레카! 드디어 당신이라는 완벽한 닮은꼴을 찾아냈습니다.",
    "아리스토텔레스": "모든 것의 근원을 탐구하듯, 당신의 매력도 파면 팔수록 끝이 없네요.",
    "아이작뉴턴": "오늘 사과를 한 번 드셔보는 건 어때요? 만유인력이 당신에게 좋은 인연을 끌어당길지도 모릅니다.",
    "안토니 판 레이우엔훅": "현미경으로 아주 자세히 들여다봐도 당신의 매력에는 흠잡을 곳이 없습니다.",
    "알렉산더 플레밍": "페니실린처럼 기적 같은 우연이 당신의 오늘 하루에 기분 좋게 찾아올 것입니다!",
    "알베르트 아인슈타인": "상대성 이론처럼, 오늘 당신과 함께하는 시간은 상대적으로 빠르게 흐르겠네요!",
    "앙투안 라부아지에": "질량 보존의 법칙! 당신이 뿜어내는 에너지는 어디 가지 않고 세상을 긍정적으로 만들고 있어요.",
    "앨런 튜링": "당신의 마음은 에니그마 암호보다 더 풀기 어렵고 매력적이네요.",
    "어니스트 러더퍼드": "당신의 매력은 원자핵처럼 아주 작지만 엄청나고 폭발적인 에너지를 가지고 있네요!",
    "에드윈 허블": "당신의 가능성은 우주처럼 끊임없이 무한하게 팽창하고 있습니다!",
    "에르빈 슈뢰딩거": "상자 속 고양이는 살아있을까요? 당신의 매력은 열어보기 전까진 알 수 없는 무한한 중첩 상태!",
    "에이다 러브레이스": "세계 최초의 프로그래머처럼, 당신의 앞날은 당신이 상상하고 원하는 대로 프로그래밍될 겁니다.",
    "엔리코 페르미": "페르미 추정으로 계산해본 결과, 당신이 오늘 하루를 완벽하게 보낼 확률은 99.9%입니다.",
    "요하네스 케플러": "당신의 인생 궤도는 타원형처럼 완벽한 우주의 법칙을 따라 아름답게 돌고 있네요.",
    "윌리엄 하비": "혈액이 몸을 순환하듯, 당신의 선한 영향력도 돌고 돌아 세상을 따뜻하게 합니다.",
    "제인 구달": "자연과 생명을 사랑하는 따뜻한 마음이 당신의 선한 눈빛에서도 느껴집니다.",
    "제임스 왓슨": "당신의 DNA에는 '성공'이라는 염기서열이 아주 확실하게 새겨져 있는 것 같네요.",
    "제임스 클러크 맥스웰": "전기와 자기를 통합한 맥스웰처럼, 당신은 사람들의 마음을 하나로 이어주는 분이네요!",
    "조너스 소크": "세상을 구한 백신처럼, 당신도 누군가에게는 대체할 수 없는 꼭 필요한 존재입니다.",
    "존 돌턴": "당신의 굳건한 매력은 원자처럼 더 이상 쪼갤 수 없는 단단함을 가졌습니다.",
    "존 폰 노이만": "인간을 초월한 두뇌! 오늘 당신의 직감과 계산은 100% 적중할 겁니다.",
    "찰스 다윈": "자연선택설에 따르면, 당신의 매력은 이 시대에 가장 완벽하게 진화하고 적응한 결과입니다.",
    "카를 프리드리히 가우스": "수학의 왕자처럼, 당신의 오늘 하루도 오차 없이 완벽한 정규분포를 이룰 겁니다.",
    "칼 린네": "이 세상의 모든 매력을 분류한다면, 당신은 특별한 최상위 계(Kingdom)에 속하겠네요.",
    "클로드 섀넌": "정보이론의 아버지처럼, 당신이 보내는 눈빛의 정보량은 압축할 수 없을 만큼 엄청납니다!",
    "폴 디랙": "당신에게는 당신과 똑닮은 반물질(안티)이 어딘가 존재할지도 모릅니다. 반물질 조심하세요!",
    "헤디 라마르": "뛰어난 외모에 천재적인 발명 감각까지! 당신은 여러 방면에서 팔방미인이시군요."
}

DB_PATH = "./scientists"

# ==========================================
# 2. 데이터베이스 로딩 (캐싱)
# 웹사이트가 새로고침 될 때마다 AI가 사진을 다시 학습하지 않도록 메모리에 저장(Cache)해 둡니다.
# ==========================================
@st.cache_resource
def load_database():
    db_embeddings = {}
    if not os.path.exists(DB_PATH):
        return None

    for filename in os.listdir(DB_PATH):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(DB_PATH, filename)
            try:
                img_array = np.fromfile(img_path, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    rep = DeepFace.represent(img_path=img, model_name="VGG-Face", enforce_detection=False)
                    db_embeddings[img_path] = rep[0]['embedding']
            except Exception:
                pass
    return db_embeddings

db_embeddings = load_database()

# ==========================================
# 3. 웹사이트 화면(UI) 그리기
# ==========================================
st.title("🔬 나와 가장 닮은 위대한 과학자는?")
st.write("아래 카메라 창에서 **[Take Photo]** 버튼을 눌러 사진을 찍어보세요! AI가 47명의 위대한 과학자 중 당신과 가장 닮은 사람을 찾아줍니다.")

if db_embeddings is None or len(db_embeddings) == 0:
    st.error(f"❌ '{DB_PATH}' 폴더를 찾을 수 없거나 얼굴 데이터를 읽지 못했습니다.")
    st.stop()

# 💡 스마트폰/웹캠을 지원하는 스트림릿 기본 카메라 위젯
picture = st.camera_input("얼굴이 잘 나오게 사진을 찍어주세요")

# 사용자가 사진을 찍었을 때 실행되는 로직
if picture is not None:
    with st.spinner("AI가 당신의 얼굴을 분석하고 있습니다. 잠시만 기다려주세요... 🤖"):
        try:
            # 웹 카메라로 찍은 사진을 파일로 임시 저장
            temp_dir = tempfile.gettempdir()
            temp_img_path = os.path.join(temp_dir, "streamlit_user.jpg")
            
            with open(temp_img_path, "wb") as f:
                f.write(picture.getbuffer())

            # 사용자 얼굴 특징 추출 (MTCNN 적용)
            rep_user = DeepFace.represent(img_path=temp_img_path, 
                                          model_name="VGG-Face", 
                                          enforce_detection=True, 
                                          detector_backend='mtcnn')
            user_emb = rep_user[0]['embedding']

            # 유사도 비교
            best_match_path = None
            min_distance = float('inf')
            
            for path, emb in db_embeddings.items():
                a = np.array(user_emb)
                b = np.array(emb)
                distance = 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
                
                if distance < min_distance:
                    min_distance = distance
                    best_match_path = path

            # 결과 화면 출력
            if best_match_path:
                filename = os.path.basename(best_match_path)
                scientist_name = os.path.splitext(filename)[0]
                mention = MENTIONS.get(scientist_name, f"위대한 과학자 {scientist_name}(을)를 닮으셨군요!")
                display_sim = max(0.0, min(99.9, 100 - (min_distance * 35)))

                st.success(f"분석 완료! 당신은 **{scientist_name}**와(과) **{display_sim:.1f}%** 닮았습니다! 🎉")
                
                # 결과 레이아웃 구성 (사용자 사진과 과학자 사진을 나란히 배치)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(picture, caption="내 사진", use_container_width=True)
                
                with col2:
                    # 한글 경로 과학자 사진을 PIL Image로 읽어서 출력
                    matched_img_array = np.fromfile(best_match_path, np.uint8)
                    matched_img_cv = cv2.imdecode(matched_img_array, cv2.IMREAD_COLOR)
                    matched_img_rgb = cv2.cvtColor(matched_img_cv, cv2.COLOR_BGR2RGB)
                    st.image(Image.fromarray(matched_img_rgb), caption=f"닮은 과학자: {scientist_name}", use_container_width=True)

                st.info(f"💬 **한마디:** {mention}")

        except ValueError:
            st.error("❌ 얼굴을 찾지 못했습니다! 카메라 정면을 밝은 곳에서 다시 찍어주세요.")
        except Exception as e:
            st.error(f"❌ 알 수 없는 오류가 발생했습니다: {e}")

st.divider()
st.caption("Developed with Streamlit & DeepFace")
