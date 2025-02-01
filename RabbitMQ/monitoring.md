Once you're on Prometheus UI at http://localhost:9090, follow these steps to view the metrics:

🔹 Step 1: Check Available Metrics
Click on the "Status" tab in the top menu.
Select "Targets" (http://localhost:9090/targets).
Verify that node-exporter is listed and its state is "UP".
🔹 Step 2: Query Metrics
Go to the "Graph" tab.
In the query bar, enter one of the following metrics:
CPU Usage:
Copy
Edit
node_cpu_seconds_total
Memory Usage:
Copy
Edit
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
CPU Load Average (Last 1 min):
Copy
Edit
node_load1
Total Processes Running:
Copy
Edit
node_processes_running
Disk Usage:
Copy
Edit
node_filesystem_avail_bytes
Click "Execute" and then "Graph" to visualize the data.
🔹 Step 3: View Raw Metrics
If you want to see all raw metrics collected by Node Exporter, navigate to:
bash
Copy
Edit
http://localhost:9100/metrics
🔹 Next Steps
If you want better visualization, I recommend adding Grafana to your setup. Do you want help setting that up? 🚀


rate(container_cpu_usage_seconds_total{name="rabbitmq1"}[5m])
(rate(container_cpu_usage_seconds_total{name="rabbitmq1"}[5m]) * 100)
(rate(container_cpu_usage_seconds_total{name="rabbitmq1"}[5m]) * 100)
container_memory_usage_bytes{name="rabbitmq1"}
(container_memory_usage_bytes{name="rabbitmq1"} / container_spec_memory_limit_bytes{name="rabbitmq1"}) * 100

rate(container_cpu_usage_seconds_total{container_label_com_docker_compose_service="rabbitmq1"}[5m])
container_memory_usage_bytes{container_label_com_docker_compose_service="rabbitmq1"}
