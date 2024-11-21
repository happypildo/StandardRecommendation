import json
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


class Summarizer:
    def __init__(self, model='gpt-4o-mini'):
        self.model = model

        self.descriptions = [
            """
            뉴스 기사의 제목에 해당합니다.
            """,
            """
            뉴스 기사의 본문입니다. 요약을 할 내용입니다. 해당 내용을 요약해 주시면 됩니다.
            다양한 내용이 포함될 수 있지만, 이동 통신 관련 단체들 간의 표준 단체인 3GPP에서 발간한 뉴스 기사라는 점을 명시하세요. 
            다소 어려운 용어나 내용이 포함되어 있을 수 있습니다. 다른 함수 파라미터를 참고해 잘 요약해 주시길 바랍니다.
            """,
            """
            요약의 수준을 나타냅니다. 입력에 따라 요약의 어려움을 설정해 주세요. 
            1) '전문가'의 입력이 들어오게 된다면, 단순한 요약을 해 주셔도 됩니다. 그들은 이해할 것입니다. 
            2) '학부생'의 입력이 들어오게 된다면, 그들은 기본적인 용어는 알테지만 구체적으로는 모를 것입니다. 약간의 설명을 부가해 주셔도 됩니다. 
            3) '일반인'이 들어오게 된다면, 그들은 처음 3GPP에 대해 들었을지도 모릅니다. 최대한 자세한 설명을 해 주세요.            
            """,
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "summarize_news",  # 함수 이름
                    "description": "뉴스 정보를 요약하는 함수입니다.",  # 함수 설명 (optional)
                    "parameters": {  # 함수 파라미터 지정
                        "type": "object",
                        "properties": {
                            "title": {  # 파라미터 명
                                "type": "string",  # 파라미터 타입
                                "description": self.descriptions[0],
                            },
                            "summarized_content": {
                                "type": "string",
                                "description": self.descriptions[1],
                            },
                            "difficulty":{
                                "type": "string",
                                'description': self.descriptions[2],
                            }
                        },
                        "required": ["title", "content", "difficulty"],  # 필수 파라미터 지정
                    },
                }
            }
        ]

    def summarize_news(self, title, summarized_content, difficulty='일반인'):
        return f"{summarized_content}."

    def chat_completion_request(self, messages):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def make_message(self, user_msg):
        msg = [
            {"role": "system", "content": "당신은 사용자 요청 답변하는 챗봇입니다."},
            {"role": "system", "content": "당신은 무선 및 유선 통신에서의 전문가입니다."},
            {"role": "system", "content": "사용할 함수의 값에 대해 추측하지 마세요. 사용자의 요청이 모호한 경우 명확히 물어보세요."},
            {"role": "system", "content": "답변은 한국어로하세요."},
            {"role": 'user', "content": user_msg}
        ]

        return msg

    def use_chat_gpt_for_summarization(self, title, content, difficulty='일반인'):
        message = self.make_message(f"Title: {title}, \nContent: {content}, \nDifficulty: {difficulty}")

        chat_response = self.chat_completion_request(message)
        assistance_message = chat_response.choices[0].message

        if assistance_message.tool_calls:
            for msg in assistance_message.tool_calls:
                if "function" in msg.type:
                    result = self.summarize_news(**json.loads(msg.function.arguments))

                    return result

        return "요약에 실패했습니다."


# summa = Summarizer()
# message = summa.use_chat_gpt_for_summarization(
#     title="5G Non-Terrestrial Networks",
#     content="""Just as the work in 3GPP is starting on Rel-19 Non-Terrestrial Networks (NTN), five leading contributors have released a new book on 5G NTN and beyond. Alessandro Vanelli-Coralli, Nicolas Chuberre, Gino Masini, Alessandro Guidotti, Mohamed El Jaafari are the authors of "5G Non-Terrestrial Networks: Technologies, Standards, and System Design" (Wiley-IEEE Press).
# Drawing from their expertise in their respective fields, the authors have covered recent developments in 3GPP Releases and at the definition of new work in Rel-19. The book covers different aspects of NTN including NR, NB-IoT & eMTC principles, use cases and system architecture.
# In Rel-19, the following NR and IoT areas are particularly important:
# Non-Terrestrial Networks (NTN) for NR Phase 3 (NR_NTN_Ph3)
# In Rel-17 and Rel-18 solutions enabling New Radio and NG-RAN to support Non-Terrestrial Networks (NTN) were defined.  As part of Rel-19, a new work item has been approved defining further improvements for:
# Optimized performance for terminals.
# Capacity performance on uplink.
# Notification of the service area of a Broadcast service.
# Support for a non-terrestrial network architecture with 5G system functions on board the NTN vehicle (i.e. regenerative payloads).
# Use of RedCap devices within FR1 NTN.
# Non-Terrestrial Networks (NTN) for Internet of Things (IoT) Phase 3
# With IoT-NTN specified in 3GPP RAN Rel-17, with optimizations following in Rel-18, commercial deployments are now ongoing. Now, further evolution of IoT-NTN is underway with a dedicated Rel-19 work item, focusing in on three areas:
# Support of Store & Forward (S&F) operation based on regenerative payload, including the support of feeder link switchover.
# Uplink capacity enhancements.
# The book also includes a comprehensive introduction to NTN, with the elements of a satellite communications system, orbits and constellations, technologies and challenges, related industrial projects, potential future developments, and others.
# According to Gino Masini, one of the five coauthors of 5G Non-Terrestrial Networks, "Working on this book while actively contributing in 3GPP was a big challenge for all of us, but I am confident that such a first-hand source of information will ultimately benefit the readers."
# The group of authors is representative of :the various parts of the 3GPP community, spanning different industries and academia: Alessandro Vanelli-Coralli and Alessandro Guidotti are Professors with the University of Bologna, Gino Masini (former 3GPP RAN3 Chair) is with Ericsson, and Nicolas Chuberre (NTN WI Rapporteur) and Mohamed El Jaafari are with Thales Alenia Space. All of them are active as standards delegates for their respective organizations, both within 3GPP WGs and TSGs  and outside the project.
# The book is available from Wiley-IEEE Press.
# Some background reading:
# Non-Terrestrial Networks (NTN) for NR Phase 3 (NR_NTN_Ph3, RP-234078)
# Non-Terrestrial Networks (NTN) for Internet of Things (IoT) Phase 3 (IoT_NTN_Ph3, RP-234077)"""
# )
# print(message)