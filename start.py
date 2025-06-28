import uvicorn

if __name__ == "__main__":
    uvicorn.run("rockauto:rockauto_api", host="0.0.0.0", port=8000, reload=True)
