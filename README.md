### Hi, I'm 一群小羊说 👋

**Multi-Platform Builder & Local-First AI Tooling Author**  
Building native desktop, mobile, and CLI tools across **macOS (`Swift 6` / `SwiftUI`)**, **Windows (`Rust` / `Tauri v2` / `WebView2` / `Electron`)**, **Android (`Kotlin` / `Jetpack Compose`)**, and **Apple Silicon Local AI Pipelines**.

[![X](https://img.shields.io/badge/X-@jryang1997-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/jryang1997)
[![SSPai](https://img.shields.io/badge/少数派-一群小羊说-D7191A?style=flat-square)](https://sspai.com/u/dub8fbmk/updates)

---

### Featured Open-Source Projects · 核心开源作品

| Project | Platforms & Stack | What It Solves |
| :--- | :--- | :--- |
| **[MenuBarMijia](https://github.com/jryang1997/MenuBarMijia)** | **macOS 26+** (`Swift 6`, `SwiftUI`)<br>**Windows 11** (`Tauri v2`, `Rust`, `TS`)<br>**Synology NAS** (`Shell`, `Docker`) | Native menu-bar & tray controller for **Xiaomi Mi Home (Mijia)** and **Home Assistant**. Supports zero-dependency Mi Cloud QR login, LAN WebSocket entity synthesis, press-and-hold voice control (`~0.2s` multi-device execution), and 5-second undo. Featured in [`awesome-mac`](https://github.com/jaywcjlove/awesome-mac). |
| **[omp-bot](https://github.com/jryang1997/omp-bot)** | **Windows Desktop** (`Electron`, `Node 24`)<br>**Web Workbench & CLI**<br>**Android 8.0+** (`Kotlin`, `Compose`)<br>**Shared Linux VM** (`WHPX`, `Xvfb`) | Resident multi-agent team powered by `omp` (`oh-my-pi`). Direct & group chats, bot-to-bot task delegation under a shared token budget, isolated per-bot Linux VM seats, QR-paired Android companion app, Feishu relay, and 3-tier host security guards. |
| **[dsh-hold-to-dictate](https://github.com/jryang1997/dsh-hold-to-dictate)** | **DeepSeek Harness** (`JavaScript`, `Cordis`) | Hold-to-talk & hands-free chord-tap voice dictation for the DeepSeek Harness composer. Reuses the host's local ASR model with zero external dependencies, sentence-boundary live preview, draft conflict protection, and optional AI polish. |
| **[dsh-ascii-whales](https://github.com/jryang1997/dsh-ascii-whales)** | **DeepSeek Harness** (`Canvas 2D`, `JS`) | Top-down procedural ASCII & shaded-cell whale school background for DeepSeek Harness. Five whale species, frosted-glass cards, toroidal screen wrapping, composer & fish-school avoidance, wind streaks, and drifting cloud shadows. |
| **[QuotaKeeper](https://github.com/jryang1997/QuotaKeeper)** | **Windows GUI** (`Rust`, `WebView2`)<br>**Terminal TUI** (`Ratatui`)<br>**Android** (`Kotlin` Glance) | Local-only subscription quota & token ledger monitor across 9 AI coding providers (`Claude Code`, `Codex`, `OpenCode`, `DSH`, `OMP`, `ZCode`, `Cursor`, `GLM`, `Kimi`, `MiniMax`) with traceable LiteLLM pricing snapshots. |
| **[hermes-opencode-go-quota](https://github.com/jryang1997/hermes-opencode-go-quota)** | **Hermes Desktop** (`JavaScript`, `Python`) | Native Hermes Desktop status-bar & dashboard plugin for OpenCode Go 5h/weekly/monthly usage quotas and DeepSeek API balance burn-rate forecasting. |

---

### Engineering Principles · 工程准则

- **Local-First & Zero Telemetry**: Credentials stay in the OS Keychain or Windows Credential Manager; session ledgers, speech recognition, and device control run directly from your machine without third-party relay servers.
- **Multi-Surface Cohesion**: A single domain model (`GLOSSARY.md` + `docs/adr/`) spans macOS menu bars, Windows system trays, terminal TUIs, web workbenches, and Android companion apps.
- **Minimal Dependencies & Real Verification**: Zero third-party Swift dependencies in `MenuBarMijia`; automated cross-platform CI gates and reproducible verification trails across every repository.
