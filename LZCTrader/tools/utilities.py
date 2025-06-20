import yaml
import re


def read_yaml(file_path: str) -> dict:
    """Function to read and extract contents from .yaml file.

    Parameters
    ----------
    file_path : str
        The absolute filepath to the yaml file.

    Returns
    -------
    dict
        The loaded yaml file in dictionary form.
    """
    with open(file_path, "r", encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_letters(instrument: str):
    # 匹配连续字母直到遇到数字
    match = re.match(r'^([a-zA-Z]+)\d+', instrument)
    return match.group(1) if match else None
