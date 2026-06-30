# Qwen Council — Plan de Implementación

## Información del Proyecto

- **Hackathon**: Global AI Hackathon Series with Qwen Cloud (Devpost)
- **Track**: 3 — Agent Society
- **Deadline**: July 9, 2026
- **Participantes**: ~6,000
- **Premio**: $7,000 + $3,000 en créditos cloud

## Concepto

**Qwen Council** es un sistema multi-agente donde 5 especialistas con memoria persistente debaten colaborativamente para realizar code review. La innovación clave es un **protocolo de comunicación inter-agente** basado en principios de lingüística cognitiva (Pirámide Invertida, Dado-Nuevo, alta cohesión, autosuficiencia), donde cada mensaje entre agentes está estructurado para minimizar ambigüedad y maximizar la eficiencia del debate.

---

## 1. Agentes del Consejo

| ID | Agente | Especialidad |
|:---|:-------|:-------------|
| `security` | 🛡️ Seguridad | Inyección SQL, XSS, hardcoded secrets, autenticación, OWASP Top 10 |
| `architecture` | 🏗️ Arquitectura | Patrones de diseño, acoplamiento, SOLID, escalabilidad, separación de concerns |
| `quality` | 📐 Calidad | Estilo de código, convenciones, código muerto, tests faltantes, complejidad ciclomática |
| `performance` | ⚡ Performance | Cuellos de botella, N+1 queries, falta de caché, uso ineficiente de recursos |
| `ux` | ♿ UX / Accesibilidad | Accesibilidad (a11y), i18n, mensajes de error, feedback al usuario, contraste |

---

## 2. Protocolo de Comunicación

### Formato de Mensaje: Pirámide Invertida

Cada agente produce mensajes con esta estructura:

```
HALLAZGO: [conclusión principal en 1 línea]
··· Detalle: [evidencia concreta del código: archivo, línea, fragmento]
··· Impacto: [Crítico / Alto / Medio / Bajo]
··· Propuesta: [acción correctiva sugerida]
```

### Principios aplicados

| Principio | Aplicación en el protocolo |
|:-----------|:---------------------------|
| **Pirámide invertida** | El hallazgo principal va PRIMERO, en una línea. El lector (otro agente) entiende lo esencial en 1 segundo. |
| **Dado-Nuevo (Given-New)** | En rondas 2+, cada agente empieza refiriéndose explícitamente a hallazgos de otros: *"Coincidiendo con [Agente] sobre [hallazgo], agrego que..."* |
| **Alta cohesión** | Conectores explícitos (Coincido, Discrepo, Complemento). Referencias directas a líneas de código. |
| **Autosuficiencia** | Cada mensaje incluye el contexto mínimo para entenderse sin leer mensajes anteriores. |
| **Minimalismo** | Sin relleno. Solo: hallazgo, evidencia, impacto, propuesta. |

---

## 3. Ciclo de Debate

### Ronda 1: Análisis Individual
- Cada agente recibe el código fuente completo
- Produce su análisis individual en formato Pirámide Invertida
- Los 5 outputs se recopilan para la ronda 2

### Ronda 2: Debate Cruzado
- Cada agente recibe los outputs de los otros 4 agentes
- Aplica Dado-Nuevo: "Coincido/discrepo con [Agente] sobre [hallazgo]..."
- Puede: confirmar, refutar, matizar, o agregar evidencia adicional
- Los 5 outputs actualizados se recopilan para la ronda 3

### Ronda 3: Refinamiento
- Cada agente ve los debates de ronda 2
- Actualiza su postura: mantiene, modifica o retira sus hallazgos
- Produce versión final de sus hallazgos

### Síntesis Final
- Un agente consolidador (o paso automático) produce el reporte final
- Para cada hallazgo: voto de cada agente, nivel de consenso, prioridad
- Formato del reporte:

```
═══════════════════════════════════════════════════════
  REPORTE DE CODE REVIEW — QWEN COUNCIL
═══════════════════════════════════════════════════════

ARCHIVO: src/app.py

HALLAZGOS:

1. [CRÍTICO] Inyección SQL en línea 45
   Votos: Seguridad(CRÍTICO) + Arquitecto(ALTO) + Calidad(ALTO)
   Consenso: 5/5
   Propuesta: Usar consultas parametrizadas

2. [ALTO] Función de 300 líneas sin dividir
   Votos: Calidad(ALTO) + Arquitecto(ALTO) + Performance(MEDIO)
   Consenso: 4/5 (UX se abstiene)
   Propuesta: Extraer validación y procesamiento a módulos separados

...
```

---

## 4. Arquitectura de Memoria (3 Niveles + Curva de Olvido)

### Nivel 1: Memoria de Trabajo (volátil)
| Atributo | Valor |
|:---------|:------|
| Almacenamiento | Memoria Python (dict en el orquestador) |
| Contenido | Código siendo revisado, hallazgos de ronda actual, estado del debate |
| Ciclo de vida | Se crea al iniciar sesión, se destruye al cerrar |
| Al cerrar | Los hallazgos pasan a Episódica (Nivel 2) |

### Nivel 2: Memoria Episódica (PostgreSQL)
| Atributo | Valor |
|:---------|:------|
| Almacenamiento | Tabla `episodic_memory` en Alibaba RDS PostgreSQL |
| Contenido | Sesiones completas: código revisado, hallazgos, votos, decisiones, timestamp |
| Retención | Últimas 20 sesiones activas |
| Curva de olvido | Score base = 1.0. Decae -0.1/día sin referencia. Se recupera +0.3 al ser referenciado. Umbral de archive: score < 0.3. |
| Promoción | Si un patrón aparece 3+ veces en distintas sesiones → se promueve a Semántica |

### Nivel 3: Memoria Semántica (PostgreSQL + pgvector)
| Atributo | Valor |
|:---------|:------|
| Almacenamiento | Tabla `semantic_memory` con embeddings pgvector |
| Contenido | Preferencias del usuario, reglas aprendidas, patrones consolidados, decisiones arquitectónicas |
| Embeddings | Generados con Qwen API (text-embedding) |
| Ciclo de vida | Permanente hasta invalidación explícita del usuario |
| Inyección | Solo memorias con score > 0.5 se inyectan en el prompt de nueva sesión |

---

## 5. Stack Tecnológico

| Componente | Tecnología | Razón |
|:-----------|:-----------|:------|
| LLM | Qwen2.5 (Qwen Cloud API) | Obligatorio para la hackathon |
| Backend | Python 3.11 + FastAPI | Rápido, async, tipado |
| Base de datos | PostgreSQL 15 + pgvector | Embeddings + consultas híbridas |
| Frontend | React 18 + Tailwind CSS + Vite | Dashboard visual de debate en vivo, control total de UI |
| Cache | Redis (Memory DB Alibaba) | Sesiones activas, rate limiting |
| Contenedores | Docker + docker-compose | Despliegue reproducible |
| Cloud | Alibaba ECS + RDS | Requisito de la hackathon |
| API Base | https://dashscope-intl.aliyuncs.com/compatible-mode/v1 | OpenAI-compatible |

---

## 6. Estructura del Repositorio

```
qwen-council/
├── README.md
├── LICENSE
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── plan.md
├── docs/
│   ├── architecture.md          # Diagrama + descripción
│   └── alibaba-deployment.md    # Prueba de despliegue en Alibaba
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Settings (Qwen API key, DB URL, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py           # Pydantic models
│   │   └── db.py                # SQLAlchemy engine + session
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Clase base para todos los agentes
│   │   ├── security_agent.py
│   │   ├── architecture_agent.py
│   │   ├── quality_agent.py
│   │   ├── performance_agent.py
│   │   └── ux_agent.py
│   ├── council/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Orquestador del debate (3 rondas)
│   │   ├── protocol.py          # Formateo de mensajes Pirámide Invertida
│   │   └── synthesizer.py       # Síntesis final + reporte
│   └── memory/
│       ├── __init__.py
│       ├── working_memory.py    # Nivel 1 (volátil)
│       ├── episodic_memory.py   # Nivel 2 (PostgreSQL + olvido)
│       ├── semantic_memory.py   # Nivel 3 (pgvector)
│       └── consolidator.py      # Promoción Episódica → Semántica
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── package.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── council.ts           # Llamadas al backend FastAPI
│   │   ├── components/
│   │   │   ├── CodeInput.tsx         # Editor de código
│   │   │   ├── AgentCard.tsx         # Tarjeta individual de agente
│   │   │   ├── AgentGrid.tsx         # Grid de 5 agentes con estados
│   │   │   ├── DebateTimeline.tsx    # Timeline de rondas (1/2/3)
│   │   │   ├── MessageBubble.tsx     # Burbuja individual de hallazgo
│   │   │   ├── FinalReport.tsx       # Tabla de reporte final
│   │   │   └── CouncilHeader.tsx     # Encabezado con rondas
│   │   └── types/
│   │       └── index.ts              # Tipos (Agent, Finding, Round, Report)
│   └── public/
└── tests/
    ├── test_agents.py
    ├── test_council.py
    └── test_memory.py
```

---

## 7. Plan de Implementación (7 Días)

| Día | Actividad | Subagente |
|:---:|:----------|:----------|
| 1 | Backend: FastAPI + config + modelos DB + Dockerfile | @backend-dev |
| 2 | Agentes: 5 prompts + base_agent + protocolo comunicación | @backend-dev |
| 3 | Consejo: orquestador 3 rondas + synthesizer | @backend-dev |
| 4 | Memoria: 3 niveles + pgvector + curva de olvido + consolidación | @db-architect + @backend-dev |
| 5 | Frontend: React + Tailwind + Vite (CodeInput, AgentGrid, DebateTimeline, FinalReport) | @frontend-dev |
| 6 | Tests + Seguridad + Despliegue en Alibaba ECS | @tester + @security + @devops |
| 7 | Video 3 min + Diagrama arquitectura + README + Docs finales | @documenter |

---

## 8. Video de 3 Minutos (Estructura)

```
0:00-0:30 │ PROBLEMA: Los code reviews humanos son lentos y un solo agente AI es limitado
0:30-1:00 │ ARQUITECTURA: 5 especialistas + protocolo Pirámide Invertida + memoria 3 niveles
1:00-2:00 │ DEMO: Pegar código → Ronda 1 (individual) → Ronda 2 (debate) → Ronda 3 + Síntesis
2:00-2:30 │ MEMORIA: "¿Recuerdas mi preferencia de la semana pasada?" → la recupera
2:30-3:00 │ MÉTRICA: Sin consejo vs con consejo. Despedida + link al repo
```

---

## 9. Criterios de Evaluación (Cómo ganamos puntos)

| Criterio | Peso | Cómo lo cumplimos |
|:---------|:----:|:------------------|
| **Technical Depth** | 30% | Qwen Cloud API + pgvector + sistema multi-agente con protocolo propio |
| **Innovation & Creativity** | 30% | Protocolo lingüístico inter-agente (Pirámide Invertida + Dado-Nuevo). Memoria con curva de olvido. Único. |
| **Problem Value & Impact** | 25% | Code review es un problema real y medible. Ahorra horas/equipo/semana. |
| **Presentation & Docs** | 15% | Diagrama claro, video conciso, README impecable, demo funcional en vivo. |

---

## 10. Definición de Éxito (MVP)

- [x] 5 agentes responden con formato Pirámide Invertida
- [x] 3 rondas de debate funcionan end-to-end
- [x] Reporte de síntesis con votos y consenso
- [x] Memoria episódica persiste entre sesiones
- [x] Curva de olvido funciona (score decae y se recupera)
- [x] Frontend Streamlit muestra el debate en vivo
- [x] Desplegado en Alibaba ECS con RDS
- [x] Video de 3 min en YouTube
- [x] Diagrama de arquitectura en docs/
- [ ] **Plus**: comparativa "con consejo vs sin consejo" con métricas
