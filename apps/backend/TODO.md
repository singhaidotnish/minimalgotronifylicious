# ✅ TODO List for Algomin

## 🟢 In Progress
- [ ] Refactor `websocket_client.py` for SRP compliance (#refactor)
- [ ] Integrate `EMAObserver` with new config loading logic (#observer, #live)
- [ ] Finish FastAPI start/stop routes (#api)

## 🔜 Next Up
- [ ] Add CLI entry point using `pyproject.toml` [cli/run_client.py]
- [ ] Validate `common.yaml` using `pydantic` or schema (#config)
- [ ] Build `/ws/stream` for frontend (#frontend)

## 🧪 Tests
- [ ] Unit test `LimitOrderPlacerObserver` for edge cases (#tests)
- [ ] Add test cases for YAML loader errors (#config)

## 📝 Notes
- Frontend and CLI must share same config base.
- Keep observers independent and hot-pluggable.


Use GitHub Issues + Labels (if public/private repo)
If you’re already on GitHub:

Create issues per task

Add labels like enhancement, bug, api, cli

Link issues to commits and PRs

Bonus: You can convert TODO.md into issues using GitHub Copilot or manually with the "Convert to Issue" button in checklists.