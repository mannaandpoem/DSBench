#!/usr/bin/env python
# coding: utf-8
import asyncio
import os
import argparse
import json
import base64
import time
import pandas as pd

from metagpt.llm import LLM
from metagpt.roles.di.data_interpreter import DataInterpreter

llm = LLM()
model = llm.model


def gpt_tokenize(string: str, encoding) -> int:
    """Returns the number of tokens in a text string."""
    return len(encoding.encode(string))


def find_jpg_files(directory):
    return [file for file in os.listdir(directory) if file.lower().endswith(('.jpg', '.png'))]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def find_excel_files(directory):
    return [file for file in os.listdir(directory) if
            file.lower().endswith(('xlsx', 'xlsb', 'xlsm')) and "answer" not in file.lower()]


def read_excel(file_path):
    xls = pd.ExcelFile(file_path)
    return {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}


def dataframe_to_text(df):
    return df.to_string(index=False)


def combine_sheets_text(sheets):
    return "\n\n".join(f"Sheet name: {sheet_name}\n{dataframe_to_text(df)}" for sheet_name, df in sheets.items())


def read_txt(path):
    with open(path, "r") as f:
        return f.read()


def truncate_text(text, max_tokens=128000):
    tokens = text.split()
    return ' '.join(tokens[-max_tokens:]) if len(tokens) > max_tokens else text


async def get_response(text):
    di = DataInterpreter()
    return await di.run(text)


async def process_sample(sample, save_path):
    answers = []
    introduction = read_txt(os.path.join("./data", sample["id"], "introduction.txt"))
    images = find_jpg_files(os.path.join("./data", sample["id"]))
    excels = find_excel_files(os.path.join("./data", sample["id"]))

    text = f"The introduction is detailed as follows.\n{introduction}\n\n"
    if excels:
        text += "\n".join(
            f"The worksheet can be found at: {os.path.join('./data', sample['id'], excel)}" for excel in excels)
    if images:
        text += f"The image can be found at: {os.path.join('./data', sample['id'], images[0])}\n"

    tasks = []
    for question_name in sample["questions"]:
        question_text = read_txt(os.path.join("./data", sample["id"], f"{question_name}.txt"))
        context = text + f"The question is detailed as follows.\n{question_text}\nPlease answer the question."
        tasks.append(asyncio.create_task(get_response(context)))

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    for response, question_name in zip(responses, sample["questions"]):
        if isinstance(response, Exception):
            response_text = "I cannot solve this task."
        else:
            response_text = response.content

        answers.append({
            "id": sample["id"],
            "model": model,
            "response": response_text,
            "question": question_name,
            "time": time.time()
        })

    os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path, f"{sample['id']}.json"), "w") as f:
        # json.dump(answers, f, indent=4)
        for answer in answers:
            json.dump(answer, f)  # 按行写入每个答案
            f.write("\n")  # 每个 JSON 对象一行

def main():
    parser = argparse.ArgumentParser(description="Process samples and save outputs.")
    parser.add_argument("--save_name", type=str, required=True, help="Directory to save processed outputs.")
    args = parser.parse_args()

    save_path = f"./save_process/{args.save_name}"
    with open("./data.json", "r") as f:
        samples = [eval(line.strip()) for line in f]

    keep_ids = ["00000029", "00000004", "00000034", "00000036", "00000001"]
    samples = [sample for sample in samples if sample["id"] in keep_ids]

    print(f"Processing {len(samples)} samples...")
    loop = asyncio.get_event_loop()
    tasks = [process_sample(sample, save_path) for sample in samples]
    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    main()
