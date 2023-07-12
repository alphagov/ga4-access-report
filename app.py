from google.analytics.admin import AnalyticsAdminServiceClient
import pandas as pd
from datetime import datetime
from google.auth import default

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
PROJECT = 'ga4-analytics-352613'

creds, _ = default(scopes=SCOPES, quota_project_id=PROJECT)
client = AnalyticsAdminServiceClient(credentials=creds)
#client = AnalyticsAdminServiceClient()

access_dict = {
  "entity":"properties/330577055",
  "date_ranges": [
    {
      "start_date": "2daysAgo",
      "end_date": "1daysAgo"
    }
  ],
  "dimensions": [
    {
      "dimension_name": "epochTimeMicros"
    },
    {
      "dimension_name": "userEmail"
    },
    {
      "dimension_name": "accessMechanism"
    },
    {
      "dimension_name": "accessorAppName"
    },
    {
      "dimension_name": "dataApiQuotaCategory"
    },
    {
      "dimension_name": "reportType"
    }


  ],
  "metrics": [
    {
      "metric_name": "accessCount"
    },
    {
      "metric_name": "dataApiQuotaPropertyTokensConsumed"
    }
  ]
}

access_records = client.run_access_report(access_dict)

def print_access_report(response):
    """Prints the access report."""
    access_list = []

    for rowIdx, row in enumerate(response.rows):
        #print(f"\nRow {rowIdx}")
        dims = {}
        for i, dimension_value in enumerate(row.dimension_values):
            dimension_name = response.dimension_headers[i].dimension_name
            if dimension_name.endswith("Micros"):
                # Convert microseconds since Unix Epoch to datetime object.
                dimension_value_formatted = datetime.utcfromtimestamp(
                    int(dimension_value.value) / 1000000
                )
            else:
                dimension_value_formatted = dimension_value.value
            #print(f"{dimension_name}: {dimension_value_formatted}")
            dims[dimension_name]= dimension_value_formatted 
            

        for i, metric_value in enumerate(row.metric_values):
            metric_name = response.metric_headers[i].metric_name
            #print(f"{metric_name}: {metric_value.value}")
            dims[metric_name] =  metric_value.value
        access_list.append(dims)
    df = pd.DataFrame(access_list)
    return df

df = print_access_report(access_records)

print(df)