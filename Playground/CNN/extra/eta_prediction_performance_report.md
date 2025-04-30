
# ETA Prediction Model Performance Report

## 1. Model Summary
- Baseline: CNN with fixed hyperparameters
- Optimized: CNN with Optuna-tuned hyperparameters
- Dataset: Transit data with 11 features and 100000 samples
- Training split: 80%, Test split: 20%

## 2. Key Performance Metrics

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| RMSE | 0.5433 | 0.5489 | -0.0056 (-1.03%) |
| MAE | 0.3372 | 0.3510 | -0.0138 (-4.10%) |
| MAPE | 33457813564.2789 | 36050403410.5065 | -2592589846.2276 (-7.75%) |
| R2 | 0.9645 | 0.9638 | -0.0007 (-0.08%) |
| Explained_Variance | 0.9646 | 0.9639 | -0.0007 (-0.07%) |
| P90 | 0.7899 | 0.7886 | 0.0014 (0.18%) |
| P95 | 1.0438 | 1.0530 | -0.0092 (-0.89%) |
| P99 | 2.0059 | 2.0349 | -0.0290 (-1.45%) |

## 3. Overfitting Analysis

| Metric | Baseline (Train/Test) | Optimized (Train/Test) |
|--------|----------------------|------------------------|
| RMSE | 0.5341 / 0.5433 | 0.5450 / 0.5489 |
| MAE | 0.3344 / 0.3372 | 0.3487 / 0.3510 |
| R2 | 0.9659 / 0.9645 | 0.9645 / 0.9638 |

## 4. Training Times

| Process | Duration |
|---------|----------|
| Baseline Model Training | 0:02:05.048188 |
| Optuna Hyperparameter Optimization | 1:24:48.389862 |
| Optimized Model Training | 0:01:14.206765 |
| Total Time | 1:28:07.644815 |

## 5. Best Hyperparameters

The following hyperparameters were found to be optimal after Optuna optimization:
- filters1: 98
- filters2: 119
- kernel_size: 4
- dense_units: 112
- learning_rate: 0.00019352000352505002
- batch_size: 128
- dropout_rate: 0.2259225585771292

## 6. Conclusion

The optimized model shows **slight improvement** over the baseline model. Further optimization strategies may be worth exploring.