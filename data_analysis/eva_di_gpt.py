#!/usr/bin/env python
# coding: utf-8
import asyncio
import os
from metagpt.roles.di.data_interpreter import DataInterpreter

import json
import base64

import time
import pandas as pd
from tqdm.notebook import tqdm


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


MODEL_LIMITS = {
    "gpt-3.5-turbo-0125": 16_385,
    "gpt-4-turbo-2024-04-09": 128_000,
    "gpt-4o-2024-05-13": 128_000,
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
}

# The cost per token for each model input.
MODEL_COST_PER_INPUT = {
    "gpt-3.5-turbo-0125": 0.0000005,
    "gpt-4-turbo-2024-04-09": 0.00001,
    "gpt-4o-2024-05-13": 0.000005,
    "gpt-4o": 0.0000025,# 2.5
    "gpt-4o-mini": 0.00000015,# 0.150
}

# The cost per token for each model output.
MODEL_COST_PER_OUTPUT = {
    "gpt-3.5-turbo-0125": 0.0000015,
    "gpt-4-turbo-2024-04-09": 0.00003,
    "gpt-4o-2024-05-13": 0.000015,
    "gpt-4o": 0.000010,#10.00
    "gpt-4o-mini": 0.00000060,#0.600
}


samples = []
with open("./data.json", "r") as f:
    for line in f:
        samples.append(eval(line.strip()))
len(samples)


# start = time.time()
# consume = time.time() - start

async def get_response(text):
    di = DataInterpreter()
    chat_res = await di.run(text)

    return chat_res


model = "gpt-4o"
eval_instance_num = 3
total_cost = 0

# keep_ids = ["00000029", "00000004", "00000034", "00000036", "00000001"]
keep_ids = ["00000029", "00000004", "00000034", "00000036"]
filter_samples = []
for sample in samples:
    if sample["id"] in keep_ids:
        filter_samples.append(sample)
samples = filter_samples
for id in tqdm(range(len(samples))):
    sample =samples[id]
    if len(sample["questions"]) > 0:

        image = find_jpg_files(os.path.join("./data", sample["id"]))

        
        excels = find_excel_files(os.path.join("./data", sample["id"]))


        introduction = read_txt(os.path.join("./data", sample["id"], "introduction.txt"))
        questions = []
        for question_name in sample["questions"]:
            questions.append(read_txt(os.path.join("./data", sample["id"], question_name+".txt")))
        
    
        
        text = f"The introduction is detailed as follows. \n {introduction}" 
        if excels:
            text += "\n \n The worksheet can be obtained in the path: "
            for excel in excels:
                text += f" {os.path.join('./data',  sample['id'], excel)}"
    
        if image:
            text += f"\n The image can be obtained in the path: {os.path.join('./data',  sample['id'], image[0])} \n"
        
        question_content = ""    
        # print(workbooks)
        answers = []
        all_mess = []
        for question in tqdm(questions):
            # question_content += question
    
            all_context = text + f"The question is detailed as follows. \n {question} \nPlease answer the question. "
            input_t = all_context
            # input_t = truncate_text(all_context, 2000)
            start = time.time()
            cost = 0
            prompt_tokens = completion_tokens = 0
            response = ""
            try:
                rst = asyncio.run(get_response(input_t))
                response = rst.content
            except Exception as e:
                print(e)
                time.sleep(3)

                # cost = 0
                history = "I cannot solve this task."
                summary = "I cannot solve this task."
                # all_mess.append("I cannot solve this task.")
            total_cost += cost
            print("Total cost: ", total_cost)
            answers.append({"id": sample["id"], "model": model, "input": prompt_tokens,
                            "output": completion_tokens, "cost": cost, "time": time.time()-start, "response": response})
            # break
    save_path = os.path.join("./save_process", model+"-di")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(os.path.join(save_path, sample['id'] + ".json"), "w") as f:
        for answer in answers:
            json.dump(answer, f)
            f.write("\n")
