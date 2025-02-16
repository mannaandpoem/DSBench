import argparse
import os
import autogen
from autogen.coding import LocalCommandLineCodeExecutor

import json
import base64
import time
import pandas as pd
from tqdm import tqdm



parser = argparse.ArgumentParser(description="Process samples and save outputs.")
parser.add_argument("--save_name", type=str, default="gpt-4o", help="Directory to save processed outputs.")
args = parser.parse_args()
model = args.save_name

config_list = autogen.config_list_from_json(
    "../../../OAI_CONFIG_LIST"
)
print(config_list)

def gpt_tokenize(string: str, encoding) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens

def find_jpg_files(directory):
    jpg_files = [file for file in os.listdir(directory) if file.lower().endswith('.jpg') or file.lower().endswith('.png')]
    return jpg_files if jpg_files else None

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def find_excel_files(directory):
    jpg_files = [file for file in os.listdir(directory) if (file.lower().endswith('xlsx') or file.lower().endswith('xlsb') or file.lower().endswith('xlsm')) and not "answer" in file.lower()]
    return jpg_files if jpg_files else None

def read_excel(file_path):
    # 读取Excel文件中的所有sheet
    xls = pd.ExcelFile(file_path)
    sheets = {}
    for sheet_name in xls.sheet_names:
        sheets[sheet_name] = xls.parse(sheet_name)
    return sheets

def dataframe_to_text(df):
    # 将DataFrame转换为文本
    text = df.to_string(index=False)
    return text

def combine_sheets_text(sheets):
    # 将所有sheet的文本内容组合起来
    combined_text = ""
    for sheet_name, df in sheets.items():
        sheet_text = dataframe_to_text(df)
        combined_text += f"Sheet name: {sheet_name}\n{sheet_text}\n\n"
    return combined_text

def read_txt(path):
    with open(path, "r") as f:
        return f.read()

def truncate_text(text, max_tokens=128000):
    # 计算当前文本的token数
    tokens = text.split()
    if len(tokens) > max_tokens:
        # 截断文本以确保不超过最大token数
        text = ' '.join(tokens[-max_tokens:])
    return text


samples = []
with open("./data.json", "r") as f:
    for line in f:
        samples.append(eval(line.strip()))
len(samples)

def filter_data(data, keep_names):
    return [d for d in data if d["name"] in keep_names]


keep_ids = ["00000029", "00000004", "00000034", "00000036", "00000001"]
filter_samples = []
for sample in samples:
    if sample["id"] in keep_ids:
        filter_samples.append(sample)
samples = filter_samples

print(f"Total samples: {len(samples)}")
# create an AssistantAgent named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 41,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
    },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        # the executor to run the generated code
        "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
    },
)
chat_res = user_proxy.initiate_chat(
    assistant,
    message="""What is the current path?""",
)

print(chat_res)
