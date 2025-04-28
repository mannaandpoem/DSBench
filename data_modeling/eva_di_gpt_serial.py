#!/usr/bin/env python
# coding: utf-8
import argparse
import asyncio
import json
import os
import time
import traceback

from metagpt.roles.di.data_interpreter import DataInterpreter


# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="Run model tasks sequentially")
    parser.add_argument('--save_name', "-s", type=str, default="gpt-4o",
                        help="Model to use (e.g., gpt-4o)")
    parser.add_argument('--data_file', type=str, default="./data.json", help="Data file to load")
    parser.add_argument('--save_path', type=str, default="./output_model/", help="Path to save the output")
    parser.add_argument("--keep_ids", type=str, required=True, help="Comma-separated list of IDs to keep in samples.")
    return parser.parse_args()


def load_data(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(eval(line))
    return data


def keep_data(data, keep_names):
    return [d for d in data if d["name"] in keep_names]


def filter_data(data, keep_ids):
    return [d for d in data if d["name"] in keep_ids]


async def get_response(text):
    di = DataInterpreter()
    chat_res = await di.run(text)
    return chat_res


async def process_task(id, data, data_path, instruction, save_name, save_path):
    try:
        name = data[id]['name']
        print(f"Current directory: {os.getcwd()}")
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
            rst = await get_response(input_t)
            response = rst.content
        except Exception as e:
            error = str(e)
            response = f"I cannot solve this task. {e}"

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
    except Exception as e:
        print(f"Error processing task {id}: {str(e)}")
        print(traceback.format_exc())
        return 0  # Return 0 cost for failed tasks


async def process_all_tasks(data, data_path, instruction, save_name, save_path):
    total_cost = 0
    for id in range(0, len(data)):
        print(f"running id: {id}")
        try:
            cost = await process_task(id, data, data_path, instruction, save_name, save_path)
            total_cost += cost
        except Exception as e:
            print(f"Failed to process task {id}: {str(e)}")
            print(traceback.format_exc())
            continue  # Skip to the next task if this one fails
    return total_cost


def main():
    # 解析命令行参数
    args = parse_args()
    save_name = args.save_name
    data_file = args.data_file
    save_path = args.save_path
    keep_ids = args.keep_ids.split(',')

    # 加载数据
    data = load_data(data_file)

    # Constants
    instruction = "You are a data scientist. I have a data modeling task. You must give me the predicted results as a CSV file as detailed in the following content. You should try your best to predict the answer. I provide you with three files. One is training data, one is test data. There is also a sample file for submission"
    data_path = "./data/data_resplit/{name}/"  ## replace this to your data file

    keep_ids = [id.strip() for id in keep_ids]
    data = filter_data(data, keep_ids)
    print(f"All ids len: {len(data)}")

    # Run all tasks in the event loop
    total_cost = asyncio.run(process_all_tasks(data, data_path, instruction, save_name, save_path))
    print(f"Total cost: {total_cost}")


if __name__ == "__main__":
    main()
