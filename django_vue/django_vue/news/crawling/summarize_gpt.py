import json
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


class Summarizer:
    def __init__(self, model='gpt-4o-mini'):
        self.model = model

    def chat_completion_request(self, messages):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                # tools=self.tools,
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
            {"role": "system", "content": "입력으로 받는 정보 중 `content`는 뉴스는 이동통신 관련 단체들 간의 공동 연구 프로젝트로 국제전기통신연합(ITU)의 IMT-2000 프로젝트의 범위 내에서 - 전 세계적으로 적용 가능한 - 3세대 이동통신 시스템 규격의 작성을 목적으로 하는 3GPP 단체에서 발행한 기사입니다."},
            {"role": "system", "content": "해당 뉴스의 content를 요약해, 요약 정보만을 출력하세요."},
            {"role": "system", "content": """
            입력 중 `difficulty`는 요약의 수준을 나타냅니다. 입력에 따라 요약의 어려움을 설정해 주세요. 
            1) '전문가'의 입력이 들어오게 된다면, 단순한 요약을 해 주셔도 됩니다. 그들은 이해할 것입니다. 
            2) '학부생'의 입력이 들어오게 된다면, 그들은 기본적인 용어는 알테지만 구체적으로는 모를 것입니다. 약간의 설명을 부가해 주셔도 됩니다. 
            3) '일반인'이 들어오게 된다면, 그들은 처음 3GPP에 대해 들었을지도 모릅니다. 최대한 자세한 설명을 해 주세요.            
            """},
            {"role": "system", "content": "답변은 한국어로하세요."},
            {"role": 'user', "content": user_msg}
        ]

        return msg

    def use_chat_gpt_for_summarization(self, title, content, difficulty='일반인'):
        message = self.make_message(f"Title: {title}, \nContent: {content}, \nDifficulty: {difficulty}")

        chat_response = self.chat_completion_request(message)

        return chat_response.choices[0].message.content


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