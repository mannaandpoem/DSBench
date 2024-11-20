#!/usr/bin/env python
# coding: utf-8
import argparse
import os
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
import json
import time
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Process samples and save outputs.")
parser.add_argument("--save_name", type=str, default="gpt-4o", help="Directory to save processed outputs.")
args = parser.parse_args()
model = args.save_name

config_list = autogen.config_list_from_json(
    "../../../OAI_CONFIG_LIST"
)

data = []

with open("./data.json", "r") as f:
    for line in f:
        data.append(eval(line))

len(data)


def filter_data(data, keep_names):
    return [d for d in data if d["name"] in keep_names]


keep_names = ["playground-series-s4e2", "us-patent-phrase-to-phrase-matching", "bike-sharing-demand",
              "playground-series-s3e16", "covid19-global-forecasting-week-3",
              "feedback-prize-english-language-learning", "covid19-global-forecasting-week-2",
              "tabular-playground-series-jan-2022", "playground-series-s3e14", "nlp-getting-started"]
data = filter_data(data, keep_names)

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
start = time.time()
# the assistant receives a message from the user_proxy, which contains the task description
chat_res = user_proxy.initiate_chat(
    assistant,
    message="""What date is today? Compare the year-to-date gain for META and TESLA.""",
    summary_method="reflection_with_llm",
)
consume = time.time() - start


def get_response(text, config_list):
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
    # the assistant receives a message from the user_proxy, which contains the task description
    chat_res = user_proxy.initiate_chat(
        assistant,
        message=text,
        summary_method="reflection_with_llm",
    )
    return chat_res


total_cost = 0

instruction = "You are a data scientist. I have a data modeling task. You must give me the predicted results as a CSV file as detailed in the following content. You should try your best to predict the answer. I provide you with three files. One is training data, one is test data. There is also a sample file for submission"

save_path = "./output_model/"

data_path = "./data/data_resplit/{name}/"  ## replace this to your data file

for id in tqdm(range(0, len(data))):
    # for id in tqdm([0]):
    # print(sample)
    name = data[id]['name']
    with open(f"./data/task/{name}.txt", "r") as f:
        description = f.read()

    data_path = data_path.format(name=name)
    text = (
        f"\n \n All three data files can be found in the folder: {data_path}. After the data modeling, please give me the prediction resutls for the test file. You must"
        f" save the answer as a csv file. I won't run your code and you must run the code for the predicted results and give the submission file. The file should be saved in the path ./output_model/{model}/{name}.csv")

    all_context = instruction + "\n" + description + "\n" + text
    input_t = all_context

    # input_t = truncate_text(all_context, 2000)
    start = time.time()
    cost = 0
    error = ""
    prompt_tokens = completion_tokens = 0
    try:
        response = get_response(input_t, config_list)
        prompt_tokens = response.cost['usage_including_cached_inference'][model]['prompt_tokens']
        completion_tokens = response.cost['usage_including_cached_inference'][model]['completion_tokens']
        cost = response.cost['usage_including_cached_inference'][model]['cost']
        summary = response.summary
        history = response.chat_history
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

    if not os.path.exists(f"{save_path}{model}/"):
        os.makedirs(f"{save_path}{model}/")
    with open(f"{save_path}{model}/{name}.json", "w") as f:
        json.dump({"name": name, "model": model, "input": prompt_tokens,
                   "output": completion_tokens, "cost": cost, "time": time.time() - start, "error": error,
                   'summary': summary, "history": history}, f)
