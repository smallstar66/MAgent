import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["TOGETHER_API_KEY"] = '2dde51635fbb84097198ddb134f5b04d580a467bc973e56ee9b340759336cb97'
os.environ["LANGSMITH_API_KEY"] = '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'
# os.environ["OPENAI_API_KEY"] = ''

from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes

# 1. Create prompt template
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# 2. Create model
# model = ChatOpenAI()
model = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.environ["TOGETHER_API_KEY"],
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

# 3. Create parser
parser = StrOutputParser()

# 4. Create chain
chain = prompt_template | model | parser


# 4. App definition
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 5. Adding chain route
add_routes(
    app,
    chain,
    path="/chain",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)