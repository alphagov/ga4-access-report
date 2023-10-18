# GA4-access-report
This downloads the GA4 access records derived from the GA4 admin API and sends them to BigQuery so that you can see who is accessing a GA4 property.

The authentication to GA and BigQuery is handled by Google Application Default credentials so ensure you have run `gcloud auth login` to generate them if you are running this locally.

The code base is design to be deployed to Google Cloud Functions with a Cloud Scheduler hitting the http endpoint to trigger an exectution daily.


## Requirements


*   [Google Cloud Platform (GCP) project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) with [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project#enable-billing) - Create or use an existing project as needed.
    *   Note: This solution uses billable GCP resources.
*   [Google Analytics](https://analytics.google.com/analytics/web/)


### Environment variables needed
These can be set in a `.env` file

`GCP_PROJECT_ID` The project to host the Cloud Function and the BigQuery data

`GA4_ENTITY` in the format `properties/123456` or `accounts/123456`
