#!/usr/bin/env python
# coding: utf-8
import asyncio
import os

import json
import base64
import re
import time
import pandas as pd
from tqdm.notebook import tqdm

from metagpt.roles.di.data_interpreter import DataInterpreter

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




data = []

with open("./data.json", "r") as f:
    for line in f:
        data.append(eval(line))

len(data)

model = "gpt-4o"



async def get_response(text):
    di = DataInterpreter()
    chat_res = await di.run(text)
    return chat_res

total_cost = 0

instruction = "You are a data scientist. I have a data modeling task. You must give me the predicted results as a CSV file as detailed in the following content. You should try your best to predict the answer. I provide you with three files. One is training data, one is test data. There is also a sample file for submission"

save_path = "./output_model/"

data_path = "./data/data_resplit/{name}/" ## replace this to your data file

keep_names = ["playground-series-s4e2", "us-patent-phrase-to-phrase-matching", "bike-sharing-demand", "playground-series-s3e16", "covid19-global-forecasting-week-3", "feedback-prize-english-language-learning", "covid19-global-forecasting-week-2", "tabular-playground-series-jan-2022", "playground-series-s3e14", "nlp-getting-started"]
keep_data = []
for d in data:
    if d["name"] in keep_names:
        keep_data.append(d)
data = keep_data

for id in tqdm(range(0, len(data))):
# for id in tqdm([0]):
    # print(sample)
    name = data[id]['name']
    with open(f"./data/task/{name}.txt", "r") as f:
        description = f.read()

    text = (f"\n \n All three data files can be found in the folder: {data_path}. After the data modeling, please give me the prediction resutls for the test file. You must"
            f" save the answer as a csv file. I won't run your code and you must run the code for the predicted results and give the submission file. The file should be saved in the path ./output_model/{model}-di/{name}.csv")

    all_context = instruction + "\n" + description + "\n" + text
    input_t = all_context

    # input_t = truncate_text(all_context, 2000)
    start = time.time()
    cost = 0
    error = ""
    prompt_tokens = completion_tokens = 0
    response = ""
    try:
        rst = asyncio.run(get_response(input_t))
        response = rst.content
    except Exception as e:
        print(e)
        # time.sleep(3)
        error = str(e)
        # cost = 0
        history = "I cannot solve this task."
        summary = "I cannot solve this task."
        print(history)
        print(e)
        time.sleep(3)
                # all_mess.append("I cannot solve this task.")
    total_cost += cost
    print("Total cost: ", total_cost)

    if not os.path.exists(f"{save_path}{model}-di/"):
        os.makedirs(f"{save_path}{model}-di/")
    with open(f"{save_path}{model}-di/{name}.json", "w") as f:
        json.dump({"name": name, "model": model, "input": prompt_tokens,
                            "output": completion_tokens, "cost": cost, "time": time.time()-start, "error": error, 'response': response}, f)
