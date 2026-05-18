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

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
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
            }]
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


    response=chat.choices[0].message

    if(response.tool_calls):
        print("Tool call exists !!!",file=sys.stderr)
        print("Tool call function name :",response.tool_calls[0].function.name,file=sys.stderr)
        print("Tool call function argumens :",response.tool_calls[0].function.arguments,file=sys.stderr)
        print("Tool call function argumens type :",type(response.tool_calls[0].function.arguments),file=sys.stderr)
        tool_args=json.loads(response.tool_calls[0].function.arguments)
        file_path=tool_args["file_path"]
        print("Tool call function argumens type :",type(tool_args),file=sys.stderr)

        with open(file_path,"r") as f:
            print(f.read())
    else:
        print("Doesn't Exist : NONE", file=sys.stderr)
        print(response.content)

    # print("=== FULL MESSAGE ===", file=sys.stderr)
    # print(chat.choices[0].message, file=sys.stderr)
    # print("=== TOOL CALLS ===", file=sys.stderr)
    # print(chat.choices[0].message.tool_calls, file=sys.stderr)
    # print("=== CONTENT ===", file=sys.stderr)
    # print(chat.choices[0].message.content, file=sys.stderr)
    # print("=== FINISH REASON ===", file=sys.stderr)
    # print(chat.choices[0].finish_reason, file=sys.stderr)

if __name__ == "__main__":
    main()
