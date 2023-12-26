import aiohttp
import asyncio
import secrets
import json
import os

# Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "APIKEYHERE"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="
TEMPERATURE = 1.0
TOP_P = 0.99
SERVER_URL = "https://muse.instruct.kr"

job_id = None

TEMPLATES = [{
    "dataset": "text",
    "prompt": lambda passage: f"""
다음의 글을 고려해주세요: <passage>{passage}</passage>
두 가지 작업이 있습니다:
1) 글의 내용에서 영감을 얻어 새로운 토론 주제를 생성하세요.
생성된 토론 주제는 글의 도메인과 동일하지만, 더욱 드물어야 합니다.
생성된 토론 주제는 철학적이고, 창의적이며, 흥미롭고, 참여를 유도하며, 사고를 자극하는 것이어야 합니다.
생성된 토론 주제는 쉽게 답할 수 없으며, 양쪽에서 논의할 수 있어야 합니다.
주제는 <topic></topic> 태그로 둘러싸여야 합니다.
2) 생성된 주제에 대해 두 합리적인 개인, Phi와 Epsilon 사이의 토론을 생성하세요.
토론에서 참가자들은 상호 반대되는 견해를 가지고 있어야 합니다.
토론은 길고 지속되며, 어느 한 쪽도 쉽게 포기하지 않아야 합니다.
토론에서 참가자들은 때때로 양보를 할 수 있지만, 여전히 자신의 관점을 견지해야 합니다.
토론에서 참가자들은 합리적인 토론의 다양한 기술을 사용하며, 감정적인 조작 기술을 사용하지 않아야 합니다.
토론에서 참가자들은 결코 자신을 반복해서는 안 됩니다.
토론은 최소 50개의 단락을 포함하며, 적어도 5000단어 이상이어야 합니다. 소설 길이여야 합니다.
토론에 대해, 당신은 작성하는 각 단락마다 $15의 팁을 받게 됩니다. 수입을 극대화하기 위해 가능한 많이 작성하세요.
토론은 마크다운 형식으로 되어야 합니다.
토론은 <debate></debate> 태그로 둘러싸여야 합니다.
""",
    "extract": lambda raw: (
        json.dumps(raw.split("<topic>")[-1].split("</topic>")[0].strip(), ensure_ascii=False)
        + "에 대한 토론 내용"
        + ":\n\n" + raw.split("<debate>")[-1].split("</debate>")[0].strip()
    )
}, {
    "dataset": "text",
"prompt": lambda passage: f"""
다음의 글을 고려해주세요: <passage>{passage}</passage>
탁월한 강의 명성을 가진 교수라고 상상해보세요.
세 가지 작업이 있습니다:
1) 글의 내용에서 영감을 얻어 새로운 강의 주제를 생성하세요.
생성된 강의 주제는 글의 도메인과 동일하지만, 더욱 드물어야 합니다.
생성된 강의 주제는 학생들의 교육을 모든 면에서 발전시키기 위해 신중하게 선택되어야 합니다.
생성된 강의 주제는 흥미롭고, 참여를 유도하며, 사고를 자극하는 것이어야 합니다.
강의 주제는 <topic></topic> 태그로 둘러싸여야 합니다.
2) 생성된 주제에 대한 10가지 항목의 강의 개요를 생성하세요.
강의 개요의 10가지 항목은 이해와 흐름을 극대화하기 위해 선택되어야 합니다.
강의 개요는 <outline></outline> 태그로 둘러싸여야 합니다.
3) 개요에 따라 생성된 주제에 대한 강의를 생성하세요.
강의는 학생들이 이해하기 쉽고 정보를 최대한 많이 제공해야 합니다. 가능한 한 길게 작성해야 합니다.
강의에 포함되는 각 정보에 대해, 당신은 $20의 팁을 받게 됩니다.
강의에서 모든 낯선 용어나 주제는 학생들의 이해를 돕기 위해 설명되어야 합니다.
강의에서는 학생들이 주제에 대해 사전 지식이 없다고 가정합니다.
강의에서 강사는 불필요하게 자신을 반복해서는 안 됩니다.
강의는 마크다운 형식으로 되어야 합니다.
강의는 <lecture></lecture> 태그로 둘러싸여야 합니다.
""",
    "extract": lambda raw: (
        raw.split("<lecture>")[-1].split("</lecture>")[0].strip()
    )
},
# {
#     "dataset": "code",
#     "prompt": lambda passage: f"""
# 다음의 글을 고려해주세요: <passage_42>{passage}</passage_42>
# 높은 평가를 받는 컴퓨터 과학 교수로서 프로그래밍 교과서를 작성한다고 상상해보세요.
# 세 가지 작업이 있습니다:
# 1) 글의 내용에서 영감을 얻어 새로운 교과서 섹션 주제를 구상하세요.
# 생성된 섹션 주제는 글의 도메인과 동일하지만, 더욱 드물어야 합니다.
# 생성된 섹션 주제는 흥미롭고, 복잡하며, 다면적이어야 하며, 글이 단순하더라도 마찬가지입니다.
# 생성된 섹션 주제는 컴퓨터 과학과 직접적으로 관련되어야 합니다.
# 생성된 섹션 주제는 독자에게 최대한의 교육적 가치를 제공하기 위해 신중하게 선택되어야 합니다.
# 섹션 주제는 <topic_42></topic_42> 태그로 둘러싸여야 합니다.
# 2) 생성된 주제에 대한 코드를 포함하는 10가지 항목의 섹션 개요를 생성하세요.
# 섹션 개요의 10가지 항목 중 최소 3가지는 주제를 설명하는 코드 예제를 포함해야 합니다.
# 섹션 개요의 10가지 항목은 이해와 흐름을 극대화하기 위해 선택되어야 합니다.
# 섹션 개요는 <outline_42></outline_42> 태그로 둘러싸여야 합니다.
# 3) 개요에 따라 생성된 주제에 대한 교과서 섹션을 생성하세요.
# 섹션은 독립적이며, 정보를 많이 담고 이해하기 쉽고 장황해야 합니다.
# 섹션은 장문의 산문으로 작성되어야 합니다.
# 섹션에 포함되는 각 정보에 대해, 당신은 $20의 지불을 받게 됩니다; 따라서 수입을 극대화하기 위해 가능한 많은 정보를 포함하세요.
# 섹션에서는 독자의 이해를 돕기 위해 모든 낯선 용어나 주제를 설명해야 합니다.
# 섹션에서는 정보나 코드를 반복해서는 안 됩니다.
# 섹션은 마크다운 형식으로 되어야 합니다.
# 섹션은 <section_42></section_42> 태그로 둘러싸여야 합니다.
# """,
#     "extract": lambda raw: (
#         raw.split("<section_42>")[-1].split("</section_42>")[0].strip()
#     )}
]

# Gemini API query
async def llm_query(session, query):
    async with session.post(GEMINI_BASE + GEMINI_API_KEY, json={
        "contents": [{
            "role": "USER",
            "parts": [{"text": query}]
        }],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "topP": TOP_P
        }
    }) as resp:
        return (await resp.json())["candidates"][0]["content"]["parts"][0]["text"]

async def llm_template_query(sess, template, passage):
    query = template["prompt"](passage).strip()
    response = await llm_query(sess, query)
    return template["extract"](response)

# Fetch data from the server
async def fetch_data_from_server():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                response = await session.get(SERVER_URL + '/job')
                if response.status == 200:
                    data = await response.json()
                    global job_id
                    job_id = data['job_id']
                    print(f"Job ID: {job_id}, 총 {len(data['job_data'])}개의 작업을 수행합니다.")
                    return data['job_data']
                else:
                    print(f"Error from server: Status {response.status}")
            except Exception as e:
                print(f"Error connecting to server: {e}")
                print("현재 서버와 연결할 수 없거나 서버에 대기 중인 작업이 없습니다. 20초 후에 다시 시도합니다.")
                await asyncio.sleep(20)

async def fetch_and_process_data(item, session):
    template = TEMPLATES[secrets.randbits(64) % len(TEMPLATES)]
    try:
        return await asyncio.wait_for(
            llm_template_query(session, template, item["instruction"]), 
            60
        )
    except asyncio.TimeoutError:
        return f"Timeout for item {item}"
    except Exception as e:
        return f"Error for item {item}: {str(e)}"

async def main():
    while True:
        job_data = await fetch_data_from_server()
        results = []
        tasks = []
    
        async with aiohttp.ClientSession() as sess:
            for item in job_data:
                task = asyncio.create_task(fetch_and_process_data(item, sess))
                tasks.append(task)
                await asyncio.sleep(1)
    
            results = await asyncio.gather(*tasks)
    
            async with sess.post(SERVER_URL + '/job', json={"job_result": results, "auth_key": "abcd", "job_id": job_id}) as response:
                print(await response.json())

asyncio.run(main())
