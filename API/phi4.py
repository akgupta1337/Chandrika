# import json
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from transformers import BitsAndBytesConfig
# import re

# baseTools = [
#     {
#         "name": "handleMusic",
#         "description": "Handles all music-related operations like play, pause, resume, next, previous, playlists, etc.",
#         "parameters": {
#             "user_query": {
#                 "description": "The original user input related to music request (e.g., play a sad song, pause the song, etc.).",
#                 "type": "str",
#             }
#         },
#     },
#     {
#         "name": "doWebSearch",
#         "description": "Handles all general-purpose web queries including Wikipedia, news, and weather.",
#         "parameters": {
#             "user_query": {
#                 "description": "The original question or topic to search (e.g., today's weather, news about India, who is Alan Turing).",
#                 "type": "str",
#             }
#         },
#     },
#     {
#         "name": "manageTasks",
#         "description": "Handles todos and reminders.",
#         "parameters": {
#             "user_query": {
#                 "description": "The user's request for a task, such as setting a reminder or todo.",
#                 "type": "str",
#             }
#         },
#     },
# ]

# webSearchTools = [
#     {
#         "name": "get_weather_updates",
#         "description": "Fetches weather information for a specific day.",
#         "parameters": {
#             "day": {
#                 "description": "The day to get the weather for. Accepts natural language like 'today', 'tomorrow', weekdays (e.g., 'Friday').",
#                 "type": "str",
#                 "default": "today",
#             }
#         },
#     },
#     {
#         "name": "get_news_updates",
#         "description": "Fetches the latest news summary based on a specific topic.",
#         "parameters": {
#             "q": {
#                 "description": "Keywords or a phrase to search for. ",
#                 "type": "str",
#                 "default": "india",
#             }
#         },
#     },
#     {
#         "name": "search_wikipedia",
#         "description": "Search Wikipedia for information about any topic or question.",
#         "parameters": {
#             "query": {
#                 "description": "The question or topic to search for on Wikipedia.",
#                 "type": "str",
#             }
#         },
#     },
# ]


# musicTools = [
#     {
#         "name": "play_playlist",
#         "description": "Plays a predefined playlist. Available options: gym, love, dance, sad, spiritual.",
#         "parameters": {
#             "playlistname": {
#                 "description": "Choose one of the predefined playlists: gym, love, dance, sad or spiritual.",
#                 "type": "str",
#             }
#         },
#     },
#     {
#         "name": "play_song",
#         "description": "Plays a specific song by name.",
#         "parameters": {
#             "song_name": {
#                 "description": "Name of the song to play.",
#                 "type": "str",
#             }
#         },
#     },
#     {
#         "name": "pause_song",
#         "description": "Pauses the currently playing song.",
#         "parameters": {},
#     },
#     {
#         "name": "resume_song",
#         "description": "Resumes the currently paused song.",
#         "parameters": {},
#     },
#     {
#         "name": "play_next_song",
#         "description": "Skips to the next song in the playlist or queue.",
#         "parameters": {},
#     },
#     {
#         "name": "play_previous_song",
#         "description": "Plays the previous song from the playlist or queue.",
#         "parameters": {},
#     },
# ]


# taskTools = [
#     {
#         "name": "set_todo_and_reminder",
#         "description": "Set a todo or task reminder for a specific time and date.",
#         "parameters": {
#             "task_name": {
#                 "description": "The name of the task or todo item.",
#                 "type": "str",
#             },
#             "description": {
#                 "description": "Additional details or description about the task.",
#                 "type": "str",
#             },
#             "time": {
#                 "description": "Specific time for the task (e.g., '5:00 PM', '14:30', '9 AM').",
#                 "type": "str",
#             },
#             "date": {
#                 "description": "The date for the task. Accepts 'today', 'tomorrow', weekdays (e.g., 'Monday'), or specific dates.",
#                 "type": "str",
#                 "default": "today",
#             },
#         },
#     },
# ]
# prev_query = ""

# bnb_config = BitsAndBytesConfig(load_in_8bit=True)
# model_name = "microsoft/Phi-4-mini-instruct"
# model = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     torch_dtype="auto",
#     device_map={"": 0},
#     trust_remote_code=True,
#     quantization_config=bnb_config,
# )

# # load tokenizer
# tokenizer = AutoTokenizer.from_pretrained(
#     model_name, use_fast=True, trust_remote_code=True
# )
# print("Hello from Chandrika!")


# def get_model_response(
#     tools, query, system_prompt="You are a helpful assistant with some tools."
# ):
#     global prev_query
#     model.eval()

#     messages = [
#         {
#             "role": "system",
#             "content": system_prompt,
#             "tools": json.dumps(tools),
#         },
#         {
#             "role": "user",
#             "content": prev_query + query,
#         },
#     ]

#     text = tokenizer.apply_chat_template(
#         messages, tokenize=False, add_generation_prompt=True
#     )

#     model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

#     generated_ids = model.generate(
#         **model_inputs,
#         max_new_tokens=256,
#     )

#     generated_ids = [
#         output_ids[len(input_ids) :]
#         for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
#     ]

#     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     return response


# def get_general_response(query, system_prompt="You are a helpful assistant."):
#     model.eval()

#     messages = [
#         {
#             "role": "system",
#             "content": system_prompt,
#         },
#         {
#             "role": "user",
#             "content": query,
#         },
#     ]

#     text = tokenizer.apply_chat_template(
#         messages, tokenize=False, add_generation_prompt=True
#     )

#     model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

#     generated_ids = model.generate(
#         **model_inputs,
#         max_new_tokens=256,
#     )

#     generated_ids = [
#         output_ids[len(input_ids) :]
#         for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
#     ]

#     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     return response


# def parse_tool_call(response):
#     print(response)
#     try:
#         # First check for tool call tags
#         match = re.search(r"<\|tool_call\|>(.*?)<\|/tool_call\|>", response, re.DOTALL)
#         if match:
#             json_part = match.group(1)
#             tool_call = json.loads(json_part)[0]
#         else:
#             # Try to parse response as direct JSON array
#             tool_call = json.loads(response)[0]

#         function_name = tool_call.get("name") or tool_call.get("function", "null")
#         arguments = (
#             tool_call.get("arguments")
#             or tool_call.get("args")
#             or tool_call.get("parameters", {})
#         )
#         return {"function": function_name, "arguments": arguments}
#     except:
#         cleaned_response = re.sub(r"<\|/?tool_call\|>", "", response).strip()
#         return {
#             "function": "need_more_info",
#             "arguments": {"message": cleaned_response},
#         }


# def dummy():

#     return {"function": "dummy", "arguments": {}}


# def doWebSearch(user_query):

#     return call_tool(webSearchTools, user_query)


# def handleMusic(user_query):

#     return call_tool(musicTools, user_query)


# def manageTasks(user_query):

#     return call_tool(taskTools, user_query)


# tool_registry = {
#     # Base Tools
#     "handleMusic": handleMusic,
#     "doWebSearch": doWebSearch,
#     "manageTasks": manageTasks,
#     # Web Search Tools
#     "get_weather_updates": dummy,
#     "get_news_updates": dummy,
#     "search_wikipedia": dummy,
#     # Music Tools
#     "play_playlist": dummy,
#     "play_song": dummy,
#     "pause_song": dummy,
#     "resume_song": dummy,
#     "play_next_song": dummy,
#     "play_previous_song": dummy,
#     # Task Tools
#     "set_todo_and_reminder": dummy,
#     # extra info
#     "need_more_info": dummy,
# }


# def call_tool(tools, user_query):
#     global prev_query
#     response = get_model_response(
#         tools,
#         user_query,
#         "You are a helpful assistant with tools. Default day is today. Don't assume things, if any detail is missing ask for it.",
#     )

#     tool_info = parse_tool_call(response)

#     function_name = tool_info["function"]
#     if function_name == "need_more_info":
#         prev_query += user_query + " "
#     else:
#         prev_query = ""

#     if function_name in tool_registry:
#         return tool_info
#     else:

#         print(f"Function '{function_name}' not found.")

#         return {"function": "null", "arguments": {}}


# def chat(query):
#     response = get_model_response(baseTools, query)
#     tool_info = parse_tool_call(response)
#     function_name = tool_info["function"]
#     arguments = tool_info["arguments"]

#     if function_name in tool_registry:
#         result = tool_registry[function_name](**arguments)
#         return {
#             "function": result.get("function", "null"),
#             "arguments": result.get("arguments", {}),
#         }
#     else:
#         print(f"Function '{function_name}' not found.")
#         return {"function": "null", "arguments": {}}
