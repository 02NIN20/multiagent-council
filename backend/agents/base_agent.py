"""Base class for all council agents.

Provides:
- OpenAI-compatible async call to Qwen Cloud API
- Prompt construction helpers for Inverted Pyramid + Given-New
- Abstract `analyze` method that subclasses must implement
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from openai import AsyncOpenAI

from backend.config import settings
from backend.models.schemas import Finding

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base agent.

    Parameters
    ----------
    name : str
        Unique agent identifier (e.g. "security", "architecture").
    role_description : str
        Short description of the agent's speciality.
    """

    def __init__(self, name: str, role_description: str) -> None:
        self.name = name
        self.role_description = role_description

        self._client = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            timeout=settings.qwen_timeout_seconds,
        )
        self._model = settings.qwen_model

    # ──────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────

    @abstractmethod
    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Analyse *code* and return a list of findings.

        Parameters
        ----------
        code : str
            Source code to review.
        context : list[dict] | None
            Findings from previous rounds (other agents' output) for cross-debate.
        round : int
            Current debate round (1, 2, or 3).

        Returns
        -------
        list[Finding]
            Zero or more findings in Inverted Pyramid format.
        """
        ...

    # ──────────────────────────────────────────────
    #  Prompt helpers
    # ──────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        """System prompt that sets the agent's role and output format."""
        return (
            f"Eres un experto en {self.role_description} especializado en code review. "
            "Tu tarea es analizar código fuente y encontrar problemas relacionados con tu especialidad.\n\n"
            "Debes responder ÚNICAMENTE con una lista de hallazgos en el siguiente formato "
            "(Pirámide Invertida). Cada hallazgo debe tener esta estructura exacta:\n\n"
            "HALLAZGO: <conclusión principal en 1 línea>\n"
            "··· Detalle: <evidencia concreta del código: archivo, línea, fragmento>\n"
            "··· Impacto: <Crítico | Alto | Medio | Bajo>\n"
            "··· Propuesta: <acción correctiva sugerida>\n\n"
            "Reglas:\n"
            "- No incluyas texto adicional fuera del formato especificado.\n"
            "- Si no encuentras problemas, responde únicamente: \"NO_HAY_HALLAZGOS\"\n"
            "- Cada hallazgo debe estar separado por una línea en blanco.\n"
            "- Sé específico: menciona líneas de código, fragmentos, y nombres de variables/funciones reales.\n"
            "- Usa el nivel de impacto correcto: Crítico (vulnerabilidad/error grave), "
            "Alto (problema significativo), Medio (mejora importante), Bajo (sugerencia menor)."
        )

    def _build_round_intro(self, round: int) -> str:
        """Instructions for the current debate round."""
        if round == 1:
            return (
                "### Ronda 1: Análisis Individual\n"
                "Analiza el código a continuación y produce tus hallazgos de forma independiente."
            )
        elif round == 2:
            return (
                "### Ronda 2: Debate Cruzado\n"
                "A continuación recibirás los hallazgos de otros agentes del consejo. "
                "Debes aplicar el principio **Dado-Nuevo**: cada hallazgo debe empezar "
                "refiriéndose explícitamente a un hallazgo de otro agente.\n\n"
                "Usa frases como:\n"
                "- \"Coincidiendo con [Agente] sobre [hallazgo], agrego que...\"\n"
                "- \"Discrepo de [Agente] sobre [hallazgo] porque...\"\n"
                "- \"Complementando a [Agente] sobre [hallazgo], añado...\"\n\n"
                "Mantén el mismo formato de Pirámide Invertida para cada hallazgo."
            )
        elif round == 3:
            return (
                "### Ronda 3: Refinamiento Final\n"
                "Has visto los argumentos de todos los agentes. Ahora debes refinar tu postura:\n"
                "- Puedes MANTENER, MODIFICAR o RETIRAR cada uno de tus hallazgos.\n"
                "- Si modificas un hallazgo, explica brevemente por qué.\n"
                "- Si retiras un hallazgo, indica explícitamente: \"RETIRADO: ...\"\n"
                "- Mantén el formato Pirámide Invertida para los hallazgos que conservas."
            )
        return ""

    def _build_context_block(self, context: list[dict[str, Any]] | None, round: int) -> str:
        """Format previous-round findings as context for the agent."""
        if not context or round == 1:
            return ""
        block_parts = ["\n### Hallazgos de la ronda anterior:\n"]
        for i, item in enumerate(context, 1):
            agent_name = item.get("agent", f"Agente {i}")
            block_parts.append(f"\n--- {agent_name} ---")
            hallazgo = item.get("hallazgo", "")
            detalle = item.get("detalle", "")
            impacto = item.get("impacto", "")
            propuesta = item.get("propuesta", "")
            block_parts.append(f"HALLAZGO: {hallazgo}")
            if detalle:
                block_parts.append(f"··· Detalle: {detalle}")
            if impacto:
                block_parts.append(f"··· Impacto: {impacto}")
            if propuesta:
                block_parts.append(f"··· Propuesta: {propuesta}")
        return "\n".join(block_parts)

    def _build_user_prompt(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> str:
        """Assemble the full user prompt."""
        parts = [
            self._build_round_intro(round),
            self._build_context_block(context, round),
            f"\n\n### Código a revisar:\n\n```\n{code}\n```",
        ]
        if round > 1:
            parts.append(
                "\n\nInstrucciones adicionales:\n"
                "- Recuerda aplicar Dado-Nuevo en tus respuestas.\n"
                "- Cada hallazgo debe empezar con una referencia explícita a otro agente.\n"
                "- Mantén el formato Pirámide Invertida."
            )
        if round == 3:
            parts.append(
                "\n\nInstrucciones adicionales:\n"
                "- Indica si MANTIENES, MODIFICAS o RETIRAS cada hallazgo.\n"
                "- Si RETIRAS, pon \"RETIRADO:\" al inicio.\n"
                "- Para hallazgos que mantienes, usa el formato Pirámide Invertida."
            )
        return "\n".join(parts)

    # ──────────────────────────────────────────────
    #  LLM call
    # ──────────────────────────────────────────────

    async def _call_llm(self, user_prompt: str) -> str:
        """Send a chat completion request to Qwen Cloud API and return the text response."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            content: str | None = response.choices[0].message.content
            return content or "NO_HAY_HALLAZGOS"
        except Exception:
            logger.exception("[%s] LLM call failed", self.name)
            return "NO_HAY_HALLAZGOS"

    # ──────────────────────────────────────────────
    #  Response parsing
    # ──────────────────────────────────────────────

    def _parse_findings(self, text: str, round: int) -> list[Finding]:
        """Parse the LLM response into a list of Findings."""
        if not text or text.strip() == "NO_HAY_HALLAZGOS":
            return []

        findings: list[Finding] = []
        blocks = text.strip().split("\n\n")

        for block in blocks:
            if "RETIRADO:" in block:
                continue  # skip withdrawn findings
            block = block.strip()
            if not block:
                continue

            finding = self._parse_single_finding(block, round)
            if finding is not None:
                findings.append(finding)

        return findings

    def _parse_single_finding(self, block: str, round: int) -> Finding | None:
        """Parse a single Inverted Pyramid text block into a Finding."""
        lines = block.split("\n")
        hallazgo = ""
        detalle = ""
        impacto = ""
        propuesta = ""

        for line in lines:
            line = line.strip()
            if line.startswith("HALLAZGO:"):
                hallazgo = line[len("HALLAZGO:"):].strip()
            elif line.startswith("··· Detalle:") or line.startswith("···Detalle:"):
                detalle = line.split(":", 1)[1].strip() if ":" in line else ""
            elif line.startswith("··· Impacto:") or line.startswith("···Impacto:"):
                impacto = line.split(":", 1)[1].strip() if ":" in line else ""
            elif line.startswith("··· Propuesta:") or line.startswith("···Propuesta:"):
                propuesta = line.split(":", 1)[1].strip() if ":" in line else ""

        if not hallazgo:
            return None

        impacto = self._normalize_impact(impacto)

        return Finding(
            agent=self.name,
            hallazgo=hallazgo,
            detalle=detalle,
            impacto=impacto,
            propuesta=propuesta,
            ronda=round,
        )

    @staticmethod
    def _normalize_impact(impacto: str) -> str:
        """Normalize impact level to one of Crítico|Alto|Medio|Bajo."""
        normalized = impacto.lower().strip()
        if "critico" in normalized or "crítico" in normalized:
            return "Crítico"
        if "alto" in normalized:
            return "Alto"
        if "medio" in normalized:
            return "Medio"
        if "bajo" in normalized:
            return "Bajo"
        return "Medio"
