#!/usr/bin/env python3
"""
MCP Server for Frida Hacking Tools
Provides access to various Android hacking tools through Model Context Protocol
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import subprocess
import os
import re

# MCP imports
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Tool imports
from utils.adb_utils import run_adb_command_retn
from utils.color_utils import ANSI

class FridaToolsMCPServer:
    def __init__(self):
        self.server = Server("frida-tools")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="adb_devices",
                    description="List all connected Android devices via ADB",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="adb_connect",
                    description="Connect to Android device via ADB WiFi",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host": {
                                "type": "string",
                                "description": "IP address of the device"
                            },
                            "port": {
                                "type": "string", 
                                "description": "Port number (default: 5555)",
                                "default": "5555"
                            }
                        },
                        "required": ["host"]
                    }
                ),
                types.Tool(
                    name="list_packages",
                    description="List all installed packages on Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Optional filter for package names"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="proxy_get",
                    description="Get current proxy settings on Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="proxy_set",
                    description="Set proxy settings on Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host": {
                                "type": "string",
                                "description": "Proxy server IP address"
                            },
                            "port": {
                                "type": "string",
                                "description": "Proxy server port (default: 8080)",
                                "default": "8080"
                            }
                        },
                        "required": ["host"]
                    }
                ),
                types.Tool(
                    name="proxy_unset",
                    description="Remove proxy settings from Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="install_certificate",
                    description="Install SSL certificate on Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "host": {
                                "type": "string",
                                "description": "Host to download certificate from"
                            },
                            "port": {
                                "type": "string",
                                "description": "Port to download certificate from",
                                "default": "8080"
                            },
                            "cert_path": {
                                "type": "string",
                                "description": "Local path to certificate file (if not downloading)"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="frida_kill_list",
                    description="Kill running Frida server and list available Frida versions",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="reboot_device",
                    description="Reboot the connected Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="sign_apk",
                    description="Sign an APK file with keystore",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "apk_file": {
                                "type": "string",
                                "description": "Path to APK file to sign"
                            },
                            "keystore": {
                                "type": "string",
                                "description": "Path to keystore file",
                                "default": "C:\\share\\tools\\MyHackingTools\\Frida-tool\\config\\my-release-key.keystore"
                            },
                            "keypass": {
                                "type": "string",
                                "description": "Keystore password",
                                "default": "toannguyen"
                            }
                        },
                        "required": ["apk_file"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "adb_devices":
                    return await self._adb_devices()
                elif name == "adb_connect":
                    return await self._adb_connect(arguments)
                elif name == "list_packages":
                    return await self._list_packages(arguments)
                elif name == "proxy_get":
                    return await self._proxy_get()
                elif name == "proxy_set":
                    return await self._proxy_set(arguments)
                elif name == "proxy_unset":
                    return await self._proxy_unset()
                elif name == "install_certificate":
                    return await self._install_certificate(arguments)
                elif name == "frida_kill_list":
                    return await self._frida_kill_list()
                elif name == "reboot_device":
                    return await self._reboot_device()
                elif name == "sign_apk":
                    return await self._sign_apk(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _run_adb_command(self, command: str) -> str:
        """Run ADB command and return output"""
        try:
            result = subprocess.run(['adb'] + command.split(), 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _run_tool_command(self, command: str) -> str:
        """Run frida-tool command"""
        try:
            result = subprocess.run(['uv', 'run', 'cli_tool.py'] + command.split(),
                                  capture_output=True, text=True, timeout=60,
                                  cwd='e:\\Tools\\MyHackingTools\\Frida-tool')
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {str(e)}"

    async def _adb_devices(self) -> list[types.TextContent]:
        """List connected devices"""
        output = await self._run_adb_command("devices")
        return [types.TextContent(type="text", text=f"Connected devices:\n{output}")]

    async def _adb_connect(self, args: dict) -> list[types.TextContent]:
        """Connect to device via WiFi"""
        host = args["host"]
        port = args.get("port", "5555")
        output = await self._run_adb_command(f"connect {host}:{port}")
        return [types.TextContent(type="text", text=f"Connection result:\n{output}")]

    async def _list_packages(self, args: dict) -> list[types.TextContent]:
        """List installed packages"""
        filter_text = args.get("filter", "")
        command = "shell pm list packages"
        if filter_text:
            command += f" | grep {filter_text}"
        output = await self._run_adb_command(command)
        return [types.TextContent(type="text", text=f"Installed packages:\n{output}")]

    async def _proxy_get(self) -> list[types.TextContent]:
        """Get proxy settings"""
        output = await self._run_adb_command("shell su -c 'settings get global http_proxy'")
        return [types.TextContent(type="text", text=f"Current proxy settings:\n{output}")]

    async def _proxy_set(self, args: dict) -> list[types.TextContent]:
        """Set proxy settings"""
        host = args["host"]
        port = args.get("port", "8080")
        proxy_setting = f"{host}:{port}"
        output = await self._run_adb_command(f"shell su -c 'settings put global http_proxy {proxy_setting}'")
        return [types.TextContent(type="text", text=f"Proxy set to {proxy_setting}\n{output}")]

    async def _proxy_unset(self) -> list[types.TextContent]:
        """Unset proxy settings"""
        output = await self._run_adb_command("shell su -c 'settings put global http_proxy :0'")
        return [types.TextContent(type="text", text=f"Proxy settings cleared\n{output}")]

    async def _install_certificate(self, args: dict) -> list[types.TextContent]:
        """Install certificate"""
        cmd_parts = ["install_cert"]
        if "host" in args and "port" in args:
            cmd_parts.extend(["-H", args["host"], "-P", args["port"]])
        elif "cert_path" in args:
            cmd_parts.extend(["-p", args["cert_path"]])
        
        output = await self._run_tool_command(" ".join(cmd_parts))
        return [types.TextContent(type="text", text=f"Certificate installation result:\n{output}")]

    async def _frida_kill_list(self) -> list[types.TextContent]:
        """Kill Frida and list versions"""
        output = await self._run_tool_command("klfrida")
        return [types.TextContent(type="text", text=f"Frida server management:\n{output}")]

    async def _reboot_device(self) -> list[types.TextContent]:
        """Reboot device"""
        output = await self._run_adb_command("reboot")
        return [types.TextContent(type="text", text=f"Device reboot initiated\n{output}")]

    async def _sign_apk(self, args: dict) -> list[types.TextContent]:
        """Sign APK file"""
        apk_file = args["apk_file"]
        keystore = args.get("keystore", "C:\\share\\tools\\MyHackingTools\\Frida-tool\\config\\my-release-key.keystore")
        keypass = args.get("keypass", "toannguyen")
        
        cmd_parts = ["signapk", "-af", apk_file, "--keystore", keystore, "--keypass", keypass]
        output = await self._run_tool_command(" ".join(cmd_parts))
        return [types.TextContent(type="text", text=f"APK signing result:\n{output}")]

async def main():
    """Main server entry point"""
    server_instance = FridaToolsMCPServer()
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="frida-tools",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
