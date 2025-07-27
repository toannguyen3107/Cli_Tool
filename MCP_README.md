# Frida Tools MCP Server

This is a Model Context Protocol (MCP) server that provides access to various Android hacking tools through AI assistants.

## Features

The MCP server exposes the following tools:

### Device Management
- **adb_devices**: List all connected Android devices
- **adb_connect**: Connect to Android device via ADB WiFi
- **reboot_device**: Reboot the connected Android device

### Package Management
- **list_packages**: List all installed packages on Android device

### Proxy Management
- **proxy_get**: Get current proxy settings on Android device
- **proxy_set**: Set proxy settings on Android device
- **proxy_unset**: Remove proxy settings from Android device

### Security Tools
- **install_certificate**: Install SSL certificate on Android device
- **frida_kill_list**: Kill running Frida server and list available Frida versions
- **sign_apk**: Sign an APK file with keystore

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Start the MCP server:
```bash
uv run python mcp_server.py
```

Or use the batch script:
```bash
start_mcp_server.bat
```

## Configuration

### For Claude Desktop

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "frida-tools": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "e:\\Tools\\MyHackingTools\\Frida-tool",
      "env": {}
    }
  }
}
```

### For other MCP clients

Use the provided `mcp_config.json` file or adapt it to your client's configuration format.

## Usage Examples

Once connected to an AI assistant that supports MCP, you can use natural language to interact with your Android device:

- "List all connected devices"
- "Connect to device at 192.168.1.100"
- "Set proxy to 192.168.1.50:8080"
- "Install certificate from 192.168.1.50:8080"
- "List all installed packages"
- "Kill Frida server and show available versions"
- "Sign APK file at /path/to/app.apk"

## Requirements

- Python 3.12+
- UV package manager
- ADB (Android Debug Bridge) in PATH
- Connected Android device (USB or WiFi)
- Root access on Android device (for some features)

## Security Notes

- This tool requires root access on the Android device for proxy settings and certificate installation
- Ensure your Android device is properly secured when using these tools
- The certificate installation feature modifies system certificate store
