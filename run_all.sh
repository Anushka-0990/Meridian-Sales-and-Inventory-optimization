#!/usr/bin/env bash
# Reproducible end-to-end pipeline for Meridian Retail Analytics
set -e
echo "== 1/4 ETL & data quality =="
python3 01_ETL_and_clean.py
echo "== 2/4 SQL business analysis =="
python3 02_run_sql_analysis.py
echo "== 3/4 Modelling (forecast + ABC/XYZ + policy) =="
python3 03_model_inventory.py
echo "== 4/4 Client Excel deliverable =="
python3 04_build_excel_deliverable.py
echo "Done. See /outputs, /images and retail_analytics_deliverable.xlsx"
