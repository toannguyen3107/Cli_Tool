# Frida Tools - Android Hacking Toolkit

A comprehensive command-line toolkit for Android security testing and device management.

## 🚀 Quick Start

### Command Line Interface
```bash
# Using UV (recommended)
uv run cli_tool.py -h

# Direct Python
python cli_tool.py -h
```

### MCP Server (AI Integration)
```bash
# Start MCP server for AI assistants
uv run python mcp_server.py

# Or use batch script
start_mcp_server.bat
```

## 📱 Available Commands

```shell
usage: cli_tool.py [-h] {connect,devices,install_cert,klfrida,packages,proxy,reboot,signapk} ...

CLI tool to run specific jobs.

positional arguments:
  {connect,devices,install_cert,klfrida,packages,proxy,reboot,signapk}
                        Available commands
    connect             Connect to device via ADB WiFi
    devices             List all connected devices
    install_cert        Install a certificate with ip and port.
    klfrida             kill and list frida server
    packages            List all installed packages
    proxy               Manage proxy settings
    reboot              Reboot the device
    signapk             Sign an APK file

options:
  -h, --help            show this help message and exit
```

## 🤖 MCP Integration

This toolkit includes a Model Context Protocol (MCP) server that allows AI assistants to control your Android device through natural language.

### Setup for Claude Desktop
1. Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "frida-tools": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "E:\\Tools\\MyHackingTools\\Frida-tool"
    }
  }
}
```

2. Start using natural language:
   - "List all connected devices"
   - "Connect to device at 192.168.1.100"
   - "Set proxy to 192.168.1.50:8080"
   - "Install certificate from burp suite"

See [MCP_README.md](MCP_README.md) for detailed MCP documentation.

## 🛠️ Installation Options

### Option 1: Batch Script (Windows)
```batch
# Add e:\Tools\MyHackingTools\Frida-tool to PATH
# Then use anywhere:
frida-tool devices
frida-tool connect -H 192.168.1.100
```

### Option 2: Python Package
```bash
# Install as editable package
uv pip install -e .

# Use globally:
frida-tool devices
```
