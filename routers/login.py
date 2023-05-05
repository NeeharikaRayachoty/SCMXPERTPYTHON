import datetime as dt
from config.config import Setting
from fastapi import APIRouter,Request,Form,HTTPException, status, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Dict, List, Optional
from jose import JWTError, jwt


app = APIRouter()

TEMPLATES = Jinja2Templates(directory="templates")

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
   """Function to change plain password to Hash"""
   return PWD_CONTEXT.hash(password)
def verify_password(password: str, hashed_password: str):
   """Function to verify hased password"""
   return PWD_CONTEXT.verify(password, hashed_password)

class login(BaseModel):
   Email: str
   Password: str

class OAuth2PasswordBearerWithCookie(OAuth2):
 def __init__(
       self,
       tokenUrl: str,
       scheme_name: Optional[str] = None,
       scopes: Optional[Dict[str, str]] = None,
       description: Optional[str] = None,
       auto_error: bool = True,
 ):
       if not scopes:
          scopes = {}
       flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
       super().__init__(
       flows=flows,
       scheme_name=scheme_name,
       description=description,
       auto_error=auto_error,
       )
 async def __call__(self, request: Request) -> Optional[str]:
    authorization: str = request.cookies.get(Setting.COOKIE_NAME)
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        if self.auto_error:
            raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Not authenticated",
               headers={"WWW-Authenticate": "Bearer"},
               )
        else:
            return None
    return param

OAUTH2_SCHEME = OAuth2PasswordBearerWithCookie(tokenUrl="token")

def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=Setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role":data.get("role")})
    encoded_jwt = jwt.encode(
        to_encode,
        Setting.SECRET_KEY,
        algorithm=Setting.ALGORITHM
    )
    return encoded_jwt
SIGNUP_COLLECTION = Setting.User
def get_user(email: str) -> login:
    user = SIGNUP_COLLECTION.find_one({"Email":email})
    if user:
        return user
    return None

def authenticate_user(username: str, plain_password: str) -> login:
    user = get_user(username)
    if not user:
        return False
    if not verify_password(plain_password, user['Password']):
        return False
    return user

def get_current_user_from_cookie(request: Request) -> login:
    token = request.cookies.get(Setting.COOKIE_NAME)
    user = decode_token(token)
    return user

def decode_token(token: str) -> login:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )
    token = str(token).replace("Bearer", "").strip()

    try:
        payload = jwt.decode(token, Setting.SECRET_KEY, algorithms=[Setting.ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = get_user(username)
    return user

def get_current_user_from_token(token: str = Depends(OAUTH2_SCHEME)) -> login:
    user = decode_token(token)
    return user

@app.post("token")
def login_for_access_token(response: Response,\
        form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:

    # Authenticate the user with the provided credentials
    user = authenticate_user(form_data.login_user, form_data.login_password)
    if not user:
        # If the user is not authenticated, raise an HTTPException with 401 status code
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, \
            detail="Incorrect username or password")

    # Create an access token for the authenticated user
    access_token = create_access_token(data={"username": user["Email"], "role":user["Role"]})

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=Setting.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )
    # Return the access token and token type in a dictionary
    return {Setting.COOKIE_NAME: access_token, "token_type": "bearer"}


class LoginForm:
    """
    A class that represents a login form and provides methods to load and validate form data.

    Attributes:
        request (Request): A `Request` object representing the incoming HTTP request.
        errors (List): A list of error messages that can be returned during form validation.
        login_user (Optional[str]): A string representing the user's login email,
        or `None` if not specified.
        login_password (Optional[str]): A string representing the user's login password,
        or `None` if not specified.
    """

    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.login_user: Optional[str] = None
        self.login_password: Optional[str] = None

    async def load_data(self):
        """
        Asynchronously loads form data from the incoming request
        and sets the `login_user` and `login_password`
        attributes of the `LoginForm` object.

        Args:
            self (LoginForm): The `LoginForm` object to load data into.

        Returns:
            None.
        """
        form = await self.request.form()
        self.login_user = form.get("email")
        self.login_password = form.get("password")

    async def is_valid(self):
        """
        Asynchronously validates the `LoginForm` object's `login_user`
        and `login_password` attributes and
        returns a boolean indicating whether the attributes are valid.

        If either the `login_user` or `login_password` attributes are invalid,
        an error message is added to
        the `errors` attribute of the `LoginForm` object.

        Args:
            self (LoginForm): The `LoginForm` object to validate.

        Returns:
            A boolean indicating whether the `login_user` and `login_password`
            attributes are valid and
            there are no errors. Returns `True` if the attributes are valid
            and there are no errors,
            otherwise `False`.
        """
        if not self.login_user or not (self.login_user.__contains__("@")):
            self.errors.append("Email is required")
        if not self.login_password or not len(self.login_password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


@app.get("/",response_class = HTMLResponse)
def login_get(request:Request):
   return TEMPLATES.TemplateResponse("login.html",{"request":request})
   
@app.post("/login",response_class = HTMLResponse)
async def login_post(request:Request, email:str=Form(...),password:str=Form(...)):
#    print(email)
   form = LoginForm(request)
   await form.load_data()
   try:
      if not await form.is_valid():
            # Form data is not valid
            raise HTTPException(status_code=400, detail="Form data is not valid")
        # Form data is valid, generate new access token
      response = RedirectResponse("/dashboard", status.HTTP_302_FOUND)
      login_for_access_token(response=response, form_data=form)
      form.__dict__.update(msg="Login Successful!")
      return response
   # response = RedirectResponse("/", status.HTTP_302_FOUND)
   # login_for_access_token(response=response, form_data=form)
   # login_data = login(Email=email,Password=password)
   # user = Setting.User.find_one({"Email":email})
   # print(user)
   # if not user:
   #    return TEMPLATES.TemplateResponse("login.html",{"request":request,"credentials":"User Not Registred yet!"})

   # if not verify_password(password,user['Password'] ):

   #    # login_data = Setting.User.insert_one(login_data.dict())
   #    return TEMPLATES.TemplateResponse("login.html",{"request":request,"credentials":"Invalid Credentials"})
   # return TEMPLATES.TemplateResponse("dashboard.html",{"request":request,"User":user['Username']})
   except HTTPException as exception:
      # Catch HTTPException and update form with error message
      form.__dict__.update(msg="")
      form.__dict__.get("errors").append(exception.detail)
      return TEMPLATES.TemplateResponse("login.html", form.__dict__)
   except Exception as exception:
      # Catch any other exception and return 500 Internal Server Error
      raise HTTPException(status_code=500, detail=str(exception)) from exception

      
# @app.get("/dashboard", response_class=HTMLResponse)
# def home_page(request: Request):
#     """Home Page"""
#     try:
#         user = get_current_user_from_cookie(request)
#     except ValueError:
#         user = None
#     context = {
#         "user": user,
#         "request": request,
#     }
#     return TEMPLATES.TemplateResponse("dashboard.html", context)

@app.get("/logout", response_class=HTMLResponse)
def logout_get():
    """
    Handle a GET request to the logout endpoint.
    This function deletes the authentication cookie and redirects the user to the root page ("/").
    The authentication cookie is deleted by setting its value to an empty string and setting its
    max age to 0. This ensures that the browser deletes the cookie on the client side.
    :return: A `RedirectResponse` object that redirects the user to the root page ("/").
    """
    try:
        response = RedirectResponse(url="/login")
        response.delete_cookie(Setting.COOKIE_NAME)
        print(response)
        return response
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Cookie name not found.") from exc
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception)) from exception





  




