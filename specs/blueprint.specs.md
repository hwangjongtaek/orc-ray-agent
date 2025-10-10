# Ray 기반 분산 플러그인 에이전트 시스템 최종 설계안

## 1. 개요

### 1.1. 문서 목적

본 문서는 FastAPI와 Ray를 활용한 분산 머신러닝 플러그인 에이전트 시스템의 최종 아키텍처, 구성 요소별 상세 설계, API 명세, 데이터 모델, 배포 및 운영 방안을 정의하는 것을 목적으로 한다. 본 설계안은 프로젝트 참여자들이 일관된 이해를 바탕으로 개발을 진행하기 위한 최종 가이드라인이다.

### 1.2. 시스템 요약

본 시스템은 외부의 작업 요청을 받아, 사전 등록된 플러그인(컨테이너화된 ML 모델 또는 데이터 처리 로직)을 Ray 분산 컴퓨팅 클러스터에서 동적으로 실행하고 그 결과를 반환하는 MLOps 플랫폼이다. 관리자는 웹 기반 대시보드를 통해 시스템의 모든 자원(사용자, 플러그인, 작업)을 실시간으로 모니터링하고 관리할 수 있다.

## 2. 시스템 아키텍처

### 2.1. 전체 아키텍처

| 컴포넌트             | 역할                                                | 기술 스택                  |
| -------------------- | --------------------------------------------------- | -------------------------- |
| **API Agent**        | REST API 서버, 관리자 대시보드 웹 서버              | FastAPI, Jinja2, Alpine.js |
| **Plugin Registry**  | 플러그인 메타데이터 관리 및 등록/조회 API           | FastAPI, PostgreSQL        |
| **Database**         | 사용자, 작업, 플러그인 정보 영구 저장               | PostgreSQL                 |
| **Message Queue**    | API Agent와 Ray Cluster 간 작업 전달 및 상태 동기화 | RabbitMQ                   |
| **Ray Cluster**      | 분산 작업 실행 환경 (Head, Worker 노드로 구성)      | Ray                        |
| **Plugin Container** | 실제 로직을 수행하는 독립된 컨테이너 환경           | Docker                     |

### 2.2. 작업 처리 흐름 (Job Processing Flow)

1. **사용자**는 `API Agent`에 REST API를 통해 특정 플러그인 실행을 요청한다 (Job 생성).
2. `API Agent`는 요청을 검증하고, Job 정보를 **Database**에 `queued` 상태로 저장한다.
3. `API Agent`는 Job 정보를 **Message Queue**(`job_queue`)에 전송한다.
4. **Ray Cluster**의 `Ray Worker`는 `job_queue`를 구독(subscribe)하다가 새로운 Job을 수신한다.
5. `Ray Worker`는 Job에 명시된 플러그인 정보를 바탕으로 `Plugin Registry`에서 Docker 이미지 위치 등 상세 정보를 조회한다.
6. `Ray Worker`는 해당 **Plugin Container**를 실행하고, Ray Actor(`PluginExecutorActor`)를 통해 작업을 처리한다.
7. 작업 처리 중 상태 변경(e.g., `processing`, `completed`, `failed`)이 발생하면, Actor는 **Message Queue**(`status_queue`)에 상태를 전송한다.
8. `API Agent`는 `status_queue`를 구독하다가 상태 변경 메시지를 수신하여 **Database**의 Job 상태를 업데이트한다.
9. **사용자**는 API를 통해 Job의 최종 상태와 결과를 조회한다.

## 3. 기술 스택

- **Backend**: Python 3.13, FastAPI, Pydantic, SQLAlchemy
- **Database**: PostgreSQL 17
- **Message Broker**: RabbitMQ 3.13 (Latest LTS)
- **Distributed Computing**: Ray
- **Frontend (Dashboard)**: Jinja2, Tailwind CSS (CDN), Alpine.js (CDN)
- **Containerization**: Docker
- **Orchestration (Dev)**: Docker Compose

## 4. 프로젝트 디렉토리 구조

프로젝트는 다음과 같은 주요 컴포넌트로 구성됩니다:

- **api-agent/** - REST API 서버 및 관리자 대시보드 (Port 5900)
- **plugin-registry/** - 플러그인 메타데이터 관리 서비스 (Port 5901)
- **ray-worker/** - 분산 작업 실행 엔진 (Ray + Docker)
- **plugins/** - 예제 플러그인 구현 (classifier, processor)
- **specs/** - 시스템 문서
- **Makefile, docker-compose.yml** - 개발 자동화 도구

**자세한 디렉토리 구조 및 파일 설명은 [structure.specs.md](structure.specs.md)를 참조하십시오.**

### 4.1. 주요 컴포넌트 요약

| 컴포넌트 | 경로 | 용도 | 포트 |
|----------|------|------|------|
| API Agent | `api-agent/` | REST API, JWT 인증, Job 관리, 대시보드 | 5900 |
| Plugin Registry | `plugin-registry/` | 플러그인 메타데이터 CRUD | 5901 |
| Ray Worker | `ray-worker/` | Docker 기반 플러그인 실행 | - |
| Example Plugins | `plugins/` | 참조 구현 (classifier, processor) | - |
| Documentation | `specs/`, `*.md` | 시스템 문서 | - |

## 5. 데이터베이스 스키마 (SQLAlchemy Models)

`api-agent/app/models/` 경로에 정의될 모델.

### 5.1. `user.py`

```
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    jobs = relationship("Job", back_populates="owner")

```

### 5.2. `plugin.py`

```
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class Plugin(Base):
    __tablename__ = "plugins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    description = Column(String)
    docker_image_url = Column(String, nullable=False)
    input_schema = Column(JSON) # 입력 데이터 검증을 위한 JSON Schema
    output_schema = Column(JSON) # 출력 데이터 검증을 위한 JSON Schema
    created_at = Column(DateTime(timezone=True), server_default=func.now())

```

### 5.3. `job.py`

```
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    plugin_name = Column(String, index=True, nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    input_data = Column(JSON)
    result = Column(JSON)
    error_message = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    owner = relationship("User", back_populates="jobs")

```

## 6. 플러그인 개발 가이드

### 6.1. 플러그인 인터페이스 규약

모든 플러그인은 다음 규약을 준수해야 한다:

1. **입력**: JSON 형식의 데이터를 표준 입력(STDIN) 또는 명령행 인자로 수신
2. **출력**: JSON 형식의 결과를 표준 출력(STDOUT)으로 반환
3. **에러**: 에러 발생 시 0이 아닌 exit code 반환, 에러 메시지는 STDERR로 출력
4. **타임아웃**: 장시간 실행되는 작업의 경우 주기적인 상태 업데이트 권장

### 6.2. 플러그인 메타데이터 (plugin.json)

```json
{
  "name": "example-classifier",
  "version": "1.0.0",
  "description": "Example ML classifier plugin",
  "docker_image": "registry.example.com/example-classifier:1.0.0",
  "input_schema": {
    "type": "object",
    "properties": {
      "features": {
        "type": "array",
        "items": { "type": "number" }
      },
      "model_params": {
        "type": "object"
      }
    },
    "required": ["features"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "prediction": { "type": "string" },
      "confidence": { "type": "number" },
      "metadata": { "type": "object" }
    },
    "required": ["prediction"]
  }
}
```

### 6.3. 플러그인 구현 예제

**main.py**:

```python
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process(input_data):
    """
    플러그인의 핵심 로직
    """
    try:
        features = input_data.get('features', [])
        model_params = input_data.get('model_params', {})

        # 실제 ML 모델 추론 로직
        prediction = perform_inference(features, model_params)

        return {
            "prediction": prediction,
            "confidence": 0.95,
            "metadata": {
                "model_version": "1.0.0",
                "features_count": len(features)
            }
        }
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

def perform_inference(features, params):
    # 실제 추론 로직 구현
    return "class_A"

if __name__ == "__main__":
    try:
        # 입력 데이터 읽기
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        else:
            input_data = json.load(sys.stdin)

        # 처리
        result = process(input_data)

        # 결과 출력
        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
```

**Dockerfile**:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY plugin.json .

# 플러그인 실행
ENTRYPOINT ["python", "main.py"]
```

**requirements.txt**:

```
numpy==1.24.0
scikit-learn==1.2.0
```

### 6.4. 플러그인 등록 절차

1. 플러그인 Docker 이미지 빌드:

   ```bash
   docker build -t example-classifier:1.0.0 .
   ```

2. 이미지를 컨테이너 레지스트리에 푸시:

   ```bash
   docker tag example-classifier:1.0.0 registry.example.com/example-classifier:1.0.0
   docker push registry.example.com/example-classifier:1.0.0
   ```

3. Plugin Registry API를 통해 등록:
   ```bash
   curl -X POST http://api-agent:5900/api/v1/plugins \
     -H "Content-Type: application/json" \
     -d @plugin.json
   ```

## 7. API 명세 (REST API Specification)

Base URL: `/api/v1`

### 7.1. Authentication

#### `POST /auth/token`

이메일, 패스워드로 로그인 후 JWT 토큰 발급.

**Request Body**:

```json
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses**:

- `401 Unauthorized`: 잘못된 자격 증명
- `400 Bad Request`: 유효하지 않은 요청 형식

#### `GET /users/me`

현재 로그인된 사용자 정보 조회.

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 7.2. Users

#### `POST /users`

신규 사용자 생성.

**Request Body**:

```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "full_name": "Jane Doe"
}
```

**Response (201 Created)**:

```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2024-01-02T00:00:00Z"
}
```

**Error Responses**:

- `400 Bad Request`: 이메일 형식 오류 또는 약한 비밀번호
- `409 Conflict`: 이미 존재하는 이메일

### 7.3. Plugins

`plugin-registry` 서비스가 제공하는 API.

#### `POST /plugins`

신규 플러그인 등록.

**Request Body**:

```json
{
  "name": "example-classifier",
  "version": "1.0.0",
  "description": "Example ML classifier plugin",
  "docker_image_url": "registry.example.com/example-classifier:1.0.0",
  "input_schema": {
    "type": "object",
    "properties": {
      "features": { "type": "array" }
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "prediction": { "type": "string" }
    }
  }
}
```

**Response (201 Created)**:

```json
{
  "id": 1,
  "name": "example-classifier",
  "version": "1.0.0",
  "description": "Example ML classifier plugin",
  "docker_image_url": "registry.example.com/example-classifier:1.0.0",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `GET /plugins`

등록된 모든 플러그인 목록 조회.

**Query Parameters**:

- `skip` (int, optional): 건너뛸 레코드 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 레코드 수 (기본값: 100)
- `name` (string, optional): 이름으로 필터링

**Response (200 OK)**:

```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "name": "example-classifier",
      "version": "1.0.0",
      "description": "Example ML classifier plugin",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### `GET /plugins/{name}`

특정 이름의 플러그인 상세 정보 조회.

**Response (200 OK)**:

```json
{
  "id": 1,
  "name": "example-classifier",
  "version": "1.0.0",
  "description": "Example ML classifier plugin",
  "docker_image_url": "registry.example.com/example-classifier:1.0.0",
  "input_schema": {...},
  "output_schema": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses**:

- `404 Not Found`: 플러그인을 찾을 수 없음

#### `DELETE /plugins/{name}`

플러그인 삭제.

**Response (204 No Content)**

### 7.4. Jobs

#### `POST /jobs`

신규 작업 생성. (인증 필요)

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "plugin_name": "example-classifier",
  "input_data": {
    "features": [1.0, 2.0, 3.0, 4.0],
    "model_params": {
      "threshold": 0.5
    }
  }
}
```

**Response (202 Accepted)**:

```json
{
  "id": 123,
  "plugin_name": "example-classifier",
  "status": "queued",
  "input_data": {...},
  "result": null,
  "error_message": null,
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

**Error Responses**:

- `400 Bad Request`: 입력 데이터가 플러그인 스키마와 맞지 않음
- `404 Not Found`: 지정된 플러그인을 찾을 수 없음
- `401 Unauthorized`: 인증 토큰 누락 또는 만료

#### `GET /jobs`

현재 사용자의 모든 작업 목록 조회. (인증 필요)

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:

- `skip` (int, optional): 건너뛸 레코드 수 (기본값: 0)
- `limit` (int, optional): 조회할 최대 레코드 수 (기본값: 50)
- `status` (string, optional): 상태로 필터링 (queued, processing, completed, failed)
- `plugin_name` (string, optional): 플러그인 이름으로 필터링

**Response (200 OK)**:

```json
{
  "total": 25,
  "items": [
    {
      "id": 123,
      "plugin_name": "example-classifier",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:00:10Z"
    }
  ]
}
```

#### `GET /jobs/{job_id}`

특정 작업의 상세 상태 및 결과 조회. (인증 필요)

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:

```json
{
  "id": 123,
  "plugin_name": "example-classifier",
  "status": "completed",
  "input_data": {
    "features": [1.0, 2.0, 3.0, 4.0]
  },
  "result": {
    "prediction": "class_A",
    "confidence": 0.95
  },
  "error_message": null,
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": "2024-01-01T00:00:01Z",
  "completed_at": "2024-01-01T00:00:10Z"
}
```

**Error Responses**:

- `404 Not Found`: 작업을 찾을 수 없음
- `403 Forbidden`: 다른 사용자의 작업에 대한 접근 시도

## 8. 메시지 큐 상세

### 8.1. 큐 구성

시스템은 두 개의 주요 큐를 사용한다:

1. **job_queue**: API Agent → Ray Worker로 작업 전달
2. **status_queue**: Ray Worker → API Agent로 상태 업데이트 전달

### 8.2. 메시지 스키마

#### job_queue 메시지 형식

```json
{
  "job_id": 123,
  "plugin_name": "example-classifier",
  "docker_image_url": "registry.example.com/example-classifier:1.0.0",
  "input_data": {
    "features": [1.0, 2.0, 3.0, 4.0]
  },
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### status_queue 메시지 형식

```json
{
  "job_id": 123,
  "status": "completed",
  "result": {
    "prediction": "class_A",
    "confidence": 0.95
  },
  "error_message": null,
  "updated_at": "2024-01-01T00:00:10Z"
}
```

### 8.3. 큐 설정

**RabbitMQ 큐 설정**:

```python
# job_queue 설정
channel.queue_declare(
    queue='job_queue',
    durable=True,              # 서버 재시작 시 큐 유지
    arguments={
        'x-message-ttl': 3600000,  # 메시지 TTL: 1시간
        'x-max-length': 10000,      # 최대 메시지 수
        'x-dead-letter-exchange': 'dlx_exchange'  # DLX 설정
    }
)

# status_queue 설정
channel.queue_declare(
    queue='status_queue',
    durable=True,
    arguments={
        'x-message-ttl': 1800000,  # 메시지 TTL: 30분
    }
)
```

### 8.4. 재시도 및 Dead Letter Exchange

**Dead Letter Exchange 설정**:

```python
# DLX 및 DLQ 설정
channel.exchange_declare(
    exchange='dlx_exchange',
    exchange_type='direct',
    durable=True
)

channel.queue_declare(
    queue='dead_letter_queue',
    durable=True
)

channel.queue_bind(
    queue='dead_letter_queue',
    exchange='dlx_exchange',
    routing_key='job_queue'
)
```

**재시도 로직**:

- 최대 3회 재시도
- 재시도 간격: 지수 백오프 (1초, 2초, 4초)
- 3회 실패 후 DLQ로 이동

## 9. Ray Actor 및 워크플로우

### 9.1. `PluginExecutorActor` 정의

Ray 클러스터에서 실제 플러그인 컨테이너를 실행하고 통신하는 역할을 수행하는 Actor.

```
# ray_worker/actors.py
import ray
import docker
from pika.adapters.blocking_connection import BlockingChannel

@ray.remote
class PluginExecutorActor:
    def __init__(self, amqp_channel: BlockingChannel):
        self.docker_client = docker.from_env()
        self.amqp_channel = amqp_channel

    def execute_plugin(self, job_id: int, image_url: str, input_data: dict) -> None:
        # 1. 상태를 'processing'으로 업데이트하여 status_queue에 전송
        self._update_status(job_id, "processing")

        try:
            # 2. Docker 컨테이너 실행
            # 컨테이너에 input_data를 환경변수나 STDIN으로 전달
            container = self.docker_client.containers.run(
                image_url,
                command=f"python main.py '{json.dumps(input_data)}'",
                detach=True
            )
            result = container.wait()
            logs = container.logs().decode("utf-8")
            container.remove()

            if result['StatusCode'] == 0:
                # 3. 성공 시 'completed' 상태와 결과 전송
                output = json.loads(logs) # 컨테이너는 결과를 STDOUT으로 출력
                self._update_status(job_id, "completed", result=output)
            else:
                # 4. 실패 시 'failed' 상태와 에러 메시지 전송
                self._update_status(job_id, "failed", error_message=logs)

        except Exception as e:
            self._update_status(job_id, "failed", error_message=str(e))

    def _update_status(self, job_id, status, result=None, error_message=None):
        message = {"job_id": job_id, "status": status, "result": result, "error_message": error_message}
        self.amqp_channel.basic_publish(
            exchange='',
            routing_key='status_queue',
            body=json.dumps(message)
        )

```

## 10. 확장성 및 성능 고려사항

### 10.1. Ray 클러스터 스케일링

#### 수평 확장 (Horizontal Scaling)

**Worker 노드 동적 추가**:

```bash
# 새로운 Worker 노드 시작
ray start --address=<head-node-ip>:6379 --num-cpus=8 --num-gpus=1
```

**Auto-scaling 설정** (Kubernetes 환경):

```yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: orc-ray-cluster
spec:
  rayVersion: "2.5.0"
  headGroupSpec:
    replicas: 1
    rayStartParams:
      dashboard-host: "0.0.0.0"
  workerGroupSpecs:
    - groupName: worker-group
      replicas: 3
      minReplicas: 1
      maxReplicas: 10
      rayStartParams:
        num-cpus: "4"
```

#### 수직 확장 (Vertical Scaling)

- **CPU/Memory 리소스 할당**: 컨테이너별 리소스 제한 설정
- **GPU 리소스**: ML 추론 작업에 GPU 할당
- **Actor 리소스 요구사항**:

```python
@ray.remote(num_cpus=2, num_gpus=0.5, memory=4*1024*1024*1024)
class PluginExecutorActor:
    pass
```

### 10.2. 데이터베이스 최적화

#### 연결 풀링

```python
# SQLAlchemy 연결 풀 설정
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # 기본 연결 수
    max_overflow=10,       # 추가 연결 수
    pool_timeout=30,       # 연결 대기 시간
    pool_recycle=3600,     # 연결 재활용 시간
    pool_pre_ping=True     # 연결 상태 확인
)
```

#### 인덱스 최적화

```sql
-- Job 조회 성능 향상을 위한 복합 인덱스
CREATE INDEX idx_jobs_owner_status ON jobs(owner_id, status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_plugin_status ON jobs(plugin_name, status);

-- Plugin 조회 성능 향상
CREATE INDEX idx_plugins_name_version ON plugins(name, version);
```

#### 쿼리 최적화

- **Eager Loading**: N+1 쿼리 문제 방지

```python
# 좋은 예
jobs = db.query(Job).options(joinedload(Job.owner)).all()

# 나쁜 예
jobs = db.query(Job).all()
for job in jobs:
    owner = job.owner  # N+1 쿼리 발생
```

- **Pagination**: 대량 데이터 조회 시 페이지네이션 사용

### 10.3. 캐싱 전략

#### Redis 통합 (선택사항)

```python
import redis
from functools import lru_cache

# Redis 클라이언트
redis_client = redis.Redis(host='redis', port=6379, db=0)

# 플러그인 메타데이터 캐싱
def get_plugin_cached(name: str):
    cache_key = f"plugin:{name}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    plugin = db.query(Plugin).filter(Plugin.name == name).first()
    redis_client.setex(cache_key, 3600, json.dumps(plugin.dict()))
    return plugin
```

#### 메모리 캐싱

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_active_plugins():
    return db.query(Plugin).all()
```

### 10.4. 로드 밸런싱

#### API Agent 로드 밸런싱

**NGINX 설정**:

```nginx
upstream api_agents {
    least_conn;  # 최소 연결 수 기반 밸런싱
    server api-agent-1:5900 weight=1;
    server api-agent-2:5900 weight=1;
    server api-agent-3:5900 weight=1;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Ray Worker 부하 분산

- Ray는 자동으로 가용한 Worker 노드에 작업 분산
- `PluginExecutorActor` 인스턴스를 여러 개 생성하여 병렬 처리

### 10.5. 성능 모니터링 지표

- **API 응답 시간**: P50, P95, P99 latency 추적
- **Job 처리량**: 시간당 처리된 Job 수
- **Queue Depth**: job_queue의 대기 중인 메시지 수
- **Ray 클러스터 리소스 사용률**: CPU, Memory, GPU 사용률
- **데이터베이스 쿼리 시간**: 슬로우 쿼리 로그 분석

## 11. 관리자 대시보드

- **접근 경로**: `/dashboard`
- **기술 스택**: FastAPI(라우팅 및 데이터 제공), Jinja2(템플릿 렌더링), Alpine.js(클라이언트 인터랙션), Tailwind CSS(스타일링).
- **주요 페이지**:
  - `/dashboard/login`: 대시보드 관리자 로그인.
  - `/dashboard/overview`: 전체 Job 수, User 수, Plugin 수 등 요약 정보.
  - `/dashboard/jobs`: Job 목록 실시간 조회, 상태별 필터링, 상세 정보 모달.
  - `/dashboard/users`: 사용자 목록 조회, 활성/비활성 관리.
  - `/dashboard/plugins`: `plugin-registry`와 연동하여 등록된 플러그인 목록 조회.

## 12. 테스팅 전략

### 12.1. 단위 테스트 (Unit Testing)

#### API Agent 테스트

**pytest 기반 테스트**:

```python
# tests/test_jobs.py
import pytest
from app.services.job_service import JobService
from app.models.job import JobStatus

def test_create_job_success(db_session, test_user, test_plugin):
    """Job 생성 성공 시나리오 테스트"""
    service = JobService(db_session)

    job = service.create_job(
        plugin_name=test_plugin.name,
        input_data={"features": [1.0, 2.0]},
        owner_id=test_user.id
    )

    assert job.status == JobStatus.QUEUED
    assert job.plugin_name == test_plugin.name
    assert job.owner_id == test_user.id

def test_create_job_invalid_plugin(db_session, test_user):
    """존재하지 않는 플러그인으로 Job 생성 시도"""
    service = JobService(db_session)

    with pytest.raises(ValueError):
        service.create_job(
            plugin_name="nonexistent",
            input_data={},
            owner_id=test_user.id
        )
```

#### Ray Actor 테스트

```python
# tests/test_actors.py
import ray
from ray_worker.actors import PluginExecutorActor

def test_execute_plugin_success(mock_docker_client, mock_amqp_channel):
    """플러그인 실행 성공 테스트"""
    actor = PluginExecutorActor.remote(mock_amqp_channel)

    result = ray.get(actor.execute_plugin.remote(
        job_id=1,
        image_url="test-image:latest",
        input_data={"features": [1.0, 2.0]}
    ))

    assert result is not None
```

### 12.2. 통합 테스트 (Integration Testing)

#### API 엔드포인트 통합 테스트

```python
# tests/integration/test_job_flow.py
from fastapi.testclient import TestClient

def test_full_job_lifecycle(client: TestClient, auth_headers):
    """전체 Job 생명주기 통합 테스트"""

    # 1. Job 생성
    response = client.post(
        "/api/v1/jobs",
        headers=auth_headers,
        json={
            "plugin_name": "test-plugin",
            "input_data": {"features": [1.0, 2.0]}
        }
    )
    assert response.status_code == 202
    job_id = response.json()["id"]

    # 2. Job 상태 조회
    response = client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] in ["queued", "processing"]

    # 3. Job 목록 조회
    response = client.get("/api/v1/jobs", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0
```

### 12.3. 엔드투엔드 테스트 (E2E Testing)

```python
# tests/e2e/test_system_flow.py
import time
import pytest

@pytest.mark.e2e
def test_complete_workflow():
    """전체 시스템 워크플로우 E2E 테스트"""

    # 1. 플러그인 등록
    plugin = register_plugin({
        "name": "e2e-test-plugin",
        "version": "1.0.0",
        "docker_image_url": "test:latest"
    })

    # 2. Job 제출
    job = submit_job(plugin.name, {"test": "data"})

    # 3. Job 완료 대기
    timeout = 60
    start = time.time()
    while time.time() - start < timeout:
        job_status = get_job_status(job.id)
        if job_status["status"] in ["completed", "failed"]:
            break
        time.sleep(1)

    # 4. 결과 검증
    assert job_status["status"] == "completed"
    assert "result" in job_status
```

### 12.4. 성능 테스트

#### Locust를 사용한 부하 테스트

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # 로그인 및 토큰 획득
        response = self.client.post("/api/v1/auth/token", json={
            "username": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def create_job(self):
        self.client.post(
            "/api/v1/jobs",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "plugin_name": "test-plugin",
                "input_data": {"features": [1.0, 2.0]}
            }
        )

    @task(1)
    def list_jobs(self):
        self.client.get(
            "/api/v1/jobs",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

실행:

```bash
locust -f tests/performance/locustfile.py --host=http://localhost:5900
```

### 12.5. 테스트 커버리지 목표

- **단위 테스트**: 최소 80% 코드 커버리지
- **통합 테스트**: 주요 API 엔드포인트 100% 커버
- **E2E 테스트**: 핵심 비즈니스 시나리오 커버

```bash
# 커버리지 측정
pytest --cov=app --cov-report=html tests/
```

## 13. 배포 전략

### 8.1. 개발 환경 (Docker Compose)

`docker-compose.yml` 파일을 통해 모든 서비스를 한번에 실행.

```
version: '3.8'

services:
  postgres:
    image: postgres:17
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=plugindb
    ports:
      - "5432:5432"

  rabbitmq:
    image: rabbitmq:3.13-management
    ports:
      - "5672:5672" # AMQP
      - "15672:15672" # Management UI

  api-agent:
    build: ./api-agent
    ports:
      - "5900:8000"
    depends_on:
      - postgres
      - rabbitmq
    environment:
      - DATABASE_URL=postgresql://user:password@postgres/plugindb
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq/

  plugin-registry:
    # api-agent와 유사한 구조로 별도 구현
    build: ./plugin-registry
    ports:
      - "5901:8000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://user:password@postgres/plugindb

  ray-head:
    image: rayproject/ray:latest
    ports:
      - "10001:10001" # Ray client
      - "8265:8265" # Ray dashboard
    command: ray start --head --dashboard-host 0.0.0.0

  ray-worker:
    image: rayproject/ray:latest
    depends_on:
      - ray-head
      - rabbitmq
    command: ray start --address=ray-head:6379
    # Worker가 Docker를 사용하기 위해 Docker 소켓 마운트 필요
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

### 13.2. 프로덕션 환경 고려사항

- **Orchestration**: Docker Swarm 또는 Kubernetes(K8s)를 사용하여 컨테이너 관리.
- **Database/MQ**: AWS RDS, RabbitMQ on AWS와 같은 Managed Service 사용 권장.
- **Ray Cluster**: KubeRay Operator를 사용하여 K8s 위에 Ray 클러스터를 효율적으로 배포 및 확장.
- **CI/CD**: GitHub Actions, Jenkins 등을 통해 테스트 및 배포 자동화 파이프라인 구축.

## 14. 시스템 운영

### 14.1. 로깅 및 모니터링

- **로깅**: 모든 서비스는 표준 출력(stdout)으로 JSON 형식의 로그를 남기고, Filebeat, Fluentd 등을 통해 중앙 로그 저장소(Elasticsearch)로 수집.
- **모니터링**: Prometheus로 각 서비스의 메트릭(API 응답 시간, Job 처리량, Ray 클러스터 상태 등)을 수집하고, Grafana를 통해 시각화 대시보드 구축. Ray는 자체 대시보드(`:8265`)도 제공.

### 14.2. 에러 처리 및 복구성

- **API Agent**: Pydantic을 사용한 입력값 검증, FastAPI의 Exception Handler를 통한 일관된 에러 응답 처리.
- **Message Queue**: RabbitMQ의 `Dead Letter Exchange`를 활용하여 처리 실패한 메시지를 별도 큐로 옮겨 추후 분석 및 재처리.
- **Ray Actor**: Actor 내부에서 `try-except` 구문을 통해 예외를 처리하고, 실패 상태를 `status_queue`에 명확히 전달. Ray의 Actor 재시작 정책 활용.

### 14.3. 보안

#### 인증 및 인가

- **JWT 토큰 기반 인증**:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

- **역할 기반 접근 제어 (RBAC)**:

```python
from enum import Enum
from fastapi import Depends, HTTPException

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# 사용 예
@app.delete("/api/v1/plugins/{name}")
async def delete_plugin(
    name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    pass
```

#### API Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/jobs")
@limiter.limit("10/minute")  # 분당 10개 요청 제한
async def create_job(request: Request, ...):
    pass
```

#### 입력 검증 및 Sanitization

```python
from pydantic import BaseModel, validator, constr
import bleach

class JobCreate(BaseModel):
    plugin_name: constr(min_length=1, max_length=100, regex=r'^[a-z0-9-]+$')
    input_data: dict

    @validator('input_data')
    def sanitize_input(cls, v):
        # JSON 입력값 크기 제한
        if len(json.dumps(v)) > 1024 * 1024:  # 1MB
            raise ValueError("Input data too large")
        return v
```

#### 컨테이너 보안

**Docker 보안 설정**:

```dockerfile
# 비 root 사용자로 실행
FROM python:3.13-slim

RUN useradd -m -u 1000 appuser
USER appuser

# 읽기 전용 파일시스템
VOLUME ["/tmp"]
```

**Kubernetes Security Context**:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

#### 의존성 취약점 관리

```bash
# Python 패키지 취약점 스캔
pip install safety
safety check

# Docker 이미지 취약점 스캔
trivy image api-agent:latest
```

#### 네트워크 보안

- **Docker 네트워크 분리**:

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true # 외부 접근 차단
```

- **K8s Network Policy**:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-agent-policy
spec:
  podSelector:
    matchLabels:
      app: api-agent
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx
      ports:
        - protocol: TCP
          port: 5900
```

#### 민감 정보 관리

**환경 변수를 통한 주입** (개발 환경):

```bash
export DATABASE_URL="postgresql://user:password@localhost/db"
export SECRET_KEY="your-secret-key"
export RABBITMQ_URL="amqp://guest:guest@localhost/"
```

**Kubernetes Secrets** (프로덕션):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: <base64-encoded-value>
  secret-key: <base64-encoded-value>
```

**HashiCorp Vault 통합**:

```python
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.getenv('VAULT_TOKEN')

secret = client.secrets.kv.v2.read_secret_version(
    path='orc-ray-agent/prod'
)
database_url = secret['data']['data']['database_url']
```

## 15. 재해 복구 및 백업

### 15.1. 데이터베이스 백업

#### 자동화된 백업

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# PostgreSQL 백업
pg_dump -h postgres -U user plugindb | gzip > $BACKUP_FILE

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# S3에 업로드 (선택사항)
aws s3 cp $BACKUP_FILE s3://backup-bucket/postgres/
```

**cron 설정**:

```
0 2 * * * /scripts/backup_db.sh
```

#### 복구 절차

```bash
# 백업에서 복구
gunzip -c backup_20240101_020000.sql.gz | psql -h postgres -U user plugindb

# 특정 시점 복구 (Point-in-Time Recovery)
# PostgreSQL의 WAL (Write-Ahead Logging) 활용
```

### 15.2. 메시지 큐 영속성

**RabbitMQ 메시지 영속성 설정**:

```python
# Durable 큐 선언
channel.queue_declare(queue='job_queue', durable=True)

# Persistent 메시지 전송
channel.basic_publish(
    exchange='',
    routing_key='job_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # 메시지를 디스크에 영속화
    )
)
```

**RabbitMQ 데이터 백업**:

```bash
# RabbitMQ 정의 및 메시지 내보내기
rabbitmqctl export_definitions /backups/rabbitmq_definitions.json

# 복구
rabbitmqctl import_definitions /backups/rabbitmq_definitions.json
```

### 15.3. Plugin Registry 백업

```bash
# Docker Registry 데이터 백업
tar -czf registry_backup.tar.gz /var/lib/registry

# S3에 업로드
aws s3 cp registry_backup.tar.gz s3://backup-bucket/registry/
```

### 15.4. 시스템 상태 복구

#### Ray 클러스터 복구

```bash
# Ray Head 노드 재시작
ray stop
ray start --head --dashboard-host 0.0.0.0

# Worker 노드들 재연결
for worker in $(cat workers.txt); do
    ssh $worker "ray start --address=<head-ip>:6379"
done
```

#### 전체 시스템 복구 절차

1. **데이터베이스 복구**: 최신 백업에서 PostgreSQL 복원
2. **RabbitMQ 재시작**: 영속화된 메시지 큐 복구
3. **API Agent 재배포**: Docker Compose 또는 K8s로 재배포
4. **Ray 클러스터 재구성**: Head 및 Worker 노드 재시작
5. **검증**: Health check 엔드포인트로 각 서비스 상태 확인

```bash
# Health check
curl http://api-agent:5900/health
curl http://plugin-registry:8000/health
```

## 16. 개발 워크플로우

### 16.1. 로컬 개발 환경 설정

#### 초기 설정

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/orc-ray-agent.git
cd orc-ray-agent

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 3. Docker Compose로 의존성 서비스 시작
docker-compose up -d postgres rabbitmq

# 4. Python 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. 의존성 설치
cd api-agent
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구

# 6. 데이터베이스 마이그레이션
alembic upgrade head

# 7. 개발 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 5900
```

### 16.2. Hot Reload 설정

**FastAPI 자동 리로드**:

```bash
# --reload 플래그 사용
uvicorn app.main:app --reload

# 특정 파일 감시
uvicorn app.main:app --reload --reload-dir app/
```

**Docker Compose에서 개발 모드**:

```yaml
# docker-compose.dev.yml
services:
  api-agent:
    build: ./api-agent
    volumes:
      - ./api-agent/app:/app/app # 소스 코드 마운트
    environment:
      - RELOAD=true
    command: uvicorn app.main:app --reload --host 0.0.0.0
```

### 16.3. 디버깅

#### VS Code 디버거 설정

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "5900"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Pytest Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

#### Ray 디버깅

```python
# ray_worker/actors.py
import ray

# 로컬 모드로 Ray 시작 (디버깅 용이)
if os.getenv('RAY_DEBUG'):
    ray.init(local_mode=True)
else:
    ray.init(address='auto')

# Actor 내부 로깅
import logging
logger = logging.getLogger(__name__)

@ray.remote
class PluginExecutorActor:
    def execute_plugin(self, job_id, image_url, input_data):
        logger.info(f"Executing plugin for job {job_id}")
        # ...
```

### 16.4. 일반적인 문제 해결

#### 데이터베이스 연결 실패

```bash
# PostgreSQL 상태 확인
docker ps | grep postgres

# 연결 테스트
psql -h localhost -U user -d plugindb

# 로그 확인
docker logs postgres
```

#### RabbitMQ 연결 문제

```bash
# RabbitMQ 상태 확인
docker exec rabbitmq rabbitmqctl status

# Management UI 접속
# http://localhost:15672 (guest/guest)

# 큐 확인
docker exec rabbitmq rabbitmqctl list_queues
```

#### Ray 클러스터 연결 실패

```bash
# Ray 상태 확인
ray status

# Ray 대시보드 접속
# http://localhost:8265

# Ray 재시작
ray stop
ray start --head
```

#### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :5900
netstat -ano | findstr :5900  # Windows

# 프로세스 종료
kill -9 <PID>
```

### 16.5. 코드 스타일 및 린팅

**pre-commit hooks 설정**:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203"]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

설치 및 실행:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### 16.6. 브랜치 전략

```
main (프로덕션)
  └── develop (개발)
      ├── feature/user-auth
      ├── feature/plugin-registry
      └── bugfix/job-status-update
```

**작업 흐름**:

1. `develop`에서 feature 브랜치 생성
2. 기능 개발 및 테스트
3. PR 생성 및 코드 리뷰
4. `develop`에 병합
5. 릴리스 시 `main`으로 병합
