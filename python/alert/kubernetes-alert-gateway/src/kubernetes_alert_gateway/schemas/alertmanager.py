from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AlertItem(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )
    status: Literal["firing", "resolved"]
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    fingerprint: str | None = None
    starts_at: str | None = Field(
        default=None,
        alias="startsAt"
    )
    ends_at: str | None = Field(
        default=None,
        alias="endsAt"
    )
    generator_url: str | None = Field(
        default=None,
        alias="generatorURL"
    )


class AlertmanagerPayload(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    version: str 
    group_key: str = Field(alias="groupKey")
    status: Literal["firing", "resolved"]
    receiver: str 
    alerts: list[AlertItem]
    truncated_alerts: int | None = Field(
        default=None,
        alias="truncatedAlerts",
    )
    group_labels: dict[str, str] = Field(
        default_factory=dict,
        alias="groupLabels",
    )
    common_labels: dict[str, str] = Field(
        default_factory=dict,
        alias="commonLabels",
    )
    common_annotations: dict[str, str] = Field(
        default_factory=dict,
        alias="commonAnnotations",
    )
    external_url: str | None = Field(
        default=None,
        alias="externalURL",
    )


class AlertmanagerResponse(BaseModel):
    status: Literal["processed"] = "processed"
    amount_alerts: int = Field(ge=0)
    sent_alerts: int = Field(ge=0)
    duplicate_alerts: int = Field(ge=0)
