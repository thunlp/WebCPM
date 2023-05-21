#! /bin/bash

wget -O model_part1.pt https://cloud.tsinghua.edu.cn/f/99e341dd2db14bc6a30e/?dl=1
wget -O model_part2.pt https://cloud.tsinghua.edu.cn/f/7e68d67a02ad4dfc9fbb/?dl=1
wget -O model_part3.pt https://cloud.tsinghua.edu.cn/f/e8d5083f352341a19db2/?dl=1
wget -O model_part4.pt https://cloud.tsinghua.edu.cn/f/7c5a50a8c5374ae0bc76/?dl=1
wget -O model_part5.pt https://cloud.tsinghua.edu.cn/f/7bb89263ff4a40cdb2be/?dl=1

python combine_pipeline_finetuned.py

rm model_part1.pt
rm model_part2.pt
rm model_part3.pt
rm model_part4.pt
rm model_part5.pt