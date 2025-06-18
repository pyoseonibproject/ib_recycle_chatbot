import csv
from openai import OpenAI

# 🔑 OpenAI API 키 설정
client = OpenAI(api_key="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")  # ← 본인의 API 키 입력

# CSV 로딩
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

# 키워드 기반 품목 추출
def extract_item(user_input, data):
    for item, info in data.items():
        for alias in info["aliases"]:
            if alias in user_input:
                return item
    return None

# OpenAI GPT 응답
def ask_gpt(question):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 분리수거 전문가야. 간결하고 정확하게 물건이 어떤 분리수거 종류인지 설명하세요. 그리고 플라스틱이면 월요일, 수요일, 금요일, 일요일에, 종이류는 화요일, 목요일, 토요일, 비닐은 목요일, 일요일, 불연성은 화요일, 토요일에 버릴 수 있다고 해줘.  그리고 일반쓰레기, 음식물 쓰레기,캔, 고철, 유리병, 스티로폼이라면 매일 버릴 수 있다고 해줘 "},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 응답 중 오류 발생: {e}"

# 챗봇 로직
def recycling_chatbot(user_input, data):
    user_input = user_input.lower()
    item = extract_item(user_input, data)

    if item:
        return data[item]["instruction"]
    else:
        print("생각중...")
        return ask_gpt(user_input)

# 실행 루프
if __name__ == "__main__":
    print("♻️ GPT 보완형 분리수거 챗봇 시작 ('종료' 입력 시 종료)")
    recycling_data = load_recycling_data("recycling_data.csv")

    while True:
        user_input = input("사용자: ")
        if user_input.strip().lower() in ["종료", "exit", "quit"]:
            print("챗봇: 감사합니다. 다음에 또 만나요!")
            break
        response = recycling_chatbot(user_input, recycling_data)
        print(f"챗봇: {response}")

