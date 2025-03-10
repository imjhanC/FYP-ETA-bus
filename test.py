import torch
print("PyTorch GPU Available:", torch.cuda.is_available())
print("CUDA Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU Found")

import xgboost as xgb
print("XGBoost Version:", xgb.__version__)
