@echo on

:: 输出日志，说明开始执行脚本
echo Running the script...

:: 激活 conda 环境
echo Activating conda environment 'pkg'...
call conda activate pkg
if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment 'pkg'.
    exit /b %errorlevel%
)

:: 确保进入 Pipenv 虚拟环境
echo Activating pipenv virtual environment...
call pipenv shell
if %errorlevel% neq 0 (
    echo Error: Failed to activate pipenv environment.
    exit /b %errorlevel%
)

:: 显示当前环境
echo Current environment:
where python
where pyinstaller

:: 执行 pyinstaller 打包命令
echo Running pyinstaller...
pyinstaller --exclude PyQt6 --onefile --windowed --add-data "instruction.png;." main.py
if %errorlevel% neq 0 (
    echo Error: pyinstaller failed to run.
    exit /b %errorlevel%
)

:: 可选：退出 pipenv 和 conda 环境
echo Exiting pipenv and conda environment...
exit
