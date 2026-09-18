ARG AIRFLOW_VERSION="3.3.2"

FROM apache/airflow:slim-${AIRFLOW_VERSION}

CMD ["bash"]
