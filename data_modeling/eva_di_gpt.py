#!/usr/bin/env python
# coding: utf-8
import asyncio
import os
import json

import time

import argparse

from metagpt.roles.di.data_interpreter import DataInterpreter


# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="Run model tasks in parallel")
    parser.add_argument('--save_name', type=str, default="gpt-4o-di", help="Model to use (e.g., gpt-4o)")
    parser.add_argument('--data_file', type=str, default="./data.json", help="Data file to load")
    parser.add_argument('--save_path', type=str, default="./output_model/", help="Path to save the output")
    return parser.parse_args()


def load_data(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(eval(line))
    return data


def filter_data(data, keep_names):
    return [d for d in data if d["name"] in keep_names]


async def get_response(text):
    di = DataInterpreter()
    chat_res = await di.run(text)
    return chat_res


# 处理每个任务的逻辑
async def process_task(id, data, data_path, instruction, save_name, save_path):
    name = data[id]['name']
    with open(f"./data/task/{name}.txt", "r") as f:
        description = f.read()
    data_path = data_path.format(name=name)
    text = (
        f"\n \n All three data files can be found in the folder: {data_path}. After the data modeling, please give me the prediction resutls for the test file. You must"
        f" save the answer as a csv file. I won't run your code and you must run the code for the predicted results and give the submission file. The file should be saved in the path ./output_model/{save_name}/{name}.csv")

    all_context = instruction + "\n" + description + "\n" + text
    input_t = all_context

    start = time.time()
    cost = 0
    error = ""
    prompt_tokens = completion_tokens = 0
    try:
        # 异步获取响应
        rst = await get_response(input_t)
        response = rst.content
    except Exception as e:
        error = str(e)
        response = "I cannot solve this task."

    if not os.path.exists(f"{save_path}{save_name}/"):
        os.makedirs(f"{save_path}{save_name}/")
    with open(f"{save_path}{save_name}/{name}.json", "w") as f:
        json.dump({
            "name": name,
            "model": save_name,
            "input": prompt_tokens,
            "output": completion_tokens,
            "cost": cost,
            "time": time.time() - start,
            "error": error,
            'response': response
        }, f)

    return cost


# 并行处理所有任务
async def main():
    # 解析命令行参数
    args = parse_args()
    save_name = args.save_name
    data_file = args.data_file
    save_path = args.save_path

    # 加载数据
    data = load_data(data_file)

    # Constants
    instruction = "You are a data scientist. I have a data modeling task. You must give me the predicted results as a CSV file as detailed in the following content. You should try your best to predict the answer. I provide you with three files. One is training data, one is test data. There is also a sample file for submission"
    data_path = "./data/data_resplit/{name}/"  ## replace this to your data file

    keep_names = ["playground-series-s4e2", "us-patent-phrase-to-phrase-matching", "bike-sharing-demand",
                  "playground-series-s3e16", "covid19-global-forecasting-week-3",
                  "feedback-prize-english-language-learning", "covid19-global-forecasting-week-2",
                  "tabular-playground-series-jan-2022", "playground-series-s3e14", "nlp-getting-started"]
    data = filter_data(data, keep_names)

    # 使用tqdm显示进度条，并行执行所有任务
    tasks = []
    for id in range(0, len(data)):
        task = process_task(id, data, data_path, instruction, save_name, save_path)
        tasks.append(task)

    # 等待所有任务完成
    total_costs = await asyncio.gather(*tasks)
    total_cost = sum(total_costs)

    print(f"Total cost: {total_cost}")


# 启动并行处理
if __name__ == "__main__":
    asyncio.run(main())
