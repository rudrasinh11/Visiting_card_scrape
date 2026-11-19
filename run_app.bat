@echo off
title Visiting Card Scanner - Red & White Edition
cd /d "E:\visiting-card-scanner"
echo ========================================================
echo   Starting Visiting Card Scanner (Local - Drive E)
echo   Offline OCR - Zero API Costs
echo ========================================================
python -m streamlit run app.py
pause
