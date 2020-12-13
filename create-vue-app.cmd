@echo off

set "SOURCE_FILES_PATH=%~dp0vue-app\"
for %%I in (.) do set DIRNAME=%%~nxI

mkdir src
mkdir server\templates
mkdir server\static
set PYTHON_PACKAGE_DIRNAME=server\packages
mkdir %PYTHON_PACKAGE_DIRNAME%

copy /-y "%SOURCE_FILES_PATH%.env" .env
copy /-y "%SOURCE_FILES_PATH%requirements.txt" requirements.txt
copy /-y "%SOURCE_FILES_PATH%webpack.config.js" webpack.config.js
copy /-y "%SOURCE_FILES_PATH%app.js" src\app.js
copy /-y "%SOURCE_FILES_PATH%index.html" server\templates\index.html
rmdir "%SOURCE_FILES_PATH%packages\db\__pycache__" /s /q
xcopy "%SOURCE_FILES_PATH%packages" %PYTHON_PACKAGE_DIRNAME% /e /-y

set OVERWRITE=y
set APP_VUE=src\App.vue
if exist %APP_VUE% (
	set /p OVERWRITE="%APP_VUE% exists. Enter y to overwrite: "
) 
if %OVERWRITE%==y (
	type nul>%APP_VUE%
)

set OVERWRITE=y
set APP_PY=server\app.py
if exist %APP_PY% (
	set /p OVERWRITE="%APP_PY% exists. Enter y to overwrite: "
) 
if %OVERWRITE%==y (
	type nul>%APP_PY%
)

call npm init -y

set "ENV_PATH=%USERPROFILE%\.envs\%DIRNAME%"
mkdir "%ENV_PATH%"
call python -m venv "%ENV_PATH%"

"%ENV_PATH%\Scripts\pip3" install -r requirements.txt

set OVERWRITE=y
set "CUSTOM_PATHS=%ENV_PATH%\Lib\site-packages\custom-paths.pth"
if exist "%CUSTOM_PATHS%" (
	set /p OVERWRITE="%CUSTOM_PATHS% exists. Enter y to overwrite: "
) 
if %OVERWRITE%==y (
	echo %cd%\%PYTHON_PACKAGE_DIRNAME%>%CUSTOM_PATHS%
)

call npm i @babel/core @babel/preset-env babel-loader css-loader webpack@4.44.1 webpack-cli@3.3.12 webpack-dev-server node-sass@4.14.1 sass-loader style-loader vue-loader vue-template-compiler @babel/plugin-transform-runtime --save-dev
call npm i vue vue-router vuex dotenv axios @babel/polyfill

cmd \k