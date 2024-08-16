# from dotenv import load_dotenv
# load_dotenv()
import boto3
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError
from datetime import date
import wikipedia

session = boto3.Session()
region = session.region_name

# modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
modelId = 'anthropic.claude-3-haiku-20240307-v1:0'

print(f'Using modelId: {modelId}')
print(f'Using region: ', {region})

bedrock_client = boto3.client(service_name = 'bedrock-runtime', region_name = region)

def provider_websearch(query):
    print(f"implement websearch here...: {query}")
    # TODO: advance search, sort by last Edited?
    pages = wikipedia.search(query)
    # print(pages)
    # exit()

    # TODO: assume the 1st page is the best. Rerank?
    page1 = wikipedia.page(pages[0])
    page2 = wikipedia.page(pages[1])
    # page3 = wikipedia.page(pages[2])
    
    # print(res.url)
    payload = "{} \n {} \n".format(page1, page2)
    return payload 

    # return res.content

    # payload = {
    #     "title": res.title,
    #     "url": res.url,
    #     "content": res.content
    # }
    # return payload 

def provider_catch_all(query):
    print(f"Catch-all / fallback provider: {query}")

provider_websearch_schema = {
    "toolSpec": {
        "name": "provider_websearch",
        "description": "A tool to search the web for latest information.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that will be send to do websearch"}
            },
            "required": ["query"]
            }
        }
    }
}

provider_catch_all_schema = {
    "toolSpec": {
        "name": "provider_catch_all",
        "description": "A tool to handle any generic query that other previous tools can't answer.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that other previous tool doesn't understand."}
            },
            "required": ["query"]
            }
        }
    }
}

toolConfig = {
    "tools": [provider_websearch_schema],
    # "toolChoice": {
    #     "any":{},    # must trigger one of the available tools
    #     # "auto":{}, # default
    #     # "tool":{   # always trigger this tool
    #     #     "name": "provider_websearch"
    #     # },
    # }
}

def guardrails(prompt): 
    response = bedrock_client.apply_guardrail(
        guardrailIdentifier=os.environ.get('GUARDRAILS_ID'), # ex: '453cg26ykbxy'
        guardrailVersion='1',
        source='INPUT', #|'OUTPUT',
        content=[
            {
                'text': {
                    'text': prompt,
                    # 'qualifiers': [
                    #     'grounding_source'|'query'|'guard_content',
                    # ]
                }
            },
        ]
    )
    # print(response)
    return response 
    
def router(user_query, enable_guardrails=False):
    # apply guardrails 
    if enable_guardrails:
        guard = guardrails(user_query)
        if guard['action'] == 'GUARDRAIL_INTERVENED':
            print("Guardrails blocked this action", guard["assessments"])
            return

    messages = [{"role": "user", "content": [{"text": user_query}]}]

    system_prompt=f"""
          You will be asked a question by the user. 
    If answering the question requires data you were not trained on, you must use the get_article tool to get the contents of a recent wikipedia article about the topic. 
    If you can answer the question without needing to get more information, please do so. 
    Only call the tool when needed. 

    """

    converse_api_params = {
        "modelId": modelId,
        "system": [{"text": system_prompt}],
        "messages": messages,
        "inferenceConfig": {"temperature": 0.0, "maxTokens": 4096},
        "toolConfig": toolConfig,
    }

    response = bedrock_client.converse(**converse_api_params)

    stop_reason = response['stopReason']

    if stop_reason == "end_turn":
        print("Claude did NOT call a tool")
        print(f"Assistant: {stop_reason}")
    elif stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response['output']['message']['content']})
        # print("Claude wants to use a tool")
        # print(response['output'])

        # trigger the actual tool to use: 
        if response['output']['message']['content'][0]['toolUse']['name'] == 'provider_websearch': 
          tool_id = response['output']['message']['content'][0]['toolUse']['toolUseId']
          websearch_res = provider_websearch(response['output']['message']['content'][0]['toolUse']['input']['query'])

          tool_response = {
              "role": "user",
              "content": [
                  {
                      "toolResult": {
                          "toolUseId": tool_id,
                          "content": [
                              {"text": websearch_res}
                          ]
                      }
                  }
              ]
          }
          # print(tool_response)

          messages.append(tool_response)
          converse_api_params = {
                "modelId": modelId,
                "system": [{"text": system_prompt}],
                "messages": messages,
                "inferenceConfig": {"temperature": 0.0, "maxTokens": 4096},
                "toolConfig": toolConfig
          }
          # print("before final res")
          final_res = bedrock_client.converse(**converse_api_params)

          print("Claude's final answer:")
          print(final_res['output']['message']['content'][0]['text'])

        # print(response['usage'])
        # print(response['metrics'])
        

if __name__ == "__main__":
    # router("Why is the sky blue?")
    # router("Which countries have the most medal in the Olympic 2024?")
    # router("Who's the current President of the United States?")
    router("Who are the candidate running for US President in 2024?")
    