-include .env
GCP_PROJECT_ID := ga4-analytics-352613

login:
	gcloud auth application-default login --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/bigquery --billing-project=$(GCP_PROJECT_ID)
	
set-project:	
	gcloud auth application-default set-quota-project $(GCP_PROJECT_ID)

deploy:
	gcloud functions deploy GA4-access-logs \
	--gen2 \
	--project=$(GCP_PROJECT_ID) \
	--region=europe-west2 \
	--runtime=python310 \
	--source=. \
	--entry-point=run
