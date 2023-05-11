#! /bin/bash
export PYTHONPATH=/data/private/qinyujia/webcpm/inference
export BING_SEARCH_KEY="**Your-Bing-Search-API-Key**"


CUDA_VISIBLE_DEVICES=0 python run_pipeline.py --data_path predictions/test.json --ckpt_path /data/private/qinyujia/pretrained_models/cpm_live_checkpoint-602000.pt
# CUDA_VISIBLE_DEVICES=7 python run_pipeline.py --data_path predictions/test.json --ckpt_path /data/private/qinyujia/pretrained_models/cpm_bee_action_new_pipeline-best.pt
