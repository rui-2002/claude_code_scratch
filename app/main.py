import argparse
import os
import sys
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")



def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


    messages=[{"role":"user","content":args.p}]
    

    while(True):

        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            max_tokens=512,
            tools=[{
                "type": "function",
                "function": {
                    "name": "Read",
                    "description": "Read and return the contents of a file",
                    "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                        "type": "string",
                        "description": "The path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                    }
                }
                },
                {
                "type": "function",
                "function": {
                    "name": "Write",
                    "description": "Write content to a file",
                    "parameters": {
                    "type": "object",
                    "required": ["file_path", "content"],
                    "properties": {
                        "file_path": {
                        "type": "string",
                        "description": "The path of the file to write to"
                        },
                        "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                        }
                    }
                    }
                }
                }]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        response=chat.choices[0].message

        tool_calls_list=[]

        if not response.tool_calls:
            print(response.content)
            break


        if response.tool_calls:
            for tc in response.tool_calls:
                tool_calls_list.append({
                    
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    
                })

        messages.append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": tool_calls_list if tool_calls_list else None
        })

        

        for tool_call in response.tool_calls:
            print("Tool call exists !!!", file=sys.stderr)
            print("Tool call function name :", tool_call.function.name, file=sys.stderr)



            if tool_call.function.name=="Read":
                print("Tool call function arguments :", tool_call.function.arguments, file=sys.stderr)
                print("Tool call function arguments type :", type(tool_call.function.arguments), file=sys.stderr)

                tool_args = json.loads(tool_call.function.arguments)
                file_path = tool_args["file_path"]

                print("Parsed arguments type :", type(tool_args), file=sys.stderr)
                print("File path :", file_path, file=sys.stderr)

                with open(file_path, "r") as f:
                    file_content = f.read()

            elif tool_call.function.name=="Write":
                tool_args=json.loads(tool_call.function.arguments)
                file_path=tool_args["file_path"]
                content=tool_args["content"]
                print("File path :", file_path, file=sys.stderr)
                with open(file_path,"w") as f:
                    f.write(content)
                file_content="File written successfully."

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": file_content
            })

        
if __name__ == "__main__":
    main()
