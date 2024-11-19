import os
import argparse
from tqdm import tqdm


def read_txt(path):
    with open(path, "r") as f:
        return f.read()


def main(model):
    # 加载样本数据
    samples = []
    with open("./data.json", "r") as f:
        for line in f:
            samples.append(eval(line.strip()))

    save_path = "./save_process"

    # 加载结果数据
    results = []
    with open(os.path.join(save_path, model, "results.json"), "r") as f:
        for line in f:
            results += eval(line.strip())

    costs = []
    time_cost = []

    eval_instance_num = 3
    id = 0
    for sample in tqdm(samples[:eval_instance_num]):
        if len(sample["questions"]) > 0:
            predicts = []
            with open(os.path.join(save_path, model, sample['id'] + ".json"), "r") as f:
                for line in f:
                    pre = eval(line.strip())
                    predicts.append(pre)
                    costs.append(pre['cost'])
                    time_cost.append(pre['time'])
        id += 1

    results_c = []
    for result in results:
        if "true" in result.lower():
            results_c.append(True)
        else:
            results_c.append(False)

    idx = 0
    score4cha = []

    for i, sample in enumerate(samples):
        if len(sample["questions"]) > 0:
            score_ = sum(results_c[idx:idx + len(sample["questions"])]) / len(sample["questions"])
            idx += len(sample["questions"])
            score4cha.append(score_)

    acc = sum(results_c) / len(results_c)
    print(f"Accuracy for all the {len(results_c)} questions is {acc}")
    print(f"Cost for all the {len(results_c)} questions is {sum(costs)}")
    print(f"Consume time for all the {len(results_c)} questions is {sum(time_cost)}")
    print()
    print(f"Accuracy for each challenge is {score4cha}")
    print(f"Average accuracy for {len(score4cha)} challenge is {sum(score4cha) / len(score4cha)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate model performance.")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Specify the model to evaluate, e.g., 'gpt-4o' or 'gpt-4o-di'."
    )
    args = parser.parse_args()
    main(args.model)
