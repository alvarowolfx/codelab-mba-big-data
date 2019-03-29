export BUCKET_NAME=mba-senai-alvaro-bucket
export PROJECT_ID=mba-senai-codelab
export BQ_DATASET=mba_senai_mensageria

python3 -m main \
  --input_subscription projects/$PROJECT_ID/subscriptions/photos-classification	 \
  --output ./output.txt \
  --dataset $BQ_DATASET \
  --project $PROJECT_ID \
  --setup_file ./setup.py 