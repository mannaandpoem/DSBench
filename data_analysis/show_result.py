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
    
    keep_ids = args.keep_ids.split(',')
    keep_ids = [id.strip() for id in keep_ids]

    filter_samples = []
    for sample in samples:
        if sample["id"] in keep_ids:
        # if sample["id"] not in filter_ids:
            filter_samples.append(sample)
    samples = filter_samples
    
    
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
                    costs.append(pre.get("cost", 0))
                    time_cost.append(pre.get("time", 0))
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
        "-s",
        type=str,
        default="gpt-4o-di-old-2",
        help="Specify the save_name to evaluate, e.g., 'gpt-4o' or 'gpt-4o-di'."
    )
    parser.add_argument("--keep_ids", type=str, required=True, help="Comma-separated list of IDs to keep in samples.")
    args = parser.parse_args()
    main(args.save_name)
