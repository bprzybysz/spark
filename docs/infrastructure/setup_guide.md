# Infrastructure Setup Guide

## Overview
This guide provides detailed instructions for setting up and maintaining the infrastructure required for the ETL and ML pipeline system.

## Components

### 1. Apache Spark Cluster

#### Requirements
- Apache Spark 3.x
- Java 11+
- Python 3.11+
- 16GB+ RAM per node
- 4+ CPU cores per node

#### Setup Steps
1. **Install Java**
   ```bash
   brew install openjdk@11
   echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 11)' >> ~/.zshrc
   ```

2. **Install Spark**
   ```bash
   brew install apache-spark
   echo 'export SPARK_HOME=/usr/local/opt/apache-spark/libexec' >> ~/.zshrc
   ```

3. **Configure Spark**
   ```bash
   # spark-defaults.conf
   spark.driver.memory 8g
   spark.executor.memory 16g
   spark.executor.cores 4
   spark.dynamicAllocation.enabled true
   ```

### 2. Delta Lake Integration

#### Setup
1. **Add Delta Lake Dependencies**
   ```xml
   <dependency>
     <groupId>io.delta</groupId>
     <artifactId>delta-core_2.12</artifactId>
     <version>2.4.0</version>
   </dependency>
   ```

2. **Configure Spark with Delta**
   ```python
   spark = SparkSession.builder \
       .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
       .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
       .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
       .getOrCreate()
   ```

### 3. Apache Kafka Setup

#### Requirements
- Kafka 3.x
- ZooKeeper
- 8GB+ RAM
- Fast storage for logs

#### Installation
```bash
# Install Kafka
brew install kafka

# Start ZooKeeper
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# Start Kafka
kafka-server-start /usr/local/etc/kafka/server.properties
```

#### Configuration
```properties
# server.properties
broker.id=1
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs=/usr/local/var/lib/kafka-logs
num.partitions=3
num.recovery.threads.per.data.dir=1
```

### 4. Monitoring Setup

#### Prometheus Installation
```bash
brew install prometheus

# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'spark'
    static_configs:
      - targets: ['localhost:9090']
```

#### Grafana Setup
```bash
brew install grafana

# Start Grafana
brew services start grafana
```

### 5. Security Configuration

#### SSL Setup
1. Generate certificates
   ```bash
   openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out certificate.crt
   ```

2. Configure SSL
   ```properties
   # server.properties
   ssl.keystore.location=/path/to/keystore
   ssl.keystore.password=password
   ssl.key.password=password
   ```

#### Authentication
1. Set up LDAP
   ```yaml
   ldap:
     url: "ldap://localhost:389"
     base: "dc=example,dc=com"
     user_dn: "cn=admin,dc=example,dc=com"
     password: "admin_password"
   ```

### 6. Backup and Recovery

#### Backup Configuration
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/path/to/backups/$DATE"

# Backup Spark configs
cp $SPARK_HOME/conf/* $BACKUP_DIR/spark/
# Backup Kafka data
kafka-backup.sh --source-dir /var/lib/kafka --target-dir $BACKUP_DIR/kafka
```

#### Recovery Procedures
1. Stop services
2. Restore from backup
3. Verify data integrity
4. Restart services

## Deployment

### Development Environment
```bash
# Clone repository
git clone https://github.com/your-org/etl-pipeline.git

# Install dependencies
poetry install

# Set up pre-commit hooks
pre-commit install
```

### Production Environment
1. **Resource Requirements**
   - 32GB+ RAM
   - 8+ CPU cores
   - 1TB+ storage
   - 10Gbps network

2. **Deployment Steps**
   ```bash
   # Build containers
   docker-compose build
   
   # Deploy services
   docker-compose up -d
   ```

## Monitoring and Maintenance

### Health Checks
```bash
# Check Spark cluster
spark-submit --class org.apache.spark.deploy.Client \
  --master spark://master:7077 \
  --total-executor-cores 1 \
  health-check.jar

# Check Kafka
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Log Management
```bash
# Configure log rotation
cat > /etc/logrotate.d/spark << EOF
/var/log/spark/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

## Troubleshooting

### Common Issues

1. **Spark Executor Memory Issues**
   ```bash
   # Check memory usage
   jmap -heap <executor-pid>
   
   # Adjust memory settings
   --conf spark.executor.memory=16g
   --conf spark.memory.fraction=0.8
   ```

2. **Kafka Connection Issues**
   ```bash
   # Check connectivity
   nc -zv localhost 9092
   
   # Check broker status
   kafka-broker-api-versions.sh --bootstrap-server localhost:9092
   ```

## Security Best Practices

1. **Network Security**
   - Use private networks
   - Implement firewalls
   - Enable SSL/TLS
   - Regular security audits

2. **Access Control**
   - Role-based access
   - Regular credential rotation
   - Audit logging
   - Multi-factor authentication

## Scaling Guidelines

1. **Horizontal Scaling**
   - Add more nodes to Spark cluster
   - Increase Kafka partitions
   - Balance data distribution

2. **Vertical Scaling**
   - Increase memory
   - Add CPU cores
   - Optimize storage

## Future Improvements
1. Implement auto-scaling
2. Add disaster recovery site
3. Enhance monitoring coverage
4. Implement blue-green deployments
5. Add performance optimization tools 