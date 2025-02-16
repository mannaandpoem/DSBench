#!/bin/bash

# # Run jobs in parallel
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-1 --keep_ids=00000001,00000002,00000003,00000004,00000005 > logs/di-4o-da-all-1-1.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-2 --keep_ids=00000006,00000007,00000008,00000009,00000010 > logs/di-4o-da-all-1-2.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-3 --keep_ids=00000011,00000012,00000013,00000014,00000016 > logs/di-4o-da-all-1-3.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-4 --keep_ids=00000017,00000018,00000019,00000020,00000022 > logs/di-4o-da-all-1-4.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-5 --keep_ids=00000025,00000026,00000027,00000028,00000030 > logs/di-4o-da-all-1-5.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-6 --keep_ids=00000034,00000035,00000036,00000037,00000038 > logs/di-4o-da-all-1-6.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-7 --keep_ids=00000039,00000041,00000042 > logs/di-4o-da-all-1-7.log 2>&1 &
# python eva_di_gpt_serial.py --save_name=di-4o-da-all-1-8 --keep_ids=00000029,00000031,00000032,00000033,00000043 > logs/di-4o-da-all-1-8.log 2>&1 &

# # Wait for all background jobs to finish
# wait


# 使用 pm2 启动进程，并指定日志文件
pm2 start python --name di-4o-da-all-1-1 --output logs/di-4o-da-all-1-1.log --error logs/di-4o-da-all-1-1.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-1 --keep_ids=00000001,00000002,00000003,00000004,00000005

pm2 start python --name di-4o-da-all-1-2 --output logs/di-4o-da-all-1-2.log --error logs/di-4o-da-all-1-2.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-2 --keep_ids=00000006,00000007,00000008,00000009,00000010

pm2 start python --name di-4o-da-all-1-3 --output logs/di-4o-da-all-1-3.log --error logs/di-4o-da-all-1-3.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-3 --keep_ids=00000011,00000012,00000013,00000014,00000016

pm2 start python --name di-4o-da-all-1-4 --output logs/di-4o-da-all-1-4.log --error logs/di-4o-da-all-1-4.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-4 --keep_ids=00000017,00000018,00000019,00000020,00000022

pm2 start python --name di-4o-da-all-1-5 --output logs/di-4o-da-all-1-5.log --error logs/di-4o-da-all-1-5.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-5 --keep_ids=00000025,00000026,00000027,00000028,00000030

pm2 start python --name di-4o-da-all-1-6 --output logs/di-4o-da-all-1-6.log --error logs/di-4o-da-all-1-6.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-6 --keep_ids=00000034,00000035,00000036,00000037,00000038

pm2 start python --name di-4o-da-all-1-7 --output logs/di-4o-da-all-1-7.log --error logs/di-4o-da-all-1-7.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-7 --keep_ids=00000039,00000041,00000042

pm2 start python --name di-4o-da-all-1-8 --output logs/di-4o-da-all-1-8.log --error logs/di-4o-da-all-1-8.log -- eva_di_gpt_serial.py --save_name=di-4o-da-all-1-8 --keep_ids=00000029,00000031,00000032,00000033,00000043

"""
00000001,00000002,00000003,00000004,00000005,00000017,00000018,00000019,00000020,00000022,00000034,00000035,00000036,00000037,00000038,00000039,00000041,00000042,00000006,00000007,00000008,00000011,00000012,00000025,00000026,00000027,00000028,00000030


"""