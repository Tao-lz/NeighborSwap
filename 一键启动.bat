@echo off
setlocal enabledelayedexpansion
chcp 936 >nul
title 邻里交换 NeighborSwap 一键启动
cd /d "%~dp0"

echo.
echo  ============================================================
echo    邻里交换 NeighborSwap  -  社区闲置物品流转平台
echo  ============================================================
echo.

if not exist "backend\app\main.py" goto :BAD_DIR
if not exist "frontend\package.json" goto :BAD_DIR

rem ---------- 找一个能用的 Python ----------
set "PY=python"
%PY% -c "import sys" >nul 2>&1
if not errorlevel 1 goto :PY_OK
set "PY=py -3"
%PY% -c "import sys" >nul 2>&1
if not errorlevel 1 goto :PY_OK
goto :NO_PYTHON
:PY_OK

rem ---------- 检查 Node ----------
where npm >nul 2>&1
if errorlevel 1 goto :NO_NODE

rem ---------- 检查 curl，用来等后端就绪 ----------
set "HAVE_CURL=0"
where curl >nul 2>&1
if not errorlevel 1 set "HAVE_CURL=1"

rem ---------- 后端虚拟环境 ----------
if not exist "backend\.venv\Scripts\python.exe" goto :MAKE_VENV
goto :CHECK_DEPS

:MAKE_VENV
echo  [*] 第一次运行：创建 Python 虚拟环境...
%PY% -m venv backend\.venv
if errorlevel 1 goto :VENV_FAIL

:CHECK_DEPS
"backend\.venv\Scripts\python.exe" -c "import fastapi,uvicorn,sqlalchemy,openai" >nul 2>&1
if errorlevel 1 goto :INSTALL_BACKEND
goto :CHECK_DB

:INSTALL_BACKEND
echo  [*] 安装后端依赖，大约 1-3 分钟...
"backend\.venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto :PIP_BACKEND_FAIL

rem ---------- 数据库 ----------
:CHECK_DB
if exist "backend\neighborswap.db" goto :CHECK_FRONT
echo  [*] 首次运行：生成演示数据...
pushd "backend"
".venv\Scripts\python.exe" seed.py
set "SEED_RC=!errorlevel!"
popd
if not "!SEED_RC!"=="0" echo  [!] 演示数据生成失败，可以继续启动，首页会是空的。

rem ---------- 前端依赖 ----------
:CHECK_FRONT
if not exist "frontend\node_modules" goto :INSTALL_FRONT
if not exist "frontend\node_modules\.bin\vite.cmd" goto :INSTALL_FRONT
goto :CHECK_RUNNING

:INSTALL_FRONT
echo  [*] 安装前端依赖，大约 2-5 分钟，请勿关闭窗口...
pushd "frontend"
call npm install
set "NPM_RC=!errorlevel!"
popd
if "!NPM_RC!"=="0" goto :CHECK_RUNNING
echo  [!] 默认源安装失败，改用国内镜像重试...
pushd "frontend"
call npm install --registry=https://registry.npmmirror.com
set "NPM_RC=!errorlevel!"
popd
if not "!NPM_RC!"=="0" goto :NPM_FAIL

rem ---------- 已经在运行？ ----------
:CHECK_RUNNING
if "%HAVE_CURL%"=="0" goto :START_ALL
curl -s --max-time 2 http://127.0.0.1:8000/openapi.json | findstr /c:"/api/dashboard" >nul
if errorlevel 1 goto :START_ALL
curl -s -o NUL --max-time 2 http://127.0.0.1:5173
if errorlevel 1 goto :START_ALL
echo  [*] 服务已经在运行，直接打开浏览器。
start "" http://localhost:5173
goto :END

rem ---------- 启动 ----------
:START_ALL
echo  [*] 启动后端  端口 8000 ...
start "邻里交换 - 后端" /d "%~dp0backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

if "%HAVE_CURL%"=="0" goto :SLEEP_BACK

set /a TRY=0
:WB_LOOP
set /a TRY+=1
if !TRY! GTR 40 goto :BACK_SLOW
ping -n 2 127.0.0.1 >nul
curl -s -o NUL --max-time 2 http://127.0.0.1:8000/api/health
if not errorlevel 1 goto :BACK_OK
goto :WB_LOOP

:SLEEP_BACK
ping -n 9 127.0.0.1 >nul
goto :BACK_OK

:BACK_SLOW
echo  [!] 后端 40 秒内没有就绪，仍然尝试启动前端。
echo      请查看"邻里交换 - 后端"窗口里的报错。

:BACK_OK
echo  [*] 启动前端  端口 5173 ...
start "邻里交换 - 前端" /d "%~dp0frontend" cmd /k "npm run dev"

if "%HAVE_CURL%"=="0" goto :SLEEP_FRONT

set /a TRY=0
:WF_LOOP
set /a TRY+=1
if !TRY! GTR 40 goto :FRONT_SLOW
ping -n 2 127.0.0.1 >nul
curl -s -o NUL --max-time 2 http://127.0.0.1:5173
if not errorlevel 1 goto :FRONT_OK
goto :WF_LOOP

:SLEEP_FRONT
ping -n 9 127.0.0.1 >nul
goto :FRONT_OK

:FRONT_SLOW
echo  [!] 前端 40 秒内没有就绪，请查看"邻里交换 - 前端"窗口。

:FRONT_OK
echo.
echo  ============================================================
echo    启动完成
echo      前端页面 : http://localhost:5173
echo      后端接口 : http://127.0.0.1:8000/docs
echo      健康检查 : http://127.0.0.1:8000/api/health
echo.
echo    会弹出两个黑色窗口，分别运行后端和前端。
echo    演示结束后，关闭这两个窗口即可停止服务，
echo    或者双击同目录下的 停止服务.bat。
echo  ============================================================
echo.
start "" http://localhost:5173
goto :END

rem ================= 出错提示 =================

:BAD_DIR
echo  [x] 当前目录不对。
echo      请把本脚本放在能看到 backend、frontend 两个文件夹的那一层，再双击运行。
goto :FAIL

:NO_PYTHON
echo  [x] 没有找到可用的 Python。
echo      请安装 Python 3.11 或更高版本，安装时勾选 "Add Python to PATH"。
echo      下载地址：https://www.python.org/downloads/
goto :FAIL

:NO_NODE
echo  [x] 没有找到 Node.js / npm。
echo      前端需要 Node.js 18 或更高版本。
echo      下载地址：https://nodejs.org/zh-cn
goto :FAIL

:VENV_FAIL
echo  [x] 创建虚拟环境失败。
echo      可能是 Python 安装不完整，或 backend 目录不可写。
goto :FAIL

:PIP_BACKEND_FAIL
echo  [x] 后端依赖安装失败。可以手动重试：
echo      backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
goto :FAIL

:NPM_FAIL
echo  [x] 前端依赖安装失败。可以手动重试：
echo      cd frontend
echo      npm install --registry=https://registry.npmmirror.com
goto :FAIL

:FAIL
echo.
pause
exit /b 1

:END
echo.
pause
exit /b 0
