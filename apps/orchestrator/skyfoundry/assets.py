from pathlib import Path
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field

class AssetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(max_length=500)
    category: Literal["sculpture", "furniture", "landscape_prop", "construction_prop", "decorative_roof_feature"]
    target_size_m: tuple[float, float, float]
    triangle_budget: int = Field(ge=100, le=100_000)
    seed: int

class AssetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ready", "disabled"]
    local_path: str | None = None
    provider: str

class AssetGenerationProvider(Protocol):
    async def generate(self, request: AssetRequest) -> AssetResult: ...

class MockAssetGenerationProvider:
    async def generate(self, request: AssetRequest) -> AssetResult:
        return AssetResult(status="ready", local_path="assets/fixtures/mock-planter.glb", provider="mock")

class LocalFolderAssetProvider:
    def __init__(self, root: Path): self.root = root.resolve()
    async def generate(self, request: AssetRequest) -> AssetResult:
        candidate = (self.root / f"{request.category}.glb").resolve()
        if self.root not in candidate.parents or not candidate.is_file(): return AssetResult(status="disabled", provider="local_folder")
        if candidate.stat().st_size > 25_000_000: return AssetResult(status="disabled", provider="local_folder")
        return AssetResult(status="ready", local_path=str(candidate), provider="local_folder")

class TrellisProvider:
    def __init__(self, enabled: bool = False): self.enabled = enabled
    async def generate(self, request: AssetRequest) -> AssetResult:
        if not self.enabled: return AssetResult(status="disabled", provider="trellis")
        raise RuntimeError("A separately deployed, validated TRELLIS endpoint is required")

