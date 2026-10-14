"""Local design automation through the discovered Figcraft MCP stdio tools.

This drives Figcraft's native engine. It does not implement the portfolio website
and never starts the Figcraft GUI. Calls are recorded for design provenance.
"""
import json
import pathlib
import subprocess
import threading
import queue


class Figcraft:
    def __init__(self, attach_port=None, timeout=120):
        self.timeout = timeout
        arguments = [r"C:\Program Files\FigCraft\figcraft-cli.exe", "mcp"]
        if attach_port is not None:
            arguments.extend(["--attach", str(attach_port)])
        self.process = subprocess.Popen(
            arguments,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.next_id = 0
        self.responses = queue.Queue()
        self.log = []
        threading.Thread(target=self._read, daemon=True).start()
        try:
            self.initialized = self.rpc("initialize", {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "ayman-portfolio-native-design", "version": "1.0"},
            })
        except Exception:
            self.process.terminate()
            self.process.wait(timeout=5)
            raise
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.process.stdin.flush()

    def _read(self):
        for line in self.process.stdout:
            try:
                self.responses.put(json.loads(line))
            except json.JSONDecodeError:
                pass

    def rpc(self, method, params):
        self.next_id += 1
        request = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params}
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        while True:
            response = self.responses.get(timeout=self.timeout)
            if response.get("id") == self.next_id:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response["result"]

    def tool(self, name, arguments=None):
        result = self.rpc("tools/call", {"name": name, "arguments": arguments or {}})
        if result.get("isError"):
            raise RuntimeError({"tool": name, "arguments": arguments, "result": result})
        self.log.append({"name": name, "arguments": arguments or {}, "success": True})
        if any(item.get("type") == "image" for item in result.get("content", [])):
            return result
        texts = [item["text"] for item in result.get("content", []) if item.get("type") == "text"]
        if len(texts) == 1:
            try:
                return json.loads(texts[0])
            except json.JSONDecodeError:
                return texts[0]
        return result

    def command(self, command, params=None):
        return self.tool("run_command", {"command": command, "params": params or {}})

    def close(self):
        self.process.stdin.close()
        self.process.wait(timeout=15)

    def save_log(self, path):
        pathlib.Path(path).write_text(json.dumps(self.log, indent=2), encoding="utf-8")
