# src/packs/schemas.py
from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Union
from datetime import date, datetime
import json, pathlib

class SourceMeta(BaseModel):
    name: str
    url: HttpUrl
    license: Optional[str] = None
    retrieved_at: datetime

class Location(BaseModel):
    state: str
    district: str
    lat: float
    lon: float

class WeatherDay(BaseModel):
    date: date
    tmin_c: float
    tmax_c: float
    precip_mm: float
    wind_kmh: float
    rain_prob_pct: Optional[int] = Field(None, ge=0, le=100)

class WeatherPack(BaseModel):
    version: str = "1.0"
    generated_at: datetime
    location: Location
    days: List[WeatherDay]
    source: SourceMeta

class StageAdvice(BaseModel):
    stage: Literal["pre-sowing","sowing","vegetative","flowering","harvest"]
    irrigation: Optional[str] = None
    fertilizer: Optional[str] = None
    pest_watch: Optional[List[str]] = None
    notes: Optional[str] = None

class CropPack(BaseModel):
    version: str = "1.0"
    crop: str
    region: Optional[str] = None
    language: Literal["en","hi","bn","te","ta","mr","kn","ml","pa","gu","or","as"] = "en"
    stages: List[StageAdvice]
    source: SourceMeta
    generated_at: datetime

class Condition(BaseModel):
    variable: Literal["precip_mm","wind_kmh","tmin_c","tmax_c","rain_prob_pct"]
    op: Literal["<","<=",">",">=","between","not_between","==","!="]
    value: Union[float, List[float]]

class Action(BaseModel):
    advice: str
    severity: Literal["info","caution","danger"]
    escalate_if_low_conf: bool = False

class SafetyRule(BaseModel):
    id: str
    title: str
    applies_to_crops: Optional[List[str]] = None
    when_all: List[Condition]
    then: Action
    rationale: Optional[str] = None
    source: Optional[str] = None

class SafetyRulesPack(BaseModel):
    version: str = "1.0"
    rules: List[SafetyRule]
    generated_at: datetime

# simple export helper (optional)
def dump_schema(model, out_path: pathlib.Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(model.model_json_schema(), f, indent=2)

if __name__ == "__main__":
    base = pathlib.Path(__file__).parent
    dump_schema(WeatherPack, base / "weather_pack.schema.json")
    dump_schema(CropPack, base / "crop_pack.schema.json")
    dump_schema(SafetyRulesPack, base / "safety_rules.schema.json")
    print("Schemas exported")
