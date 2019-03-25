python3 -m main \
  --input_subscription projects/mba-senai-codelab/subscriptions/photos-classification \
  --output ./output.txt \
  --dataset mba_senai_mensageria \
  --project mba-senai-codelab \
  --runner DataflowRunner \
  --temp_location gs://mba-senai-alvaro-bucket/photos_classification/temp \
  --staging_location gs://mba-senai-alvaro-bucket/photos_classification/staging \
  --machine_type n1-standard-1 \
  --max_num_workers 1 \
  --setup_file ./setup.py \
  --experiment ignore_py3_minor_version

