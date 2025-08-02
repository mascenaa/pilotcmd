from pilotcmd.models.base import BaseModel, ModelResponse, ModelType


class DummyModel(BaseModel):
    async def generate_response(self, prompt: str, **kwargs) -> ModelResponse:  # pragma: no cover - not used
        return ModelResponse(content="", model="dummy")

    def is_available(self) -> bool:  # pragma: no cover - not used
        return True

    @property
    def model_type(self) -> ModelType:  # pragma: no cover - not used
        return ModelType.LOCAL


def test_thinking_prompt_includes_step_by_step():
    model = DummyModel("dummy", thinking=True)
    prompt = model.get_system_prompt().lower()
    assert "step-by-step reasoning" in prompt
