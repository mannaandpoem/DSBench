#!/bin/bash

# 检查是否提供了save_name参数
if [ -z "$1" ]; then
    echo "Error: Please specify a save_name."
    exit 1
fi

# 获取用户指定的save_name
save_name=$1

# 切换到当前脚本所在目录
cd "$(dirname "$0")"

# 执行指定的 Python 脚本并保存结果
#echo "Running eva_di_gpt_parallel.py..."
#python eva_di_gpt_parallel.py --save_name "$save_name"

echo "Running eva_autogen_gpt.py ..."
python eva_autogen_gpt.py --save_name "$save_name"

echo "Running score4each_com.py..."
python score4each_com.py --save_name "$save_name"

echo "Running show_result.py..."
python show_result.py --save_name "$save_name"

echo "All tasks completed successfully!"
