
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "sw_dashboard.server:app",
        host="127.0.0.1",
        port=8088,
    )
