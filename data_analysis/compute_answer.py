import json
import asyncio
from tqdm import tqdm
import os
import argparse
from openai import AsyncOpenAI

from metagpt.llm import LLM

llm = LLM()

os.environ["OPENAI_API_KEY"] = llm.config.api_key
os.environ["OPENAI_BASE_URL"] = llm.config.base_url

llm = LLM()


async def evaluate_prediction(question, answer, prediction):
    prompt = (f"Please judge whether the generated answer is right or wrong. We require that the correct answer "
              f"to the prediction gives a clear answer, not just a calculation process or a disassembly of ideas. "
              f"The question is {question}. The true answer is \n {answer}. \n The predicted answer is \n {prediction}.\n "
              f"If the predicted answer is right, please output True. Otherwise output Flase. "
              f"Don't output any other text content. You only can output True or False.")
    try:
        # import pdb; pdb.set_trace()
        response = await llm.aask(prompt)
        return response
    except Exception as e:
        print(f"Error evaluating prediction: {e}")
        return "False"


def read_txt(path):
    with open(path, "r") as f:
        return f.read()


async def process_sample(sample, save_name, save_f, save_process, save_path):
    results = []

    if len(sample["questions"]) > 0:
        predicts = []
        with open(os.path.join(save_path, save_name, f"{sample['id']}.json"), "r") as f:
            for line in f:
                if not line.strip():  # 跳过空行
                    continue
                predicts.append(eval(line.strip()))

        for id, question_name in enumerate(sample["questions"]):
            question = read_txt(os.path.join("./data", sample["id"], f"{question_name}.txt"))
            pre = predicts[id]
            try:
                ans = await evaluate_prediction(question, str(sample["answers"][id]),
                                                pre.get("response", []))
            except Exception as e:
                print(f"Error processing question {id}: {e}")
                ans = "False"

            process = [sample["id"], ans, str(sample["answers"][id]), pre.get("response", [])[:]]
            json.dump(process, save_process)
            save_process.write("\n")
            save_process.flush()
            results.append(ans)

        json.dump(results, save_f)
        save_f.write("\n")
        save_f.flush()
    return results


async def main():
    parser = argparse.ArgumentParser(description="Evaluate predictions with AsyncOpenAI.")
    parser.add_argument("--save_name", "-s", type=str, required=False, help="Specify the save_name to use.", default="autogen-4o")
    parser.add_argument("--eval_model", type=str, default="gpt-3.5-turbo-0125", help="Specify the model to evaluate.")
    parser.add_argument("--keep_ids", type=str, required=False, help="Comma-separated list of IDs to keep in samples.", default="00000011,00000012,00000014")
    args = parser.parse_args()

    save_name = args.save_name
    eval_model = args.eval_model

    save_path = "./save_process"
    os.makedirs(os.path.join(save_path, save_name), exist_ok=True)

    samples = []
    with open("./data.json", "r") as f:
        for line in f:
            if not line.strip():
                continue
            samples.append(eval(line.strip()))

    # keep_ids = ["00000029", "00000004", "00000034", "00000036", "00000001"]
    # samples = [sample for sample in samples if sample["id"] in keep_ids]
    # filter_ids = ["00000043"]
    # samples = [sample for sample in samples if sample["id"] not in filter_ids]
    # 

    keep_ids = args.keep_ids.split(',')
    keep_ids = [id.strip() for id in keep_ids]

    filter_samples = []
    for sample in samples:
        if sample["id"] in keep_ids:
        # if sample["id"] not in filter_ids:
            filter_samples.append(sample)
    samples = filter_samples

    results = []
    save_f = open(os.path.join(save_path, save_name, "results.json"), "w")
    save_process = open(os.path.join(save_path, save_name, "results_process.json"), "w")

    # 并行处理所有样本
    tasks = [
        process_sample(sample, save_name, save_f, save_process, save_path)
        for sample in samples
    ]
    all_results = await asyncio.gather(*tasks)

    for result in all_results:
        results.extend(result)

    save_f.close()
    save_process.close()

    results_c = [True if "true" in result.lower() else False for result in results]

    idx = 0
    score4cha = []
    for sample in tqdm(samples):
        if len(sample["questions"]) > 0:
            score_ = sum(results_c[idx:idx + len(sample["questions"])]) / len(sample["questions"])
            idx += len(sample["questions"])
            score4cha.append(score_)
    print(f"Accuracy for each challenge is {score4cha}")

    acc = sum(results_c) / len(results_c)
    print(f"Accuracy for all the {len(results_c)} questions is {acc}")


if __name__ == "__main__":
    asyncio.run(main())
