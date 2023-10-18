CONFIG=.env
include ${CONFIG}

deploy:
	gcloud functions deploy GA4-access-logs \
	--gen2 \
	--project=$(PROJECT) \
	--region=europe-west2 \
	--runtime=python310 \
	--source=. \
	--entry-point=run
