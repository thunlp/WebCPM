import torch

model1 = torch.load("model_part1.pt")
model2 = torch.load("model_part2.pt")
model3 = torch.load("model_part3.pt")
model4 = torch.load("model_part4.pt")
model5 = torch.load("model_part5.pt")
model_combine = {**model1, **model2, **model3, **model4, **model5}
torch.save(model_combine, "cpm_10b_webcpm_pipeline_finetuned.pt")
