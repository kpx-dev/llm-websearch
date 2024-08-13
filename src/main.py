import logging
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def websearch(query):
  return {"result": "Here is your answer..."}

def generate_text(bedrock_client, model_id, tool_config, input_text):
    logger.info("Generating text with model %s", model_id)

    messages = [{"role": "user", "content": [{"text": input_text}]}]
    response = bedrock_client.converse(modelId=model_id, messages=messages, toolConfig=tool_config)
    output_message = response['output']['message']
    messages.append(output_message)
    stop_reason = response['stopReason']

    if stop_reason == 'tool_use':
      tool_requests = response['output']['message']['content']
      for tool_request in tool_requests:
        if 'toolUse' in tool_request:
          tool = tool_request['toolUse']

          if tool['name'] == 'websearch':
            websearch_res = websearch(tool['input']['query'])
            tool_result = {
              "toolUseId": tool['toolUseId'],
              "content": [{"json": {"results": websearch_res}}]
            }
            tool_result_message = {
              "role": "user",
              "content": [
                {
                  "toolResult": tool_result
                }
              ],

            }
            messages.append(tool_result_message)

            response = bedrock_client.converse(
                modelId=model_id,
                messages=messages,
                toolConfig=tool_config,

            )
            output_message = response['output']['message']

    # print the final response from the model.
    for content in output_message['content']:
      print(json.dumps(content, indent=4))

def main():
  logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
  model_id = "anthropic.claude-3-haiku-20240307-v1:0"

  with open("prompt/system-prompt.txt") as f:
    system_prompt = f.read()

  with open("prompt/user-prompt.txt") as f:
    user_prompt = f.read()

  tool_config = {
    # force tool use
    "toolChoice": {"tool": {"name": "websearch"}},
    "tools": [{
      "toolSpec": {
          "name": "websearch",
          "description": "Search the web for data.",
          "inputSchema": {
              "json": {
                  "type": "object",
                  "properties": {
                      "query": {
                        "type": "string",
                        "description": "The query to send to search engine."
                      }
                  },
                  "required": [
                    "query"
                  ]
              }
          }
      }
      }
    ]
  }
  bedrock_client = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")

  try:
    generate_text(bedrock_client, model_id, tool_config, user_prompt)

  except ClientError as err:
    message = err.response['Error']['Message']
    logger.error("A client error occurred: %s", message)
    print(f"A client error occured: {message}")
  else:
    print(f"Finished generating text with model {model_id}.")

if __name__ == "__main__":
  main()
