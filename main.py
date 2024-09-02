from fastapi import FastAPI
import Add_file, read_files, update_file, delete_file, authentication
import oauth2

app = FastAPI(title='MultiTenants')


app.include_router(authentication.router)
app.include_router(oauth2.router)
app.include_router(Add_file.router)
app.include_router(read_files.router)
app.include_router(update_file.router)
app.include_router(delete_file.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)