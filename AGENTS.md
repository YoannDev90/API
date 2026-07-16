# Project Info

## Branches
- `main` — Tools API (math, dns, web, encode, etc.), no LLM
- `waifly` — Slim LLM API (Python, 300MB RAM, Pterodactyl)
- `render` — LiteLLM proxy (512MB RAM, Neon DB, admin UI)

## Deployment

### Waifly (llm4free)
- Panel: https://panel.waifly.com
- Server: API (0bbe7b1d), Node PAR2
- IP: 5.180.34.59:25529
- Env vars: `WAAFLY_PANEL`, `WAAFLY_API_KEY`, `WAAFLY_SERVER_ID`, `WAAFLY_SFTP_HOST`, `WAAFLY_SFTP_PORT`, `WAAFLY_SFTP_USER`, `WAAFLY_SFTP_PASS`, `WAAFLY_URL`
- Docker image: python-3.11
- Startup: `pip install -r requirements.txt && python -m uvicorn app:app --host 0.0.0.0 --port $SERVER_PORT`

### Render (litellm)
- URL: https://api-51hr.onrender.com
- Service: srv-d9brq3pkh4rs73bj8v7g
- Env vars: `LITELLM_MASTER_KEY`, `DATABASE_URL`
- Branch: render
- Deploy: auto from GitHub push

## Provider Status (deepai only)
- Working (14): gpt-oss-120b, gemini-2.5-flash-lite, llama-4-scout, llama-3.3-70b-instruct, deepseek-v3.2, llama-3.1-8b-instant, gemini-3-pro, gpt-4.1-nano, qwen3-30b, gpt-5-nano, gemma-3-12b, gemma2-9b, standard, super-genius
- Disabled: freeai, freeai_online, netwrck, ai4chat

## CLI Commands
- Render logs: `render logs --resources srv-d9brq3pkh4rs73bj8v7g --limit 50`
- Deploy Waifly: `python deploy_waifly.py` (Pterodactyl API)

## Prisma
- Regenerate: run `generate-prisma.yml` workflow on GitHub Actions
- Pre-generated client in `prisma_client/` directory
- Schema: litellm's `proxy/schema.prisma`
