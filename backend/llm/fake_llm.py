from langchain.llms.fake import FakeListLLM

def get_fake_llm():
    return FakeListLLM(
        responses=[
            "This is a simulated LLM response for local development."
        ]
    )