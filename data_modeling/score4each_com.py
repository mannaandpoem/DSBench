import os
import argparse
import json


def load_data(data_path):
    """Load data from the specified JSON file."""
    data = []
    with open(data_path, "r") as f:
        for line in f:
            data.append(eval(line))
    return data


def create_directory(path):
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def compute_performance(data, gt_path, pred_path, save_path, python_path):
    """Compute performance for each item in the dataset."""
    for line in data:
        answer_file = os.path.join(gt_path, line['name'], 'test_answer.csv')
        pred_file = os.path.join(pred_path, f"{line['name']}.csv")

        if os.path.exists(pred_file):
            save_dir = os.path.join(save_path, line['name'])
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            print(f"Compute performance for {line['name']}")
            try:
                os.system(
                        f"python {python_path}{line['name']}_eval.py "
                        f"--answer_file {answer_file} "
                        f"--predict_file {pred_file} "
                        f"--path {save_path} "
                        f"--name {line['name']}"
                        )
            except:
                print("error: {line['name']}!")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Compute performance.")
    parser.add_argument('--save_name', type=str, required=True, help="Specify the save_name.")
    parser.add_argument('--data_path', type=str, default="./data.json", help="Path to the data JSON file.")
    parser.add_argument('--gt_path', type=str, default="./data/answers/", help="Path to ground truth answers.")
    parser.add_argument('--python_path', type=str, default="./evaluation/", help="Path to evaluation scripts.")
    parser.add_argument('--output_path', type=str, default="./output_model/", help="Path to prediction files.")
    parser.add_argument('--save_path', type=str, default="./save_performance/",
                        help="Path to save performance results.")

    args = parser.parse_args()

    # Load data
    data = load_data(args.data_path)
    print(data)

    # Define paths
    pred_path = os.path.join(args.output_path, args.save_name)
    save_path = os.path.join(args.save_path, args.save_name)

    # Compute performance
    compute_performance(data, args.gt_path, pred_path, save_path, args.python_path)


if __name__ == "__main__":
    main()
