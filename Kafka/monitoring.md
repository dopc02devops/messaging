Access Grafana:

After running docker-compose up, you can access Grafana at http://localhost:3000.
Default login: admin / admin (you can change the password in the environment variable).
Add Prometheus as Data Source:

In Grafana, add Prometheus as the data source:
URL: http://prometheus:9090

