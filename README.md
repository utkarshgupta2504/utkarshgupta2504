<a href="https://curvet.ai"><img src="assets/hero.svg" width="100%" alt="Utkarsh Gupta, Co-Founder & CTO of Curvet. I build AI products end to end."></a>

<p align="center">
  <a href="https://curvet.ai"><img src="assets/pill-curvet.svg" height="38" alt="curvet.ai"></a>
  <a href="https://utkarshg.is-a.dev"><img src="assets/pill-site.svg" height="38" alt="utkarshg.is-a.dev"></a>
  <a href="https://linkedin.com/in/utkarshgupta2504"><img src="assets/pill-linkedin.svg" height="38" alt="LinkedIn"></a>
  <a href="https://x.com/Utkarsh2504"><img src="assets/pill-x.svg" height="38" alt="X / Twitter"></a>
  <a href="https://www.npmjs.com/package/@curvet/sdk"><img src="assets/pill-npm.svg" height="38" alt="npm"></a>
  <a href="mailto:utkarshgupta2504@gmail.com"><img src="assets/pill-email.svg" height="38" alt="Email"></a>
</p>

<img src="assets/stats.svg" width="100%" alt="100+ AI models behind one API · 28 providers · 3 npm packages · 10M+ Galaxy users at Samsung">

<br>

### Building Curvet

[Curvet](https://curvet.ai) puts every major model for chat, image, video, voice and 3D behind one interface, one API key and one balance. I built it from zero and run engineering: the model router, the workflow engine, the agent runtime, voice, billing, and the infra under all of it.

<a href="https://curvet.ai"><img src="assets/router.svg" width="100%" alt="Animated diagram: a request with model auto is scored by Curvet's router, the first provider returns 429, and it falls back to the next provider which returns 200."></a>

<details>
<summary><b>Try it from your terminal</b></summary>
<br>

```bash
npm i -g @curvet/cli
curvet chat -m auto "who is utkarsh?"
```

<img src="assets/terminal.svg" width="100%" alt="Terminal: the Curvet CLI answering who Utkarsh is">

The CLI also runs as an MCP server (`curvet mcp`), so Claude, Cursor and other agents can use Curvet as a tool. SDK: [`@curvet/sdk`](https://www.npmjs.com/package/@curvet/sdk).

</details>

<br>

### Selected work

<p align="center">
  <a href="https://curvet.ai"><img src="assets/card-curvet.svg" width="49%" alt="Curvet: every AI model, one workspace"></a>
  <a href="https://github.com/Curvet-in/curvet-sdk"><img src="assets/card-sdk.svg" width="49%" alt="@curvet/sdk + cli"></a>
  <a href="https://github.com/utkarshgupta2504/cline-testgen"><img src="assets/card-testgen.svg" width="49%" alt="cline-testgen"></a>
  <a href="https://github.com/pragati-kumar/NaviFinder-Hackerchiefs"><img src="assets/card-navifinder.svg" width="49%" alt="NaviFinder"></a>
</p>

<details>
<summary><b>Earlier projects</b></summary>
<br>

| | | |
|---|---|---|
| [**NSUTx**](https://github.com/zenghost1/NSUTx) | My university portal, rebuilt as an app. 10K+ downloads on Google Play. | Flutter · Firebase |
| [**ConnectX**](https://github.com/pranjaljain584/ConnectX) | Video conferencing with chat, file sharing and a shared whiteboard. | React · WebRTC · Socket.io |
| [**Sensus**](https://github.com/samartharoraa/Sensus) | A journal that senses your mood, 85%+ accurate over 1,000+ entries. | React · NLP · AWS |

</details>

<br>

### The path so far

<img src="assets/timeline.svg" width="100%" alt="Timeline: NSUT 2019 to 2023, startups and freelance 2021 to 2023, Samsung R&D 2023 to 2026, Curvet from 2026">

<details>
<summary><b>Curvet</b> · Co-Founder & CTO · 2026 – now</summary>
<br>

- One interface, API key and credit balance across 100+ models from 28 providers.
- "Auto" model selection over a scored registry (quality, strengths, live price) with cross-provider fallback chains, so a failing provider degrades to a working answer instead of an error.
- A visual workflow builder whose run-time core is one module executed by both the browser and a headless server runner, so the two can't drift.
- An agent runtime with tiered, search-loaded tools and prompt caching, cutting the fixed prompt overhead of a simple request by more than half.
- The developer platform: an OpenAI-compatible API used from Cline and OpenCode, plus `@curvet/sdk`, `@curvet/cli` and an MCP server.
- Indian-language speech recognition and TTS, and a self-hosted voice engine with cloning.
- Production on GCP with tracing end to end (OpenTelemetry, Grafana, PostHog), a load-test harness and a ~350-file backend test suite.

</details>

<details>
<summary><b>Samsung R&D Institute</b> · SWE → Senior SWE · 2023 – 2026</summary>
<br>

- Next-Gen Connectivity: machine learning for the Galaxy Multi-Device Experience.
- Cut on-device network switching latency 3x with a deep-learning approach.
- Built internal automation that took 30% off the team's workload.
- Cross-device connectivity features used by 10M+ Galaxy users. Promoted to Senior in 2025.

</details>

<details>
<summary><b>Startups & freelance</b> · Flutter → full stack → tech lead · 2021 – 2023</summary>
<br>

- **Shakespeare AE**, Member of Technical Staff: rebuilt the Flutter app on a custom design system (40% less duplication), moved the backend from Hasura to Node + MongoDB (25% faster APIs), and built a full restaurant PoS on one real-time socket backend.
- **MyEra**, Technical Lead: a personalization engine embedded by 10+ retail brands through iframes with two-way postMessage callbacks.
- **Kalpas Innovations**, Core Developer: a Flutter dating app with video calls and geo matchmaking; crashes down 50%.
- Plus Wyden, Naxome, Blobdesign and Humming Sparrow, and a summer at Samsung R&D on speech enhancement with GANs.

</details>

<br>

### Stack

<img src="assets/stack.svg" width="100%" alt="Stack: LLM orchestration, agents, MCP, model routing, TypeScript, Python, Node.js, React, Flutter, GCP and more">

<br>

### On GitHub

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=utkarshgupta2504&show_icons=true&include_all_commits=true&count_private=true&hide_border=false&border_radius=16&bg_color=0c0c0f&border_color=27272a&title_color=fafafa&text_color=a1a1aa&icon_color=a78bfa&ring_color=8b5cf6" height="170" alt="GitHub stats">
  <img src="https://github-readme-stats.vercel.app/api/top-langs?username=utkarshgupta2504&layout=compact&hide_border=false&border_radius=16&bg_color=0c0c0f&border_color=27272a&title_color=fafafa&text_color=a1a1aa" height="170" alt="Top languages">
</p>
<p align="center">
  <img src="https://streak-stats.demolab.com/?user=utkarshgupta2504&background=0c0c0f&border=27272a&border_radius=16&stroke=27272a&ring=8b5cf6&fire=db2777&currStreakNum=fafafa&sideNums=fafafa&currStreakLabel=a78bfa&sideLabels=a1a1aa&dates=71717a" width="70%" alt="Contribution streak">
</p>

<details>
<summary><code>$ curvet --whoami --json</code></summary>
<br>

```json
{
  "name": "Utkarsh Gupta",
  "role": "Co-Founder & CTO @ Curvet",
  "based_in": "Bengaluru, India",
  "previously": ["Senior SWE @ Samsung R&D", "Flutter + full stack @ startups"],
  "building": ["model routing", "agent runtimes", "voice", "the apps on top"],
  "ask_me_about": ["LLM infra", "MCP", "shipping fast with a small team"],
  "wins": [
    "Smart India Hackathon 2022 finalist (ISRO)",
    "12th of 6,700 at CodeJitsu, IIT Guwahati",
    "Won EduThon, IIIT Lucknow, against 600+ teams"
  ],
  "resume": "https://utkarshg.is-a.dev/Utkarsh_Gupta_Resume.pdf"
}
```

</details>

<br>

<a href="https://curvet.ai"><img src="assets/footer.svg" width="100%" alt="Curvet: every model, one workspace"></a>

<!-- Images in assets/ are generated: edit scripts/build.py and re-run it. -->
