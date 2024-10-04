from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from typing import List
import os
import json, time
from extra_provider_api import make_firworks_call
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchParameter(BaseModel):
    search_parameter: str
    context: str



def make_chain_call(llm, search_parameter):

    print(search_parameter.search_parameter)
    print(search_parameter.context)
    system = """
    You are  an experienced legal research assistant, you are tasked with analyzing 
    how the provided "context" is related to the search parameter "search_parameter" 
    Your task is to write  a short,concise paragraphs (with atleast three sentences) outlining how the "context" is related to the search parameter, so that your boss can easily understand if "context" is worth spending time. Include facts, names, dates, and other relevant information, in your answer, so that your boss can have most useful facts, and reasons at once. Keep the reasons very concise, and to the point, so that your boss can quickly understand the relevance of the context to the search parameter, but it should be informative enough to give a clear picture of the context. Return a list of single paragraph answer."""
    human = f"The search parameter is {search_parameter.search_parameter} and the context is {search_parameter.context} Analyze carefully, and write how the context is related to the search parameter"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm
    return chain.invoke({"text": search_parameter.search_parameter, "context": search_parameter.context})


@app.post("/analyze", response_class=StreamingResponse)
async def analyze(search_parameter: SearchParameter):
    try:

        start_time = time.time()
        # Call the ChatGroq API
        # chat = ChatGroq(
        #     temperature=0,
        #     groq_api_key=GROQ_API_KEY,
        #     model_name="llama3-8b-8192",
        #     streaming=True,
        # )
        chat = ChatOpenAI(model = "gpt-4o-mini")

        res = make_chain_call(chat,search_parameter)
        end_time = time.time()
        print(f"Time taken: {end_time-start_time} and used Groq")
        answer = res.dict()['content'].split(":\n\n")[-1]
       
        return Response(content=json.dumps(answer), media_type="application/json")
    except Exception as e:
        res = make_firworks_call(search_parameter.context,search_parameter.search_parameter)
        
        
        end_time = time.time()
        print(f"Time taken: {end_time-start_time} and used Fire Works")
        answer = res.json()['choices'][0]['message']['content']
        return Response(content=json.dumps(answer), media_type="application/json")
        
            # return Response(content=[], media_type="application/json")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)
