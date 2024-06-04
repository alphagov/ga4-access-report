from google.analytics.admin import AnalyticsAdminServiceClient
import pandas as pd
from datetime import datetime
from google.auth import default
import functions_framework
import os
import re
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly', 'https://www.googleapis.com/auth/bigquery']
PROJECT = os.getenv('GCP_PROJECT_ID')
creds, _ = default(scopes=SCOPES, default_scopes=SCOPES, quota_project_id=PROJECT)
GA4_ENTITY = os.getenv('GA4_ENTITY')


def get_access_report(n):
    client = AnalyticsAdminServiceClient(credentials=creds)
    access_dict = {
      "entity": GA4_ENTITY,
      "limit": 100000,
      "date_ranges": [
        {
          "start_date": f"{n}daysAgo",
          "end_date": f"{n}daysAgo"
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
    return access_records


def format_access_report(response):
    access_list = []

    for rowIdx, row in enumerate(response.rows):
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
            dims[dimension_name] = dimension_value_formatted

        for i, metric_value in enumerate(row.metric_values):
            metric_name = response.metric_headers[i].metric_name
            dims[metric_name] = metric_value.value
        access_list.append(dims)

    df = pd.DataFrame(access_list)
    df = df.rename(columns={
      'epochTimeMicros': 'epoch_time_micros',
      'userEmail': 'user_email',
      'accessMechanism': 'access_mechanism',
      'accessorAppName': 'accessor_app_name',
      'dataApiQuotaCategory': 'api_quota_category',
      'reportType': 'report_type',
      'accessCount': 'access_count',
      'dataApiQuotaPropertyTokensConsumed': 'api_tokens_consumed'})
    return df


def send_to_bq(df):
    df['access_count'] = pd.to_numeric(df['access_count'])
    df['api_tokens_consumed'] = pd.to_numeric(df['api_tokens_consumed'])
    df['domain'] = df['user_email'].apply(lambda x: re.search(r'@.*$', str(x)).group())
    ts = df['epoch_time_micros'].max()
    table = ts.strftime('%Y%m%d')

    df.to_gbq(
        f'ga4_logs.ga4_logs_{table}',
        project_id=PROJECT,
        chunksize=None,
        reauth=False,
        if_exists='fail',
        auth_local_webserver=True,
        table_schema=None,
        location=None,
        progress_bar=True,
        credentials=creds
        )


@functions_framework.http
def run(request, n=1):
    access_records = get_access_report(n)
    df = format_access_report(access_records)
    try:
        send_to_bq(df)
        return "all good"
    except Exception as e:
        print(df.head(n=5))
        print(e)
        return "all bad"


if __name__ == '__main__':
    run(request='', n=1)
