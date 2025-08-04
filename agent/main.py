import os

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    print(f"Starting server on port {os.environ.get("MCP_PATH")}")
    uvicorn.run("agent:app", host="0.0.0.0", port=port, log_config=None)