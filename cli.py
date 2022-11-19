"""Chat bot CLI.

Usage:
    python cli.py --user-name Brendan --prompt-file chatbots/assistant.txt

Type "exit" to end the chat.
"""
import sys
import traceback
from typing import Dict

import click
import diskcache
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from settings import Settings
from oai_client import OAIClient
import utils


# Update PROMPT_CONFIG to customize your experience.
PROMPT_CONFIG = {
    "model": "text-davinci-002",
    "temperature": 0.7,
    "max_tokens": 50,
    "logit_bias": {198: -100},  # Prevent "\n" from being generated
}

def get_prompt_config(user_name: str, agent_name: str) -> Dict:
    """Get prompt config for chatbot.

    What this does:
    - Handles adding stop tokens based on user/agent names
    - Prevents newlines from being generated (you can disable this if you want)
    - Returns a copy of PROMPT_CONFIG with your custom params.
    """
    params = PROMPT_CONFIG.copy()
    params["stop"] = ["\n", f"{user_name}:", f"{agent_name}:"]
    print(params)
    return params


@click.command()
@click.option(
    "--prompt-file",
    default="chatbots/assistant.txt",
    help="Path to your customized prompt.txt file",
)
@click.option(
    "--secrets-file",
    default=".env.secret",
    help="Path to .env.secrets file with env variables"
)
@click.option(
    "--user-name",
    default="Human",
    help="First name of user.",
)
@click.option(
    "--agent-name",
    default="Assistant",
    help="First name of agent.",
)
@click.option(
    "--chat-id",
    help="Unique id for the chat (allows loading/testing historical chat). If provided, other arguments are ignored.",
)
@click.option(
    "--chat-name",
    default="test_chat",
    help="Unique-ish name for the chat (allows loading/testing historical chat). Not required if chat_id is provided.",
)
def chat(
    prompt_file: str,
    secrets_file: str,
    user_name: str,
    agent_name: str,
    chat_id: str,
    chat_name: str,
):
    """Run a chat session with the Agent."""
    ctx = Settings.from_env_file(secrets_file)

    cache = diskcache.Cache(directory=ctx.disk_cache_dir)
    oai_client = OAIClient(
        ctx.openai_api_key,
        organization_id=ctx.openai_org_id,
        cache=cache,
    )
    prompt_config = get_prompt_config(
        user_name=user_name, agent_name=agent_name
    )
    opening_line, prompt_text = utils.get_prompt_text(
        prompt_file=prompt_file, user_name=user_name, agent_name=agent_name
    )

    style = utils.get_default_style()
    session = utils.init_prompt_session(
        prompt_history_path=ctx.prompt_history_path, style=style
    )
    write_text = utils.get_write_text_fn(agent_name, "agent")

    # Load historical chat if available
    turns = []
    if chat_id is not None:
        turn_dict = utils.load_turns(chat_id=chat_id, turns_dir=ctx.chat_turns_dir)
        turns = turn_dict["turns"]
        click.echo(utils.build_transcript(turns))
        user_name = turn_dict["user_name"]
    else:
        chat_id = utils.make_chat_id(chat_name)
        click.echo(f"Chat Id: {chat_id}")
        write_text(opening_line)
        turns.append({"speaker": "agent", "text": opening_line})

    exit_loop = False
    while not exit_loop:
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{user_name}</user-prompt>: ")
        )
        if user_text.strip():
            try:
                if user_text.strip().lower() in ["exit", "quit"]:
                    exit_loop = True
                    utils.handle_end_chat(turns, user_name, write_text)
                else:
                    turns.append({"speaker": "user", "text": user_text})
                    agent_text = utils.chat_prompt(
                        turns=turns,
                        user_name=user_name,
                        agent_name=agent_name,
                        prompt_text=prompt_text,
                        prompt_config=prompt_config,
                        oai_client=oai_client,
                    )

                    write_text(agent_text)
                    turns.append({"speaker": "agent", "text": agent_text})
            except Exception as e:
                click.echo(e)
                traceback.print_exc(file=sys.stdout)

    utils.save_turns(
        chat_id=chat_id,
        turns=turns,
        user_name=user_name,
        agent_name=agent_name,
        turns_dir=ctx.chat_turns_dir,
    )


if __name__ == "__main__":
    chat()
