@echo off
cd /d "<path_to_your_frida_tool_directory>/cli_tool.py"
uv run cli_tool.py %*
