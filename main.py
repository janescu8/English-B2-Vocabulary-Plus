import random
import streamlit as st
import re
import os
from gtts import gTTS
import time
from pydub import AudioSegment

# 匯入所有書籍的單字庫
from anna_12_4_S2 import word_data as anna_12_4_S2
from the_automatic_toaster import word_data as the_automatic_toaster
# 書籍選擇
book_options = {
    "Your English Five a Day #12.4 S2": anna_12_4_S2,
    "The best invention since sliced bread? - Rachel Yang | the automatic toaster": the_automatic_toaster,
}

st.title("📚 英文單字測試遊戲")
st.write("選擇一本書來挑戰你的詞彙能力！")

# 讓使用者選擇一本書
selected_book = st.selectbox("請選擇一本書：", list(book_options.keys()))
word_data = book_options[selected_book]

# 顯示單字庫總數
st.write(f"📖 單字庫總數：{len(word_data)} 個單字")

# 取得不重複的隨機單字
def get_unique_words(num_words):
    all_words = [(word, data[0], data[1]) for word, data in word_data.items()]
    random.shuffle(all_words)
    return all_words[:num_words]

# 隱藏單字
def mask_word(sentence, word):
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    hidden_word = word[0] + "_" * (len(word) - 2) + word[-1]
    return pattern.sub(hidden_word, sentence)

# AI 發音
def play_pronunciation(text, filename="pronunciation.mp3", wav_filename="pronunciation.wav"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    sound = AudioSegment.from_mp3(filename)
    sound.export(wav_filename, format="wav")
    if os.path.exists(wav_filename):
        with open(wav_filename, "rb") as audio_file:
            st.audio(audio_file, format="audio/wav")
    else:
        st.error("⚠️ 無法播放音訊，音檔未正確生成。")

# 清理文字：忽略大小寫與符號
def clean_text(text):
    return re.sub(r'[^a-zA-Z\-’\' ]', '', text).lower().strip()

# 使用者選擇題數
num_questions = st.number_input("輸入測試題數", min_value=1, max_value=len(word_data), value=10, step=1)

# 選擇測試類型
test_type = st.radio("請選擇測試類型：", ["拼寫測試", "填空測試"])

# 初始化 Session State
if (
    "initialized" not in st.session_state
    or st.session_state.selected_book != selected_book
    or st.session_state.num_questions != num_questions
):
    st.session_state.words = get_unique_words(num_questions)
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.submitted = False
    st.session_state.input_value = ""
    st.session_state.selected_book = selected_book
    st.session_state.num_questions = num_questions  # 記住目前題數
    st.session_state.initialized = True

# 顯示題目
if st.session_state.current_index < len(st.session_state.words):
    test_word, meaning, example_sentence = st.session_state.words[st.session_state.current_index]
    st.write(f"🔍 提示：{meaning}")

    if st.button("播放發音 🎵"):
        play_pronunciation(test_word if test_type == "拼寫測試" else example_sentence)

    # 顯示題目與輸入框
    if test_type == "拼寫測試":
        user_answer = st.text_input(
            "請輸入單字的正確拼寫：",
            value=st.session_state.input_value,
            key=f"input_{st.session_state.current_index}",
        )
    else:
        st.write(f"請填空：{mask_word(example_sentence, test_word)}")
        user_answer = st.text_input(
            "請填入缺漏的單字：",
            value=st.session_state.input_value,
            key=f"input_{st.session_state.current_index}",
        )

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if st.button("提交答案"):
        st.session_state.submitted = True

    # 答案判斷（使用 clean_text）
    if st.session_state.submitted:
        if clean_text(user_answer) == clean_text(test_word):
            st.success("✅ 正確！")
            st.session_state.score += 1
        else:
            st.error(f"❌ 錯誤，正確答案是 {test_word}")
            play_pronunciation(test_word)
            st.session_state.mistakes.append((test_word, meaning, example_sentence))

        st.session_state.input_value = ""
        time.sleep(2)
        st.session_state.submitted = False
        st.session_state.current_index += 1
        st.rerun()

# 測驗結束
else:
    st.write(f"🎉 測試結束！你的得分：{st.session_state.score}/{len(st.session_state.words)}")

    if st.session_state.mistakes:
        st.write("❌ 你答錯的單字：")
        for word, meaning, example in st.session_state.mistakes:
            st.write(f"**{word}** - {meaning}")
            st.write(f"例句：{example}")
            st.write("---")

    if st.button("🔄 重新開始"):
        st.session_state.words = get_unique_words(num_questions)
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.mistakes = []
        st.session_state.submitted = False
        st.session_state.input_value = ""
        st.rerun()
