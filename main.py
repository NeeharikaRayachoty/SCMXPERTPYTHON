from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from routers import login,signup,dashboard,shipment,devicedata,password
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(HTTPException)
async def redirect_to_login(request: Request, exc: HTTPException) -> Response:
     # pylint: disable=unused-argument
    if exc.status_code == 401:
        # Redirect to login page
        return HTMLResponse("<script>window.location.href = '/login';</script>")
    # Re-raise the exception for other status codes
    raise exc

app.include_router(login.app)
app.include_router(signup.app)
app.include_router(dashboard.app)
app.include_router(shipment.app)
app.include_router(devicedata.app)
app.include_router(password.app)



