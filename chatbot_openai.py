import streamlit as st
import csv
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])  # ← secrets.toml 또는 환경변수로 설정하세요

# CSV 로딩 함수
@st.cache_data
def load_recycling_data(filename):
    data = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = row["item"]
            aliases = [alias.strip() for alias in row["aliases"].split(",")]
            instruction = row["instruction"]
            data[item] = {
                "aliases": aliases,
                "instruction": instruction
            }
    return data

# 품목 추출
def extract_item(user_input, data):
    for item, info in data.items():
        for alias in info["aliases"]:
            if alias in user_input:
                return item
    return None

# GPT 호출
def ask_gpt(question):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 분리수거 전문가야. 간결하고 정확하게 분리수거 방법과 요일을 알려줘."},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 오류: {e}"

# 앱 시작
st.title("♻️ 분리수거 챗봇")

recycling_data = load_recycling_data("recycling_data.csv")
user_input = st.text_input("분리수거 관련 질문을 입력하세요:")

if user_input:
    item = extract_item(user_input.lower(), recycling_data)
    if item:
        st.success(recycling_data[item]["instruction"])
    else:
        st.info("GPT에게 물어보는 중입니다...")
        response = ask_gpt(user_input)
        st.success(response)

