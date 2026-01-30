
## Chapter 5: DATA REPLICATION

This project demonstrates a robust, scalable Change Data Capture (CDC) architecture that replicates data from a MySQL database to multiple PostgreSQL replicas in real-time using Apache Kafka and Kafka Connect.

### Architecture Overview

The pipeline leverages Debezium and Kafka Connect to capture row-level changes (INSERT, UPDATE, DELETE) from MySQL's binary logs and stream them to Kafka topics. Independent JDBC Sink connectors then consume these changes and apply them to multiple target PostgreSQL instances.

```mermaid
graph TD
    subgraph source ["Source Layer"]
        MySQL[("MySQL Database")]
    end

    subgraph stream ["Streaming & Integration Layer"]
        KafkaConnect["Kafka Connect"]
        Debezium["Debezium Connector"]
        SchemaRegistry["Schema Registry"]
        Kafka["Kafka Broker"]
        
        MySQL -->|Captures binlog| Debezium
        Debezium --> KafkaConnect
        KafkaConnect --> SchemaRegistry
        KafkaConnect --> Kafka
    end

    subgraph target ["Target Layer (Replicas)"]
        Sink1["Replica 1 Sink"]
        Sink2["Replica 2 Sink"]
        Postgres1[("Postgres Replica 1")]
        Postgres2[("Postgres Replica 2")]
        
        Kafka --> Sink1
        Kafka --> Sink2
        Sink1 --> Postgres1
        Sink2 --> Postgres2
    end

    subgraph mon ["Monitoring"]
        KafkaUI["Kafka UI"]
        KafkaUI -.-> Kafka
        KafkaUI -.-> KafkaConnect
    end

    classDef database fill:#336791,stroke:#fff,stroke-width:2px,color:#fff
    classDef kafka fill:#231f20,stroke:#fff,stroke-width:2px,color:#fff
    classDef tools fill:#f1f1f1,stroke:#333,stroke-width:2px
    
    class MySQL,Postgres1,Postgres2 database
    class Kafka,SchemaRegistry kafka
    class KafkaConnect,Debezium,Sink1,Sink2,KafkaUI tools
```

### Key Features
- **Real-Time Replication**: Low-latency data synchronization using log-based CDC.
- **Multi-Replica Support**: Scalable architecture supporting multiple independent sink targets.
- **Schema Evolution**: Avro serialization with Confluent Schema Registry ensures robust data types and schema versioning.
- **Fault-Tolerant**: Kafka provides a durable buffer between the source and target systems.

### Technologies Used
- **Database**: MySQL 8.0, PostgreSQL 15
- **Message Broker**: Apache Kafka (KRaft mode)
- **Data Integration**: Kafka Connect, Debezium, Confluent JDBC Sink
- **Serialization**: Avro
- **Monitoring**: Kafka-UI
- **Orchestration**: Docker Compose
