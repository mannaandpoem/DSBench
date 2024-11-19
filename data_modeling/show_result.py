import os
import json
from tqdm.notebook import tqdm
import time

import os
import argparse
from tqdm import tqdm


def load_data(data_path, keep_names):
    """Load and filter data based on keep_names."""
    data = []
    with open(data_path, "r") as f:
        for line in f:
            data.append(eval(line))
    return [d for d in data if d["name"] in keep_names]


def compute_metrics(data, gt_path, baseline_path, output_path, save_path):
    """Compute task completion rate, cost, time, and performance."""
    task_complete = 0
    scores = []
    all_costs = []
    all_times = []

    for line in data:
        with open(os.path.join(gt_path, line['name'], "result.txt"), "r") as f:
            gt = eval(f.read().strip())
        with open(os.path.join(output_path, f"{line['name']}.json"), "r") as f:
            record = eval(f.read().strip())
        all_costs.append(record['cost'])
        all_times.append(record['time'])
        with open(os.path.join(baseline_path, line['name'], "result.txt"), "r") as f:
            bl = eval(f.read().strip())

        result_file = os.path.join(save_path, line['name'], "result.txt")
        if not os.path.exists(result_file):
            scores.append(0)
            show_pre = "not exists"
        else:
            task_complete += 1
            with open(result_file, "r") as f:
                pre = f.read().strip()
            if pre == "nan":
                show_pre = "nan"
                scores.append(0)
            else:
                pre = eval(pre)
                sc = max(0, (pre - bl) / (gt - bl))
                scores.append(sc)
                show_pre = pre

    task_completion_rate = task_complete / len(data)
    total_cost = sum(all_costs)
    total_time = sum(all_times)
    average_performance = sum(scores) / len(scores) if scores else 0

    return task_completion_rate, total_cost, total_time, average_performance


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Evaluate model performance.")
    parser.add_argument('--save_name', type=str, required=True, help="Specify the save_name.")
    parser.add_argument('--data_path', type=str, default="./data.json", help="Path to the data JSON file.")
    parser.add_argument('--gt_path', type=str, default="./save_performance/GT", help="Path to ground truth results.")
    parser.add_argument('--baseline_path', type=str, default="./save_performance/baseline",
                        help="Path to baseline results.")
    parser.add_argument('--output_path', type=str, default="./output_model/", help="Path to prediction outputs.")
    parser.add_argument('--save_path', type=str, default="./save_performance/",
                        help="Path to saved performance results.")

    args = parser.parse_args()

    # Define paths
    save_name = args.save_name
    save_path = os.path.join(args.save_path, save_name)
    output_path = os.path.join(args.output_path, save_name)

    # Specify challenges to keep
    keep_names = [
        "playground-series-s4e2", "us-patent-phrase-to-phrase-matching", "bike-sharing-demand",
        "playground-series-s3e16", "covid19-global-forecasting-week-3",
        "feedback-prize-english-language-learning", "covid19-global-forecasting-week-2",
        "tabular-playground-series-jan-2022", "playground-series-s3e14", "nlp-getting-started"
    ]
    # Load data
    data = load_data(args.data_path, keep_names)

    # Compute metrics
    task_completion_rate, total_cost, total_time, average_performance = compute_metrics(
        data, args.gt_path, args.baseline_path, output_path, save_path
    )

    # Output results
    print(f"Task completion rate: {task_completion_rate}")
    print(f"Total cost: {total_cost}")
    print(f"Total time consumed: {total_time}")
    print(f"Average performance: {average_performance}")


if __name__ == "__main__":
    main()
