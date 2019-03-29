# Lab Big Data Interativo com Spark e Dataproc

## Criar cluster Hadoop 

## Configurar GCS

* Criar um bucket com nome `mba-senai-{seu-nome}-bucket`
* `export BUCKET_NAME=mba-senai-{seu-nome}-bucket`

## Baixar arquivo e copiar para bucket

* wget https://github.com/databricks/Spark-The-Definitive-Guide/raw/master/data/bike-data/201508_station_data.csv
* wget https://github.com/databricks/Spark-The-Definitive-Guide/raw/master/data/bike-data/201508_trip_data.csv
* gsutil cp 201508_station_data.csv gs://${BUCKET_NAME}/csv/201508_station_data.csv
* gsutil cp 201508_trip_data.csv gs://${BUCKET_NAME}/csv/201508_trip_data.csv

## Entrar no Master node via SSH

## Abrir shell do pyspark

* pyspark
