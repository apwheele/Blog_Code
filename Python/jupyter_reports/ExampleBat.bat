::===============================================================
:: This is an example bat file for Windows
:: so you can schedule a job to run when you are 
:: away from your computer
:: this is what is needed to work with anaconda prompt
:: need to switch conda_act line to wherever it is located
:: on your machine
::===============================================================

@echo on
set "base=%cd%"
set conda_act=D:\Python\Scripts\activate.bat
call %conda_act% 
call cd %base%
call python 01_CreateReport.py
