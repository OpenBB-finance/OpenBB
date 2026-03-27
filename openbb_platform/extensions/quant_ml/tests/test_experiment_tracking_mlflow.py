from __future__ import annotations

import re
from types import SimpleNamespace

from openbb_quant_ml.service import experiment_tracking as experiment_tracking


class FakeMlflowRun:
    def __init__(self, run_id: str, tags: dict[str, str]) -> None:
        self.info = SimpleNamespace(run_id=run_id)
        self.tags = dict(tags)


class FakeMlflowClient:
    def __init__(self) -> None:
        self.created_experiments: list[str] = []
        self.created_runs: list[tuple[str, dict[str, str]]] = []
        self.params: list[tuple[str, str, str]] = []
        self.metrics: list[tuple[str, str, float]] = []
        self.tags: list[tuple[str, str, str]] = []
        self.terminated: list[tuple[str, str]] = []
        self._runs: dict[str, FakeMlflowRun] = {}
        self._experiment = SimpleNamespace(experiment_id="exp-123")

    def get_experiment_by_name(self, name: str) -> SimpleNamespace | None:
        if name in self.created_experiments:
            return self._experiment
        return None

    def create_experiment(self, name: str) -> str:
        self.created_experiments.append(name)
        return self._experiment.experiment_id

    def search_runs(
        self, *, experiment_ids: list[str], filter_string: str, max_results: int = 1
    ) -> list[FakeMlflowRun]:
        assert experiment_ids == [self._experiment.experiment_id]
        assert max_results == 1
        match = re.search(r"tags\.openbb_run_id = '([^']+)'", filter_string)
        run_id = match.group(1) if match else ""
        run = self._runs.get(run_id)
        return [run] if run is not None else []

    def create_run(self, *, experiment_id: str, tags: dict[str, str]) -> FakeMlflowRun:
        run = FakeMlflowRun("mlflow-run-1", tags)
        self._runs[tags["openbb_run_id"]] = run
        self.created_runs.append((experiment_id, dict(tags)))
        return run

    def log_param(self, run_id: str, key: str, value: str) -> None:
        self.params.append((run_id, key, value))

    def log_metric(self, run_id: str, key: str, value: float) -> None:
        self.metrics.append((run_id, key, value))

    def set_tag(self, run_id: str, key: str, value: str) -> None:
        self.tags.append((run_id, key, value))

    def set_terminated(self, run_id: str, *, status: str) -> None:
        self.terminated.append((run_id, status))


def test_register_experiment_run_syncs_mlflow_when_enabled(monkeypatch) -> None:
    client = FakeMlflowClient()
    fake_mlflow = SimpleNamespace(
        tracking=SimpleNamespace(
            MlflowClient=lambda tracking_uri=None: client
        )
    )
    upserts: list[dict[str, object]] = []

    monkeypatch.setenv("OPENBB_QUANT_ML_MLFLOW_ENABLED", "true")
    monkeypatch.setenv("OPENBB_QUANT_ML_MLFLOW_EXPERIMENT_NAME", "quant-lab")
    monkeypatch.delenv("OPENBB_QUANT_ML_MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.setattr(experiment_tracking, "get_experiment_run", lambda run_id: None)
    monkeypatch.setattr(
        experiment_tracking,
        "upsert_experiment_run",
        lambda **kwargs: upserts.append(kwargs),
    )
    monkeypatch.setattr(
        experiment_tracking,
        "_load_mlflow_module",
        lambda: fake_mlflow,
    )

    experiment_tracking.register_experiment_run(
        run_id="run-mlflow-1",
        model_type="lgbm_ranker",
        dataset_version="dataset-v1",
        feature_set_version="features-v1",
        hyperparameters={"lr": 0.1, "window": {"train_start": "2024-01-01"}},
        feature_set={"feature_columns": ["alpha_1", "alpha_2"]},
        performance={},
        artifact_uri="/tmp/run-mlflow-1",
        status="running",
    )
    experiment_tracking.register_experiment_run(
        run_id="run-mlflow-1",
        model_type="lgbm_ranker",
        dataset_version="dataset-v1",
        feature_set_version="features-v1",
        hyperparameters={"lr": 0.1, "window": {"train_start": "2024-01-01"}},
        feature_set={"feature_columns": ["alpha_1", "alpha_2"]},
        performance={
            "score": 1.23,
            "models": [{"sharpe": 1.1}],
            "constraints_summary": {"gross_exposure_max": 1.0},
        },
        artifact_uri="/tmp/run-mlflow-1",
        status="completed",
    )

    assert len(upserts) == 2
    assert client.created_experiments == ["quant-lab"]
    assert len(client.created_runs) == 1
    assert ("mlflow-run-1", "hyperparameters.lr", "0.1") in client.params
    assert (
        "mlflow-run-1",
        "feature_set.feature_columns",
        '["alpha_1", "alpha_2"]',
    ) in client.params
    assert ("mlflow-run-1", "performance.score", 1.23) in client.metrics
    assert ("mlflow-run-1", "performance.models.0.sharpe", 1.1) in client.metrics
    assert (
        "mlflow-run-1",
        "performance.constraints_summary.gross_exposure_max",
        1.0,
    ) in client.metrics
    assert ("mlflow-run-1", "status", "completed") in client.tags
    assert ("mlflow-run-1", "FINISHED") in client.terminated


def test_register_experiment_run_keeps_sqlite_path_when_mlflow_missing(
    monkeypatch,
) -> None:
    upserts: list[dict[str, object]] = []

    monkeypatch.setenv("OPENBB_QUANT_ML_MLFLOW_ENABLED", "true")
    monkeypatch.setattr(experiment_tracking, "get_experiment_run", lambda run_id: None)
    monkeypatch.setattr(
        experiment_tracking,
        "upsert_experiment_run",
        lambda **kwargs: upserts.append(kwargs),
    )
    monkeypatch.setattr(
        experiment_tracking,
        "_load_mlflow_module",
        lambda: None,
    )

    experiment_tracking.register_experiment_run(
        run_id="run-no-mlflow",
        model_type="xgb_lstm",
        dataset_version="dataset-v0",
        feature_set_version="features-v0",
        hyperparameters={"epochs": 3},
        feature_set={"feature_columns": ["alpha"]},
        performance={"score": 0.5},
        artifact_uri="/tmp/run-no-mlflow",
        status="completed",
    )

    assert len(upserts) == 1
    assert upserts[0]["run_id"] == "run-no-mlflow"
