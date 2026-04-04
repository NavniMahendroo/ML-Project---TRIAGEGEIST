from pydantic import BaseModel, ConfigDict


class SiteDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_id: str
    name: str
