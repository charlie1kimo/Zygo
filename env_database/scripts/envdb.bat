@echo off

if not "%1" == "" (
	python -m env_database.scripts.%1
) else (
	python -m env_database.env_plots2.env_plots2
)