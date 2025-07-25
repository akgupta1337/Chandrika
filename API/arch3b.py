import re
import json
from typing import Any, Dict, List
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(load_in_8bit=True)

model_name = "katanemo/Arch-Function-3B"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True,
    quantization_config=bnb_config,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Please use our provided prompt for best performance
TASK_PROMPT = """
You are a helpful assistant.
""".strip()

TOOL_PROMPT = """
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tool_text}
</tools>
""".strip()

FORMAT_PROMPT = """
For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
""".strip()

play_playlist_api = {
    "type": "function",
    "function": {
        "name": "play_playlist",
        "description": "Plays a predefined playlist. Available options: gym, love, dance, sad, spiritual.",
        "parameters": {
            "type": "object",
            "properties": {
                "playlistname": {
                    "type": "str",
                    "description": "Choose one of the predefined playlists: gym, love, dance, sad or spiritual.",
                }
            },
            "required": ["playlistname"],
        },
    },
}

play_song_api = {
    "type": "function",
    "function": {
        "name": "play_song",
        "description": "Plays a specific song by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "song_name": {
                    "type": "str",
                    "description": "Name of the song to play.",
                }
            },
            "required": ["song_name"],
        },
    },
}

pause_song_api = {
    "type": "function",
    "function": {
        "name": "pause_song",
        "description": "Pauses the currently playing song.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

resume_song_api = {
    "type": "function",
    "function": {
        "name": "resume_song",
        "description": "Resumes the currently paused song.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

play_next_song_api = {
    "type": "function",
    "function": {
        "name": "play_next_song",
        "description": "Skips to the next song in the playlist or queue.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

play_previous_song_api = {
    "type": "function",
    "function": {
        "name": "play_previous_song",
        "description": "Plays the previous song from the playlist or queue.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

set_todo_and_reminder_api = {
    "type": "function",
    "function": {
        "name": "set_todo_and_reminder",
        "description": "Set a todo or task reminder for a specific time and date.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "str",
                    "description": "The name of the task or todo item.",
                },
                "description": {
                    "type": "str",
                    "description": "Additional details or description about the task.",
                },
                "time": {
                    "type": "str",
                    "description": "Specific time for the task (e.g., '5:00 PM', '14:30', '9 AM').",
                },
                "date": {
                    "type": "str",
                    "description": "The date for the task. Accepts 'today', 'tomorrow', weekdays (e.g., 'Monday'), or specific dates.",
                    "default": "today",
                },
            },
            "required": ["task_name", "description", "time"],
        },
    },
}

get_weather_updates_api = {
    "type": "function",
    "function": {
        "name": "get_weather_updates",
        "description": "Fetches weather information for a specific day.",
        "parameters": {
            "type": "object",
            "properties": {
                "day": {
                    "type": "str",
                    "description": "The day to get the weather for. Accepts natural language like 'today', 'tomorrow', weekdays (e.g., 'Friday').",
                    "default": "today",
                },
            },
        },
    },
}

get_news_updates_api = {
    "type": "function",
    "function": {
        "name": "get_news_updates",
        "description": "Fetches the latest news summary based on a specific topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "str",
                    "description": "Keywords or a phrase to search for.",
                    "default": "india",
                },
            },
        },
    },
}

do_web_search_api = {
    "type": "function",
    "function": {
        "name": "doWebSearch",
        "description": "Performs a general-purpose web search for any topic or question.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "str",
                    "description": "The topic or question to search for online (e.g., 'who is Alan Turing', 'Python vs Java').",
                },
            },
            "required": ["user_query"],
        },
    },
}

handle_music_api = {
    "type": "function",
    "function": {
        "name": "handleMusic",
        "description": "Handles all music-related operations like play, pause, resume, next, previous, playlists, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "str",
                    "description": "The original user input related to music request (e.g., play a sad song, pause the song, etc.).",
                },
            },
            "required": ["user_query"],
        },
    },
}

base_web_search_api = {
    "type": "function",
    "function": {
        "name": "doWebSearch",
        "description": "Handles all general-purpose web queries including Wikipedia, news, and weather.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "str",
                    "description": "The original question or topic to search (e.g., today's weather, news about India, who is Alan Turing).",
                },
            },
            "required": ["user_query"],
        },
    },
}

manage_tasks_api = {
    "type": "function",
    "function": {
        "name": "manageTasks",
        "description": "Handles todos and reminders.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "str",
                    "description": "The user's request for a task, such as setting a reminder or todo.",
                },
            },
            "required": ["user_query"],
        },
    },
}

musicTools = [
    play_playlist_api,
    play_song_api,
    pause_song_api,
    resume_song_api,
    play_next_song_api,
    play_previous_song_api,
]

taskTools = [
    set_todo_and_reminder_api,
]

webTools = [
    get_weather_updates_api,
    get_news_updates_api,
    do_web_search_api,
]

baseTools = [
    handle_music_api,
    base_web_search_api,
    manage_tasks_api,
]


def convert_tools(tools: List[Dict[str, Any]]):
    return "\n".join([json.dumps(tool) for tool in tools])


# Helper function to create the system prompt for our model
def format_prompt(tools: List[Dict[str, Any]]):
    tool_text = convert_tools(tools)

    return (
        TASK_PROMPT
        + "\n\n"
        + TOOL_PROMPT.format(tool_text=tool_text)
        + "\n\n"
        + FORMAT_PROMPT
        + "\n"
    )


def get_function_info(userQuery, tools):
    system_prompt = format_prompt(tools)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": userQuery},
    ]

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        inputs,
        max_new_tokens=256,
        do_sample=False,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )

    response = tokenizer.decode(outputs[0][len(inputs[0]) :], skip_special_tokens=True)
    print(response)
    return response


def get_summary(context, prompt):
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "user", "content": context},
    ]

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        inputs,
        max_new_tokens=256,
        do_sample=False,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )

    response = tokenizer.decode(outputs[0][len(inputs[0]) :], skip_special_tokens=True)
    print(response)
    return response


def parse_function_response(response):
    match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", response, re.DOTALL)
    if match:
        try:
            payload = json.loads(match.group(1))
            return {
                "name": payload.get("name"),
                "arguments": payload.get("arguments", {}),
            }
        except json.JSONDecodeError:
            return response
    return response


def dummy():

    return {"function": "dummy", "arguments": {}}


def doWebSearch(user_query):

    return call_tool(webTools, user_query)


def handleMusic(user_query):

    return call_tool(musicTools, user_query)


def manageTasks(user_query):

    return call_tool(taskTools, user_query)


tool_registry = {
    # Base Tools
    "handleMusic": handleMusic,
    "doWebSearch": doWebSearch,
    "manageTasks": manageTasks,
    # Web Search Tools
    "get_weather_updates": dummy,
    "get_news_updates": dummy,
    # Music Tools
    "play_playlist": dummy,
    "play_song": dummy,
    "pause_song": dummy,
    "resume_song": dummy,
    "play_next_song": dummy,
    "play_previous_song": dummy,
    # Task Tools
    "set_todo_and_reminder": dummy,
}


def call_tool(tools, user_query):
    response = get_function_info(user_query, tools)
    tool_info = parse_function_response(response)
    function_name = tool_info["name"]
    if function_name in tool_registry:
        return tool_info
    else:
        print(f"Special Function '{function_name}' not found.")
        return {"name": "null", "arguments": {}}


def route_query(query):
    base_response = get_function_info(query, baseTools)
    tool_info = parse_function_response(base_response)

    function_name = tool_info["name"]
    arguments = tool_info["arguments"]

    if function_name in tool_registry:
        result = tool_registry[function_name](**arguments)
        return {
            "name": result.get("name", "null"),
            "arguments": result.get("arguments", {}),
        }
    else:
        print(f"Base Function '{function_name}' not found.")
        return {"name": "null", "arguments": {}}
