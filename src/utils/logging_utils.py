import os


def init_mlflow(cfg):
    """
    Config örneği:

    mlflow:
      tracking_uri: "http://mlflow:5000"   # opsiyonel
      experiment_name: "dev-experiments"
    """
    try:
        import mlflow
    except ImportError:
        return None

    mlflow_cfg = cfg.get("mlflow", {})
    tracking_uri = mlflow_cfg.get("tracking_uri", os.environ.get("MLFLOW_TRACKING_URI"))
    experiment_name = mlflow_cfg.get("experiment_name", "default-experiment")

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    mlflow.set_experiment(experiment_name)
    run = mlflow.start_run()
    return run