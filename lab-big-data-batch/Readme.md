# Lab Big Data Batch com Spark e Dataproc

## Criar cluster Hadoop 

## Configurar GCS

* Criar um bucket com nome `mba-senai-{seu-nome}-bucket`
* `export BUCKET_NAME=mba-senai-{seu-nome}-bucket`

## Copiar arquivo de texto

* gsutil cp gs://pub/shakespeare/rose.txt gs://${BUCKET_NAME}/input/rose.txt

## Criar arquivo word-count.py

## Executar job no cluster

* gcloud dataproc jobs submit pyspark word-count.py \
    --cluster=${CLUSTER} \
    --region=us-central1 \
    -- gs://${BUCKET_NAME}/input/ gs://${BUCKET_NAME}/output/

## Ver resultados

* gsutil cat gs://${BUCKET_NAME}/output/*