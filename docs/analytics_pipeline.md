# Model Analytics Pipeline

## Overview

The Model Analytics Pipeline provides robust functionality for processing, analyzing, and monitoring model metrics and predictions. It enables data scientists and ML engineers to gain insights into model performance and behavior through batch processing and scheduled analytics jobs.

## Architecture

The analytics pipeline consists of the following components:

1. **Batch Processor** - Processes metrics and prediction data in batches
2. **Batch Scheduler** - Schedules and manages analytics jobs
3. **Analytics API** - Provides REST endpoints for accessing analytics data
4. **Data Analyzer** - Analyzes metrics and predictions for insights

![Analytics Pipeline Architecture](../assets/images/analytics_pipeline.png)

## Key Features

- **Batch Processing** - Efficient processing of large volumes of model metrics and predictions
- **Scheduled Analytics** - Automated scheduling of analytics jobs at configurable intervals
- **Comprehensive Metrics** - Standard ML metrics calculation and tracking
- **Error Analysis** - Detailed analysis of prediction errors and model performance
- **Time Series Analytics** - Temporal analysis of model metrics
- **API Integration** - RESTful API for accessing analytics data

## Usage

### Running a Batch Job

To run a batch analytics job manually:

```python
from src.stages.stage4_analytics.batch_processor import BatchProcessor

processor = BatchProcessor()
results = processor.run_batch_job(
    metrics_path="path/to/metrics.parquet",
    predictions_path="path/to/predictions.parquet",
    model_name="my_model"
)
```

### Scheduling Jobs

To set up a scheduled job:

```python
from src.stages.stage4_analytics.batch_scheduler import BatchScheduler

scheduler = BatchScheduler()
scheduler.add_job(
    job_id="daily_model_analytics",
    model_name="my_model",
    metrics_path="path/to/metrics.parquet",
    predictions_path="path/to/predictions.parquet",
    frequency="daily"
)

# Start the scheduler
scheduler.start_scheduler(interval_seconds=3600)
```

### Using the API

The analytics data is accessible via RESTful API endpoints:

#### List Available Jobs

```
GET /analytics/jobs
```

#### Create a New Job

```
POST /analytics/jobs
{
  "job_id": "my_job",
  "model_name": "my_model",
  "metrics_path": "path/to/metrics.parquet",
  "predictions_path": "path/to/predictions.parquet",
  "frequency": "daily"
}
```

#### Run a Job Manually

```
POST /analytics/jobs/{job_id}/run
```

#### Get Model Metrics

```
GET /analytics/model/{model_name}/metrics
```

#### Get Prediction Analytics

```
GET /analytics/model/{model_name}/predictions
```

## Output Data

Analytics outputs are stored as JSON files in the configured output directory. The file naming convention is:

- Metrics: `{model_name}_metrics_{batch_id}.json`
- Predictions: `{model_name}_predictions_{batch_id}.json`
- Job Summary: `batch_summary_{batch_id}.json`

## Configuration

The analytics pipeline can be configured through the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `output_path` | Path for storing analytics results | `data/analytics` |
| `schedule_file` | Path to the job schedule file | `data/analytics/schedule.json` |
| `window_size` | Window size for time series analysis | `7` |
| `outlier_threshold` | Threshold for outlier detection | `1.5` |

## Integration with Monitoring

The analytics pipeline integrates with the monitoring system to provide:

1. Drift detection for model inputs and outputs
2. Performance degradation alerts
3. Data quality monitoring
4. Real-time metrics visualization

## Future Enhancements

- Enhanced visualization of analytics results
- Anomaly detection algorithms for metrics
- Automated model retraining triggers
- Advanced performance profiling
- A/B testing analytics

## Testing

The analytics pipeline includes unit tests for all major components, including:

- Batch processor tests
- Scheduler validation tests
- API endpoint tests
- Analytics calculation validation

To run tests:

```bash
python -m pytest src/stages/stage4_analytics/tests/
``` 