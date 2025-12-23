"""
Dependency injection for FastAPI routes
"""

from services.elastic_search_service import ElasticsearchService
from services.redis_service import RedisService
from services.kafka_service import KafkaSpeedLayerService
from services.lambda_merger import LambdaMerger

# Singleton instances
_es_service = None
_redis_service = None
_kafka_service = None
_lambda_merger = None

def get_es_service() -> ElasticsearchService:
    global _es_service
    if _es_service is None:
        _es_service = ElasticsearchService()
    return _es_service

def get_redis_service() -> RedisService:
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service

def get_kafka_service() -> KafkaSpeedLayerService:
    global _kafka_service
    if _kafka_service is None:
        _kafka_service = KafkaSpeedLayerService()
    return _kafka_service

def get_lambda_merger() -> LambdaMerger:
    global _lambda_merger
    if _lambda_merger is None:
        _lambda_merger = LambdaMerger(
            es_service=get_es_service(),
            kafka_service=get_kafka_service()
        )
    return _lambda_merger