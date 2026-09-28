from src.app import register_routers

if __name__ == '__main__':
    import uvicorn

    register_routers()
    uvicorn.run("src.app:app", host='0.0.0.0')