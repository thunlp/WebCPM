export PYTHONPATH=/data/private/qinyujia/webcpm/training

# performing inference on test data
CUDA_VISIBLE_DEVICES=7 python inference.py --test_file ../training/dataset_interactive/test.txt --output_file output/test_output.json --ckpt_path /data/private/qinyujia/pretrained_models/cpm_bee_action_new-best.pt --beam_size 1

# evaluating the performance
python evaluate_action.py