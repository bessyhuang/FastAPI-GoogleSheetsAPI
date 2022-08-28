import uvicorn
import gspread
import re

from oauth2client.service_account import ServiceAccountCredentials as SAC
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from typing import List



Json = "steel-minutia-360807-5bd357009c2d.json"
Url = ["https://spreadsheets.google.com/feeds"]
Connect = SAC.from_json_keyfile_name(Json, Url)
GoogleSheets = gspread.authorize(Connect)
Sheet = GoogleSheets.open_by_key("1to2X5mibQdtxWGMBS_zq0vdBXC3TWLA6YKP4W2piulY")
Sheets = Sheet.sheet1


class Info(BaseModel):
    id: int
    data: List[str] = ["Bessy", "test", "321"]


app = FastAPI()


@app.get("/users/")
async def getAllData():
    return Sheets.get_all_records()

@app.get("/users/{userName}")
async def FindUsernameInfo(userName: str):
    userName_re = re.compile(r'^{}'.format(userName))
    cell = Sheets.find(userName_re)
    if cell == None:
        return "Username {} doesn't exist in Google Sheet.".format(userName)
    else:
        r = cell.row
        x = [item for item in Sheets.row_values(r) if item]
        return f"在第{cell.col}直行,第{cell.row}橫列,{x}"

@app.post("/users/")
async def AddNewUsernameInfo(info: Info):
	Sheets.append_row(info.data)
	return {"status": "SUCCESS", "data": info}

@app.put("/users/{userName}")
async def UpdateExistUsernameInfo(userName: str, modified_account: Union[str, None] = None, modified_password: Union[str, None] = None):
    cell = Sheets.find(userName)
    if cell == None:
        return "Username {} doesn't exist in Google Sheet.".format(userName)
    else:
        r = cell.row
        Sheets.update(f"B{r}:C{r}", [[modified_account, modified_password]])
        x = [item for item in Sheets.row_values(r) if item]
        return {"msg": x}

@app.delete("/users/{userName}")
async def DeleteExistUsernameInfo(userName: str):
    userName_re = re.compile(r'^{}'.format(userName))
    cell = Sheets.find(userName_re)
    if cell == None:
        return "Username {} doesn't exist in Google Sheet.".format(userName)
    else:
        r = cell.row
        Sheets.delete_row(r)
        return f"UserName {userName} 原本位於第 {cell.row} 橫列，現已刪除！"



if __name__ == "__main__":
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, debug=True)

