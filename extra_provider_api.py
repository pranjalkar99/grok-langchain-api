import requests
import json,os

from dotenv import load_dotenv

load_dotenv()

def make_firworks_call(search_parameter, context):

    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
      "model": "accounts/fireworks/models/llama-v3-70b-instruct",
      "max_tokens": 7024,
      "top_p": 1,
      "top_k": 40,
      "presence_penalty": 0,
      "frequency_penalty": 0,
      "temperature": 0.6,
      "messages": [
        {
            "role":"system",
            "content":'''You are  an experienced legal research assistant, you are tasked with analyzing 
    how the provided "context" is related to the search parameter "search_parameter" 
    Your task is to write  a short,concise paragraphs (with atleast three sentences) outlining how the "context" is related to the search parameter, so that your boss can easily understand if "context" is worth spending time. Include facts, names, dates, and other relevant information, in your answer, so that your boss can have most useful facts, and reasons at once. Keep the reasons very concise, and to the point, so that your boss can quickly understand the relevance of the context to the search parameter, but it should be informative enough to give a clear picture of the context. Return a list of single paragraph answer.'''
        },
        {
          "role": "user",
          "content": f"The search parameter is {search_parameter} and the context is {context} Analyze carefully, and write how the context is related to the search parameter"
        }
      ],
      "context_length_exceeded_behavior": "truncate"
    }
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": f"Bearer {os.environ['FIREWORKS_API_KEY']}"
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    return  response


# if __name__ == "__main__":

#     import time
#     start = time.time()
#     res = make_firworks_call("The Boundary Fire was a 2017 wildfire in Arizona that burned 17,788 acres (7,199 ha) of the Coconino and Kaibab National Forests. The fire was ignited on June 1 when lightning struck a spot on the northeast side of Kendrick Peak within the Coconino National Forest. The fire spread rapidly because of high temperatures, steep terrain, leftovers from a wildfire in 2000, and high wind speeds. The winds blew smoke over local communities and infrastructure, leading to the closure of U.S. Route 180 from June 8 to June 21. Smoke was also visible from the Grand Canyon. The Boundary Fire burned out on July 3, 2017, after 32 days of firefighting. The cost of managing the fire was $9.4 million (equivalent to $11.5 million in 2023). Damage to the area's foliage increased the risk of landslides into 2018. ", "fire at forests")
#     answer = res.json()['choices'][0]['message']['content']
#     print(answer)

#     print(f"It took {time.time() - start}")