from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NormalizedAlert(BaseModel):
    status: Literal["firing", "resolved"]
    source: Literal["alertmanager", "falco"]
    alert_name: str
    severity: str | None = None
    fingerprint: str

    cluster: str | None = None
    namespace: str | None = None
    workload: str | None = None
    workload_kind: str | None = None
    pod: str | None = None
    container: str | None = None
    node: str | None = None
    instance: str | None = None
    job: str | None = None
    pvc: str | None = None
    volume: str | None = None
    ingress: str | None = None
    service: str | None = None
    mountpoint: str | None = None
    device: str | None = None

    summary: str | None = None
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    generator_url: str | None = None
    actor: str | None = None

    project_name: str | None = None
    project_owners: list[str] = Field(default_factory=list)
    project_members: list[str] = Field(default_factory=list)

    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
