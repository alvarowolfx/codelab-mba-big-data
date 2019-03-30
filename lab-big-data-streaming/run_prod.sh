python main.py \
  --input_subscription projects/$PROJECT_ID/subscriptions/photos-classification \
  --output ./output.txt \
  --dataset $BQ_DATASET \
  --project $PROJECT_ID \
  --runner DataflowRunner \
  --temp_location gs://$BUCKET_NAME/photos_classification/temp \
  --staging_location gs://$BUCKET_NAME/photos_classification/staging \
  --machine_type n1-standard-1 \
  --max_num_workers 1 \
  --setup_file ./setup.py 

