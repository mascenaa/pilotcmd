from pilotcmd.models.base import (
    BaseModel,
    ModelResponse,
    ModelType,
)
from pilotcmd.nlp.parser import NLPParser
from pilotcmd.os_utils.detector import OSInfo, OSType


class DummyModel(BaseModel):
    async def generate_response(
        self, prompt: str, **kwargs
    ) -> ModelResponse:  # pragma: no cover - not used
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


def test_parse_response_includes_steps():
    model = DummyModel("dummy")
    os_info = OSInfo(
        type=OSType.LINUX,
        name="Linux",
        version="1",
        architecture="x86_64",
        shell="/bin/bash",
    )
    parser = NLPParser(model, os_info)
    json_response = (
        '{"commands": ['
        '{"step": 1, "command": "echo one", "explanation": "first"},'
        '{"step": 2, "command": "echo two", "explanation": "second"}'
        "]}"
    )
    result = parser._parse_model_response(json_response)
    assert result.commands[0].step == 1
    assert result.commands[1].step == 2
