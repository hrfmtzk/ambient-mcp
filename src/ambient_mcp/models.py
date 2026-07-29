from pydantic import BaseModel, Field, model_validator

Number = int | float


class FieldLabels(BaseModel):
    d1: str | None = None
    d2: str | None = None
    d3: str | None = None
    d4: str | None = None
    d5: str | None = None
    d6: str | None = None
    d7: str | None = None
    d8: str | None = None

    class Config:
        extra = "forbid"


class DataItem(BaseModel):
    created: str = Field(..., description="UTC timestamp (RFC 3339)")
    d1: Number | None = None
    d2: Number | None = None
    d3: Number | None = None
    d4: Number | None = None
    d5: Number | None = None
    d6: Number | None = None
    d7: Number | None = None
    d8: Number | None = None

    class Config:
        extra = "forbid"


class GetDataOutput(BaseModel):
    field_labels: FieldLabels = Field(
        ..., description="Labels for data fields (d1 to d8)."
    )
    items: list[DataItem] = Field(
        ..., description="Array of data items (timestamp and field values)."
    )


class GetDataErrorOutput(BaseModel):
    category: str = Field(
        ...,
        description=(
            "Error category (e.g., validation, timeout, forbidden, not_found, rate_limited)."
        ),
    )
    message: str = Field(..., description="Human-readable error message.")

    class Config:
        extra = "forbid"


GetDataResult = GetDataOutput | GetDataErrorOutput


class GetDataInput(BaseModel):
    read_key: str = Field(..., description="Ambient Read Key")
    channel_id: int = Field(..., ge=1, description="Target channel ID")
    from_: str | None = Field(
        None,
        alias="from",
        description="Start time (RFC 3339)",
    )
    to: str | None = Field(
        None,
        description="End time (RFC 3339)",
    )
    n: int | None = Field(
        None,
        ge=1,
        le=1_095_000,
        description="Number of latest items to retrieve (n)",
    )
    skip: int | None = Field(
        None,
        ge=0,
        description="Items to skip (used with n)",
    )
    fields: list[str] | None = Field(
        None,
        description="Field names to retrieve (all fields if omitted)",
    )

    class Config:
        extra = "forbid"

    @model_validator(mode="after")
    def validate_conditions(self) -> "GetDataInput":
        has_from = self.from_ is not None
        has_to = self.to is not None
        has_n = self.n is not None
        has_skip = self.skip is not None

        if has_from != has_to:
            raise ValueError("'from' and 'to' must be provided together.")

        if has_skip and not has_n:
            raise ValueError("'skip' requires 'n'.")

        if (has_from or has_to) and (has_n or has_skip):
            raise ValueError("Use either 'from/to' or 'n/skip', not both.")

        if not (has_from or has_to or has_n):
            raise ValueError("Either 'from/to' or 'n' must be provided.")

        return self
