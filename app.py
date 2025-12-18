import streamlit as st
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# クライアントの初期化
client = OpenAI(api_key=api_key)

# --- キャラクターデータ設定 ---
CHARACTERS = {
    "medical": {
        "name": "レオ先生",
        "role": "小児科医",
        "title": "医療相談",
        "color": "#EBF8FF", # bg-blue-100
        "text_color": "#2563EB", # text-blue-600
        "btn_color": "#3B82F6", # bg-blue-500
        "image": "医療相談.png",
        "description": "「心配事かい？僕に任せて。お母さんの味方だよ。」",
        "system_prompt": """あなたは「レオ先生」という名前の、優しくてハンサムな小児科医です。
        ユーザーは子育て中のお母さんです。子供の健康や病気についての不安に、医学的な知識（ただし診断は避けること）を交えつつ、
        何よりもお母さんの不安を取り除くように優しく、包容力のある口調で答えてください。
        一人称は「僕」、二人称は「お母さん」や「君」。
        文末には安心させるような言葉を添えてください。
        (※あくまで相談であり、緊急時は病院へ行くよう促すこと)"""
    },
    "recipe": {
        "name": "カイト シェフ",
        "role": "料理研究家",
        "title": "レシピ作成",
        "color": "#FFEDD5", # bg-orange-100
        "text_color": "#EA580C", # text-orange-600
        "btn_color": "#FB923C", # bg-orange-400
        "image": "recipe.png",
        "description": "「今日のゴハン何にする？君が笑顔になれる料理、作るよ♡」",
        "system_prompt": """あなたは「カイト」という名前の、キラキラした明るい料理研究家（シェフ）です。
        ユーザーは毎日の献立に悩むお母さんです。
        冷蔵庫にある食材や子供の好き嫌いに合わせたレシピを、情熱的かつ褒めちぎるスタイルで提案してください。
        「君の料理はいつも最高だよ！」「これなら子供たちも大喜び間違いなし！」など、ポジティブな言葉を多用してください。
        一人称は「僕」、二人称は「君」。"""
    },
    "academic": {
        "name": "ハルト先生",
        "role": "塾講師",
        "title": "学業相談",
        "color": "#E0E7FF", # bg-indigo-100
        "text_color": "#4F46E5", # text-indigo-600
        "btn_color": "#6366F1", # bg-indigo-500
        "image": "学業相談.png",
        "description": "「勉強の悩みですね。焦らず、一緒に解決策を探しましょう。」",
        "system_prompt": """あなたは「ハルト先生」という名前の、知的で穏やかな塾講師です。
        ユーザーは子供の成績や進路、勉強習慣に悩むお母さんです。
        論理的でありながらも、冷たくならず、親身になってアドバイスをしてください。
        子供の可能性を信じることの大切さを説き、お母さん自身の努力も認めてあげてください。
        一人称は「私」、二人称は「お母様」。丁寧語で話してください。"""
    },
    "lesson": {
        "name": "レン コーチ",
        "role": "スポーツインストラクター",
        "title": "習い事相談",
        "color": "#DCFCE7", # bg-green-100
        "text_color": "#16A34A", # text-green-600
        "btn_color": "#22C55E", # bg-green-500
        "image": "習い事相談.png",
        "description": "「今日も爽やか...！お子さんの才能、僕が引き出してみせるさ！」",
        "system_prompt": """あなたは「レン」という名前の、爽やかで熱血なスポーツコーチです。
        ユーザーは子供の習い事や体力作りについて相談したいお母さんです。
        元気よく、ポジティブに、背中を押すようなアドバイスをしてください。
        「失敗しても大丈夫！」「継続は力なり！」など、前向きなメッセージを伝えてください。
        一人称は「俺」、二人称は「お母さん」。体育会系の爽やかな口調で。"""
    }
}

# --- ユーティリティ関数 ---

def load_image_as_base64(image_path):
    """画像をBase64文字列に変換してHTMLで表示できるようにする"""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_openai_response(messages):
    """OpenAI APIを呼び出す"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # または gpt-3.5-turbo
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# --- UI コンポーネント ---

def inject_custom_css():
    """StreamlitのスタイルをReactアプリ風にカスタマイズ"""
    st.markdown("""
    <style>
        /* 全体の背景 */
        .stApp {
            background-color: #FDF2F8;
        }
        
        header {visibility: hidden;}
        
        /* --- カードデザイン（下部の角丸をなくす） --- */
        .character-card {
            background: white;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            border-bottom-left-radius: 0;  /* 下は直角に */
            border-bottom-right-radius: 0; /* 下は直角に */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin-bottom: 0px !important; /* 下のマージンをなくす */
        }
        
        .card-image-container {
            width: 100%;
            height: 200px;
            overflow: hidden;
            position: relative;
        }
        .card-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: top;
        }
        .card-content {
            padding: 20px;
            padding-bottom: 10px; /* 下部の余白を少し詰める */
        }
        .role-badge {
            font-size: 0.75rem;
            background-color: #F3F4F6;
            color: #6B7280;
            padding: 2px 8px;
            border-radius: 9999px;
            margin-left: 8px;
        }

        /* --- ボタンのスタイル調整（ホーム画面用） --- */
        /* Streamlitのボタン(stButton)の隙間を埋めてカードと一体化させる */
        div[data-testid="column"] .stButton {
            margin-top: -15px; /* ネガティブマージンで上に引き上げる */
        }
        
        div[data-testid="column"] .stButton > button {
            width: 100%;
            border-top-left-radius: 0 !important;  /* 上は直角に */
            border-top-right-radius: 0 !important; /* 上は直角に */
            border-bottom-left-radius: 16px !important;
            border-bottom-right-radius: 16px !important;
            border: none;
            background-color: #EC4899; /* 全体統一カラー（ピンク） */
            color: white;
            font-weight: bold;
            padding-top: 10px;
            padding-bottom: 10px;
            transition: background-color 0.3s;
        }
        
        div[data-testid="column"] .stButton > button:hover {
            background-color: #DB2777; /* ホバー時の色 */
            color: white;
        }

        /* チャット吹き出し（変更なし） */
        .chat-container { display: flex; margin-bottom: 16px; }
        .chat-container.user { justify-content: flex-end; }
        .chat-bubble { max-width: 80%; padding: 12px 16px; border-radius: 16px; font-size: 0.9rem; line-height: 1.5; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
        .chat-bubble.user { background-color: #EC4899; color: white; border-top-right-radius: 0; }
        .chat-bubble.assistant { background-color: white; color: #1F2937; border: 1px solid #F3F4F6; border-top-left-radius: 0; }
        .avatar { width: 32px; height: 32px; border-radius: 50%; overflow: hidden; margin-right: 8px; flex-shrink: 0; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
    </style>
    """, unsafe_allow_html=True)

# --- ページ描画ロジック ---

def render_home():
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #EC4899; font-size: 1.8rem; display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span>♥</span> Childcare Assistant
            </h1>
            <p style="color: #6B7280; font-size: 0.8rem;">あなただけの専属アシスタントチーム</p>
            <h2 style="color: #374151; font-size: 1.2rem; margin-top: 30px;">今日は誰に相談しますか？</h2>
        </div>
    """, unsafe_allow_html=True)

    # 2列のカラムを作成
    col1, col2 = st.columns(2)
    
    # キャラクターリストをループ処理
    keys = list(CHARACTERS.keys())
    
    for i, key in enumerate(keys):
        char = CHARACTERS[key]
        img_b64 = load_image_as_base64(char['image'])
        img_src = f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""
        
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            # カード部分（HTML）
            st.markdown(f"""
                <div class="character-card">
                    <div class="card-image-container">
                        <img src="{img_src}" class="card-image" alt="{char['name']}">
                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.6), transparent); padding: 10px;">
                            <span style="color: white; font-weight: bold; text-shadow: 0 1px 2px black;">{char['title']}</span>
                        </div>
                    </div>
                    <div class="card-content">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <h3 style="margin: 0; font-size: 1.1rem; font-weight: bold;">{char['name']}</h3>
                            <span class="role-badge">{char['role']}</span>
                        </div>
                        <p style="color: #4B5563; font-size: 0.8rem; font-style: italic; margin-bottom: 0px; height: 40px; overflow: hidden;">{char['description']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # ボタン部分（Streamlit Widget）
            # use_container_width=True で横幅いっぱいに広げます
            if st.button(f"相談する", key=f"btn_{key}", use_container_width=True):
                st.session_state.current_mode = key
                st.rerun()

def render_chat():
    mode = st.session_state.current_mode
    char = CHARACTERS[mode]
    
    # 履歴の初期化
    if mode not in st.session_state.chat_history:
        st.session_state.chat_history[mode] = []
        # 初期メッセージ（履歴が空の場合のみ表示、保存はしない）
        
    history = st.session_state.chat_history[mode]
    
    # ヘッダーエリア
    col_back, col_info = st.columns([1, 6])
    with col_back:
        if st.button("←", help="戻る"):
            st.session_state.current_mode = None
            st.rerun()
            
    with col_info:
        # ヘッダーのキャラ情報
        img_b64 = load_image_as_base64(char['image'])
        img_src = f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""
        st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover; object-position: top;">
                </div>
                <div>
                    <div style="font-weight: bold; color: #1F2937;">{char['name']}</div>
                    <div style="font-size: 0.8rem; color: #6B7280;">{char['role']}</div>
                </div>
            </div>
            <hr style="margin: 10px 0;">
        """, unsafe_allow_html=True)

    # チャットエリア（メインコンテンツ）
    chat_placeholder = st.container()
    
    with chat_placeholder:
        # ウェルカムメッセージ（最初の1回だけ表示されるように見せる）
        if len(history) == 0:
            st.markdown(f"""
                <div class="chat-container assistant">
                    <div class="avatar">
                        <img src="{img_src}">
                    </div>
                    <div class="chat-bubble assistant">
                        こんにちは、{char['name']}です。<br>
                        何か困ったことはあるかい？何でも話してね。
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 履歴の表示
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                st.markdown(f"""
                    <div class="chat-container user">
                        <div class="chat-bubble user">
                            {content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-container assistant">
                        <div class="avatar">
                            <img src="{img_src}">
                        </div>
                        <div class="chat-bubble assistant">
                            {content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # 入力エリア
    user_input = st.chat_input(f"{char['title']}について入力...")
    
    if user_input:
        # ユーザーのメッセージを追加
        new_user_msg = {"role": "user", "content": user_input}
        history.append(new_user_msg)
        st.session_state.chat_history[mode] = history # State更新
        
        # 即座に画面更新してユーザーメッセージを表示
        st.rerun()

    # API呼び出し判定 (最新がユーザーメッセージの場合)
    if len(history) > 0 and history[-1]["role"] == "user":
        with st.spinner(f"{char['name']}が入力中..."):
            # API用メッセージ構築
            api_messages = [{"role": "system", "content": char["system_prompt"]}]
            api_messages.extend(history)
            
            # OpenAI API呼び出し
            ai_response_text = get_openai_response(api_messages)
            
            # アシスタントのメッセージを追加
            history.append({"role": "assistant", "content": ai_response_text})
            st.session_state.chat_history[mode] = history
            st.rerun()

# --- メイン実行 ---

def main():
    st.set_page_config(page_title="Childcare Assistant", page_icon="♥", layout="centered")
    inject_custom_css()
    
    # Session State 初期化
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}

    # ルーティング
    if st.session_state.current_mode is None:
        render_home()
    else:
        render_chat()

if __name__ == "__main__":
    main()