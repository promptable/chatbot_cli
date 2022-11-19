"""Settings and secrets for the project."""
import os

import dotenv


class Settings:
    # (env_variable, is_required)
    SECRET_VARIABLES = [
        ("OPENAI_API_KEY", True),
        ("OPENAI_ORG_ID", False)
    ]
    def __init__(
        self,
        openai_api_key: str,
        openai_org_id: str = None, 
        disk_cache_dir: str = "/tmp/disk_cache",
        prompt_history_path = "./.prompt_history",
        chat_turns_dir = "./.chat_turns",
    ):
        self.openai_api_key = openai_api_key
        self.openai_org_id = openai_org_id
        self.disk_cache_dir = disk_cache_dir
        self.prompt_history_path = prompt_history_path
        self.chat_turns_dir = chat_turns_dir
        os.makedirs(chat_turns_dir, exist_ok=True)


    @classmethod
    def from_env_file(cls, env_file: str, **kwargs) -> "Settings":
        """Load secrets from a .env file.
        
        Other kwargs are passed to the Settings constructor.
        """
        cfg = dotenv.dotenv_values(env_file)
        for key, is_required in cls.SECRET_VARIABLES:
            if is_required and cfg.get(key) is None:
                raise ValueError(f"Missing required secret variable {key}")
        return cls(**cfg, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--secrets-file",
        required=True,
        help="path to .env.secrets file with env variables",
    )
    args = parser.parse_args()

    cfg = Settings.from_env_file(args.secrets_file)
    print(cfg)
    print(cfg.openai_api_key)
    print(cfg.openai_org_id)
    print(cfg.disk_cache_dir)
    print(cfg.prompt_history_path)
    print(cfg.chat_turns_dir)
