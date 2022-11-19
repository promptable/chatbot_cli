"""Utility functions for the CLI interface."""
import html
import json
import os
import logging
import uuid
from typing import Callable, Dict, List, Tuple

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit import HTML
from prompt_toolkit import print_formatted_text as print

from oai_client import OAIClient


def get_default_style():
    return Style.from_dict(
        {
            "": "#ffffff",  # default
            "user-prompt": "#884444",
            "user-text": "#ffffff",
            "bot-prompt": "#00aa00",
            "bot-text": "#A9A9A9",
        }
    )


def get_default_completer():
    return NestedCompleter.from_nested_dict(
        {
            "show": {"history": None, "commands": {"interface": {"brief"}}},
            "clear": {
                "history": None,
            },
            "exit": None,
            "quit": None,
        }
    )


def init_prompt_session(prompt_history_path: str, style=None, completer=None):
    # https://python-prompt-toolkit.readthedocs.io/en/stable/pages/dialogs.html
    # Yes/No, or List of options, etc
    # https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html
    # Custom WordCompleter, FuzzyCompleter
    if style is None:
        style = get_default_style()
    if completer is None:
        completer = get_default_completer()

    kwargs = dict(
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        style=style,
    )
    if prompt_history_path:
        kwargs["history"] = FileHistory(prompt_history_path)

    return PromptSession(**kwargs)


def make_chat_id(chat_name: str):
    """Make a chat ID from a chat name.
    
    Used to restore a chat from a previous session.
    """
    return f"{chat_name}_{str(uuid.uuid1())[:8]}"


def save_turns(
    chat_id: str,
    turns: List[Dict],
    user_name: str,
    agent_name: str,
    turns_dir: str,
):
    """Save a chat transcript to disk.
    
    Used to restore a chat from a previous session.
    """
    fpath = os.path.join(turns_dir, chat_id + ".json")
    turns_dict = {
        "chat_id": chat_id,
        "turns": turns,
        "user_name": user_name,
        "agent_name": agent_name,
    }
    with open(fpath, "w") as f:
        json.dump(turns_dict, f)


def load_turns(chat_id: str, turns_dir: str) -> Dict:
    """Load a chat transcript from disk by chat_id."""
    fpath = os.path.join(turns_dir, chat_id + ".json")
    with open(fpath) as f:
        return json.load(f)


def get_line(line_name: str, user_name: str, agent_name: str):
    return LINES_TEXT[line_name].format(user_name=user_name, agent_name=agent_name)


def get_write_text_fn(speaker_name, prompt_tag):
    """Get a function that writes text to the console.

    Allows stylizing the CLI interface with colors, html.
    """
    style = get_default_style()

    def write_text(text):
        print(
            HTML(
                f"<{prompt_tag}-prompt>{speaker_name}</{prompt_tag}-prompt>: <{prompt_tag}-text>{html.escape(text)}</{prompt_tag}-text>"
            ),
            style=style,
        )

    return write_text


def handle_end_chat(turns_: List[Dict], user_name: str, write_text_fn: Callable):
    if turns_[-1]["speaker"] == "user":
        closing_line = get_line(line_name="closing", user_name=user_name)
        write_text_fn(closing_line)


def build_transcript(turns: List[Dict]) -> str:
    clean_lines = []
    for turn in turns:
        text = turn["text"].strip().replace("\n", " ")
        clean_lines.append(f"{turn['speaker'].capitalize()}: {text}")
    return "\n".join(clean_lines)


def chat_prompt(
    turns: List[Dict],
    user_name: str,
    agent_name: str,
    prompt_text: str,
    prompt_config: dict,
    oai_client: OAIClient
) -> str:
    transcript = build_transcript(turns)
    prompt_text = prompt_text.format(
        transcript=transcript, user_name=user_name, agent_name=agent_name
    )
    logging.debug("Prompt:\n{prompt_text}")
    result = oai_client.complete(
        prompt_text, request_tag=f"chat_turn[len(turns)]", **prompt_config
    )
    logging.debug("OAI Result:\n{result}")
    return result["top_answer_text"].strip()


def get_prompt_text(prompt_file: str, user_name: str, agent_name: str) -> Tuple[str, str]:
    """Get the prompt text from a file.

    Get the opening line from the top of the file.

    Syntax of the prompt.txt should be:

    <opening line>
    ######
    <prompt text>

    Variables {agent_name} and {user_name} will be replaced with the
    values passed to the chat CLI function.
    
    Strip access whitespace at the end, which is known to cause issues.
    """
    with open(prompt_file) as f:
        instructions = f.read()
    
    opening_line, prompt_text = instructions.split("######")

    opening_line = opening_line.lstrip("opening_line:").strip()
    opening_line = opening_line.format(user_name=user_name, agent_name=agent_name)

    return opening_line.strip(), prompt_text.rstrip()
