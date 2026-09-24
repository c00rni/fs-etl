# DOcker for airflow
ARG AIRFLOW_VERSION="3.3.2-python3.12"

FROM apache/airflow:${AIRFLOW_VERSION}

USER root
COPY src/ /opt/airflow/plugins/src/
RUN chown -R airflow: /opt/airflow/plugins/src

USER airflow
ENV PYTHONPATH=/opt/airflow/plugins/src

# Install your Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
