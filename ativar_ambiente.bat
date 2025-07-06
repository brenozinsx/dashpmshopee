@echo off
echo ========================================
echo    Dashboard Operacao Shopee
echo ========================================
echo.
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
echo Instalando dependencias (se necessario)...
pip install -r requirements.txt

echo.
echo Iniciando o dashboard...
echo.
echo O dashboard sera aberto em: http://localhost:8501
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
streamlit run app.py

pause 