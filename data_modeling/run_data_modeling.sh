#!/bin/bash

# 切换到当前脚本所在目录
cd "$(dirname "$0")"

# 执行指定的 Python 脚本并保存结果
echo "Running eva_di_gpt.py..."
python eva_di_gpt.py --save_name "gpt-4o-di"

echo "Running score4each_com.py..."
python score4each_com.py --save_name "gpt-4o-di"

echo "Running show_result.py..."
python show_result.py --save_name "gpt-4o-di"

echo "All tasks completed successfully!"
