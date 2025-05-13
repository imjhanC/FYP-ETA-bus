
# ETA Prediction Model Performance Report

## 1. Model Summary
- Baseline: CNN with fixed hyperparameters
- Optimized: CNN with Optuna-tuned hyperparameters
- Dataset: Transit data with 11 features and 100000 samples
- Training split: 80%, Test split: 20%

## 2. Key Performance Metrics

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| RMSE | 0.5374 | 0.5383 | -0.0010 (-0.18%) |
| MAE | 0.3328 | 0.3329 | -0.0001 (-0.03%) |
| MAPE | 16.3540 | 16.1613 | 0.1928 (1.18%) |
| R2 | 0.9653 | 0.9652 | -0.0001 (-0.01%) |
| Explained_Variance | 0.9653 | 0.9653 | -0.0001 (-0.01%) |
| P90 | 0.7917 | 0.7992 | -0.0076 (-0.95%) |
| P95 | 1.0332 | 1.0337 | -0.0005 (-0.05%) |
| P99 | 1.9728 | 1.9912 | -0.0185 (-0.94%) |

## 3. Overfitting Analysis

| Metric | Baseline (Train/Test) | Optimized (Train/Test) |
|--------|----------------------|------------------------|
| RMSE | 0.5320 / 0.5374 | 0.5315 / 0.5383 |
| MAE | 0.3299 / 0.3328 | 0.3292 / 0.3329 |
| R2 | 0.9661 / 0.9653 | 0.9662 / 0.9652 |

## 4. Training Times

| Process | Duration |
|---------|----------|
| Baseline Model Training | 0:01:52.144247 |
| Optuna Hyperparameter Optimization | 1:26:44.246171 |
| Optimized Model Training | 0:02:27.070297 |
| Total Time | 1:31:03.460715 |

## 5. Best Hyperparameters

The following hyperparameters were found to be optimal after Optuna optimization:
- filters1: 82
- filters2: 124
- kernel_size: 5
- dense_units: 128
- learning_rate: 0.0002176513380703961
- batch_size: 64
- dropout_rate: 0.13588547271932222

## 6. Conclusion

The optimized model shows **slight improvement** over the baseline model. Further optimization strategies may be worth exploring.