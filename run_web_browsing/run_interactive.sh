#! /bin/bash
export PYTHONPATH=/data/private/qinyujia/webcpm
export BING_SEARCH_KEY="**Your-Bing-Search-API-Key**"

CUDA_VISIBLE_DEVICES=0 python run_interactive.py --data_path predictions/test_interactive.json --ckpt_path /data/private/qinyujia/pretrained_models/cpm_bee_510_multi4-epoch-2.pt