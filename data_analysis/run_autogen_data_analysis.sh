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

echo "Running eva_autogen_gpt.py..."
python eva_autogen_gpt.py --save_name "$save_name"
