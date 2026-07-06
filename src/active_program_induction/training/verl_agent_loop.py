from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from active_program_induction.env import ActiveInductionEnv, initial_messages

try:  # pragma: no cover - exercised only inside a veRL runtime.
    from verl.experimental.agent_loop.agent_loop import (
        AgentLoopBase,
        AgentLoopMetrics,
        AgentLoopOutput,
        register,
    )
except Exception:  # pragma: no cover - lets local CPU tests import this module without veRL.

    class AgentLoopBase:  # type: ignore[no-redef]
        pass

    @dataclass
    class AgentLoopMetrics:  # type: ignore[no-redef]
        generate_sequences: float = 0.0
        tool_calls: float = 0.0
        compute_score: float = 0.0
        num_preempted: int = -1

    @dataclass
    class AgentLoopOutput:  # type: ignore[no-redef]
        prompt_ids: list[int]
        response_ids: list[int]
        response_mask: list[int]
        reward_score: float | None = None
        num_turns: int = 0
        metrics: AgentLoopMetrics = field(default_factory=AgentLoopMetrics)
        extra_fields: dict[str, Any] = field(default_factory=dict)

    def register(name: str):  # type: ignore[no-redef]
        def deco(cls):
            return cls

        return deco


@register("active_program_induction")
class ActiveProgramInductionAgentLoop(AgentLoopBase):
    """veRL AgentLoop for true adaptive active program induction.

    Rollout sequence:
    1. Render the public task prompt.
    2. Ask the model for one JSON action.
    3. If it queries, execute the hidden oracle and append the observation as
       environment tokens with response_mask=0.
    4. Repeat until submit or budget/turn cap.
    5. Return the complete token trajectory and terminal reward.
    """

    async def run(self, sampling_params: dict[str, Any], **kwargs) -> AgentLoopOutput:
        task = _load_task(kwargs)
        env = ActiveInductionEnv(task, reward_mode="graded")
        messages = kwargs.get("raw_prompt") or initial_messages(task)
        prompt_ids = await self.apply_chat_template(messages)
        runtime_ids: list[int] = []
        response_mask: list[int] = []
        request_id = f"{task['task_id']}-{uuid4().hex[:8]}"
        max_turns = int(task["public"]["probe_budget"]) + 2
        final_reward = -0.1
        final_info: dict[str, Any] = {"error": "no_submit"}

        for _turn in range(max_turns):
            generation_ids = await self.server_manager.generate(
                request_id,
                prompt_ids=prompt_ids + runtime_ids,
                sampling_params=sampling_params,
            )
            generation_ids = list(generation_ids)
            action_text = self.tokenizer.decode(generation_ids, skip_special_tokens=True)
            runtime_ids.extend(generation_ids)
            response_mask.extend([1] * len(generation_ids))

            step = env.step_text(action_text)
            final_reward = step.reward
            final_info = step.info
            observation_text = "\nENVIRONMENT:\n" + step.observation + "\n"
            observation_ids = self.tokenizer.encode(observation_text, add_special_tokens=False)
            runtime_ids.extend(observation_ids)
            response_mask.extend([0] * len(observation_ids))

            if step.done:
                break

        return AgentLoopOutput(
            prompt_ids=prompt_ids,
            response_ids=runtime_ids,
            response_mask=response_mask,
            reward_score=float(final_reward),
            num_turns=max(1, len(env.queries) + int(env.done)),
            metrics=AgentLoopMetrics(),
            extra_fields={
                "task_id": task["task_id"],
                "family": task["family"],
                "equivalent": bool(final_info.get("equivalent", False)),
                "num_queries": len(env.queries),
            },
        )


def _load_task(kwargs: dict[str, Any]) -> dict:
    ground_truth = kwargs.get("ground_truth")
    if ground_truth is None and kwargs.get("reward_model"):
        reward_model = kwargs["reward_model"]
        if isinstance(reward_model, dict):
            ground_truth = reward_model.get("ground_truth")
    if ground_truth is None:
        raise ValueError("Agent loop requires serialized task JSON in ground_truth")
    return json.loads(ground_truth) if isinstance(ground_truth, str) else ground_truth
