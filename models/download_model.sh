#! /bin/bash

wget -O model_part1.pt https://cloud.tsinghua.edu.cn/f/4fa96d34d5704f21ad20/?dl=1
wget -O model_part2.pt https://cloud.tsinghua.edu.cn/f/956d2f1b824b4f3897e8/?dl=1
wget -O model_part3.pt https://cloud.tsinghua.edu.cn/f/5c32bbd5fb734df2847a/?dl=1
wget -O model_part4.pt https://cloud.tsinghua.edu.cn/f/148577a358da4ff5b1ea/?dl=1
wget -O model_part5.pt https://cloud.tsinghua.edu.cn/f/d4ca2747bc87424b93c4/?dl=1

python combine.py

rm model_part1.pt
rm model_part2.pt
rm model_part3.pt
rm model_part4.pt
rm model_part5.pt