import os
import argparse
from tqdm import tqdm


def read_txt(path):
    with open(path, "r") as f:
        return f.read()


def main(save_name):
    # 加载样本数据
    samples = []
    with open("./data.json", "r") as f:
        for line in f:
            samples.append(eval(line.strip()))

    keep_ids = ["00000029", "00000004", "00000034", "00000036", "00000001"]
    samples = [sample for sample in samples if sample["id"] in keep_ids]
    save_path = "./save_process"

    # 加载结果数据
    results = []
    with open(os.path.join(save_path, save_name, "results.json"), "r") as f:
        for line in f:
            results += eval(line.strip())

    costs = []
    time_cost = []

    id = 0
    for sample in tqdm(samples):
        if len(sample["questions"]) > 0:
            predicts = []
            with open(os.path.join(save_path, save_name, sample['id'] + ".json"), "r") as f:
                for line in f:
                    if not line.strip():
                        continue
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
    print(f"Accuracy for each challenge is {score4cha}")
    print(f"Average accuracy for {len(score4cha)} challenge is {sum(score4cha) / len(score4cha)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate save_name performance.")
    parser.add_argument(
        "--save_name",
        type=str,
        required=True,
        help="Specify the save_name to evaluate, e.g., 'gpt-4o' or 'gpt-4o-di'."
    )
    args = parser.parse_args()
    main(args.save_name)
