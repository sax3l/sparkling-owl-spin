"""OpenSearch/Elasticsearch exporter for search and analytics."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import hashlib

try:
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from opensearchpy.exceptions import RequestError, TransportError, ConnectionError
    OPENSEARCH_AVAILABLE = True
except ImportError:
    try:
        from elasticsearch import Elasticsearch
        from elasticsearch.exceptions import RequestError, TransportError, ConnectionError
        OPENSEARCH_AVAILABLE = True
        OpenSearch = Elasticsearch  # Use Elasticsearch as fallback
    except ImportError:
        OPENSEARCH_AVAILABLE = False

from .base_exporter import BaseExporter, ExportResult, ExportFormat

logger = logging.getLogger(__name__)


class OpenSearchExporter(BaseExporter):
    """Export data to OpenSearch/Elasticsearch for search and analytics."""
    
    SUPPORTED_FORMATS = [ExportFormat.JSON]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenSearch exporter.
        
        Args:
            config: Configuration dictionary containing:
                - hosts: List of OpenSearch hosts or single host string
                - port: Port number (default: 9200)
                - use_ssl: Use SSL/TLS (default: True)
                - verify_certs: Verify SSL certificates (default: True)
                - username: Authentication username
                - password: Authentication password
                - api_key: API key for authentication (alternative to username/password)
                - index_pattern: Index pattern (default: "scraped-data-{yyyy.MM.dd}")
                - settings: Index settings
                - mappings: Index mappings
                - batch_size: Number of documents per batch (default: 1000)
                - timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        
        if not OPENSEARCH_AVAILABLE:
            raise ImportError("opensearch-py or elasticsearch is required for OpenSearch export")
        
        self.hosts = config.get('hosts', ['localhost'])
        self.port = config.get('port', 9200)
        self.use_ssl = config.get('use_ssl', True)
        self.verify_certs = config.get('verify_certs', True)
        self.username = config.get('username')
        self.password = config.get('password')
        self.api_key = config.get('api_key')
        self.index_pattern = config.get('index_pattern', 'scraped-data-{yyyy.MM.dd}')
        self.index_settings = config.get('settings', self._default_index_settings())
        self.index_mappings = config.get('mappings', {})
        self.batch_size = config.get('batch_size', 1000)
        self.timeout = config.get('timeout', 30)
        
        # Normalize hosts to list of dictionaries
        if isinstance(self.hosts, str):
            self.hosts = [self.hosts]
        
        # Initialize OpenSearch client
        self.client = self._create_client()
        
        logger.info(f"OpenSearch exporter initialized for {self.hosts}")
    
    def _default_index_settings(self) -> Dict[str, Any]:
        """Default index settings for scraped data."""
        return {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "30s",
            "index.mapping.total_fields.limit": 2000,
            "analysis": {
                "analyzer": {
                    "scraped_text_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding",
                            "stop"
                        ]
                    }
                }
            }
        }
    
    def _create_client(self) -> OpenSearch:
        """Create OpenSearch client."""
        try:
            # Build connection configuration
            client_config = {
                'hosts': self._format_hosts(),
                'timeout': self.timeout,
                'max_retries': 3,
                'retry_on_timeout': True,
                'connection_class': RequestsHttpConnection
            }
            
            # Configure SSL
            if self.use_ssl:
                client_config['use_ssl'] = True
                client_config['verify_certs'] = self.verify_certs
                client_config['ssl_show_warn'] = False
            
            # Configure authentication
            if self.api_key:
                client_config['api_key'] = self.api_key
            elif self.username and self.password:
                client_config['http_auth'] = (self.username, self.password)
            
            client = OpenSearch(**client_config)
            
            # Test connection
            info = client.info()
            logger.info(f"Connected to OpenSearch: {info.get('version', {}).get('number', 'unknown')}")
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create OpenSearch client: {e}")
            raise
    
    def _format_hosts(self) -> List[Dict[str, Any]]:
        """Format hosts for OpenSearch client."""
        formatted_hosts = []
        
        for host in self.hosts:
            if isinstance(host, str):
                formatted_hosts.append({
                    'host': host,
                    'port': self.port
                })
            elif isinstance(host, dict):
                formatted_hosts.append(host)
            else:
                logger.warning(f"Invalid host format: {host}")
        
        return formatted_hosts
    
    def _generate_index_name(self, data_type: str, timestamp: Optional[datetime] = None) -> str:
        """Generate index name based on pattern and data type."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Replace date placeholders
        index_name = self.index_pattern
        index_name = index_name.replace('{yyyy}', timestamp.strftime('%Y'))
        index_name = index_name.replace('{MM}', timestamp.strftime('%m'))
        index_name = index_name.replace('{dd}', timestamp.strftime('%d'))
        index_name = index_name.replace('{data_type}', data_type.lower())
        
        return index_name.lower()  # OpenSearch indices must be lowercase
    
    def _create_index_if_not_exists(self, index_name: str, data_type: str) -> None:
        """Create index if it doesn't exist."""
        try:
            if self.client.indices.exists(index=index_name):
                logger.debug(f"Index {index_name} already exists")
                return
            
            logger.info(f"Creating index {index_name}")
            
            # Build index configuration
            index_config = {
                'settings': self.index_settings,
                'mappings': self._generate_mappings(data_type)
            }
            
            self.client.indices.create(index=index_name, body=index_config)
            logger.info(f"Index {index_name} created successfully")
            
        except RequestError as e:
            if 'resource_already_exists_exception' in str(e):
                logger.debug(f"Index {index_name} already exists (race condition)")
            else:
                logger.error(f"Failed to create index {index_name}: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            raise
    
    def _generate_mappings(self, data_type: str) -> Dict[str, Any]:
        """Generate mappings for the data type."""
        if self.index_mappings:
            return self.index_mappings
        
        # Default mappings for scraped data
        default_mappings = {
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "url": {
                    "type": "keyword",
                    "fields": {
                        "text": {
                            "type": "text",
                            "analyzer": "scraped_text_analyzer"
                        }
                    }
                },
                "domain": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "scraped_text_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "scraped_text_analyzer"
                },
                "extracted_data": {
                    "type": "object",
                    "dynamic": True
                },
                "metadata": {
                    "properties": {
                        "extracted_at": {
                            "type": "date"
                        },
                        "template_version": {
                            "type": "keyword"
                        },
                        "data_quality_score": {
                            "type": "float"
                        },
                        "extraction_method": {
                            "type": "keyword"
                        }
                    }
                },
                "tags": {
                    "type": "keyword"
                },
                "@timestamp": {
                    "type": "date"
                }
            }
        }
        
        return default_mappings
    
    def _prepare_document(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document for OpenSearch indexing."""
        doc = record.copy()
        
        # Add timestamp
        doc['@timestamp'] = datetime.now().isoformat()
        
        # Generate document ID if not present
        if 'id' not in doc:
            doc['id'] = self._generate_document_id(record)
        
        # Ensure URL field exists
        if 'url' not in doc and 'source_url' in doc:
            doc['url'] = doc['source_url']
        
        # Extract domain from URL
        if 'url' in doc and 'domain' not in doc:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(doc['url'])
                doc['domain'] = parsed_url.netloc.lower()
            except Exception:
                doc['domain'] = 'unknown'
        
        # Flatten nested objects if needed
        if 'extracted_data' in doc and isinstance(doc['extracted_data'], dict):
            # Keep extracted_data as-is for object mapping
            pass
        
        # Add metadata
        if 'metadata' not in doc:
            doc['metadata'] = {}
        
        doc['metadata'].update({
            'indexed_at': datetime.now().isoformat(),
            'exporter_version': '1.0'
        })
        
        return doc
    
    def _generate_document_id(self, record: Dict[str, Any]) -> str:
        """Generate unique document ID."""
        # Use URL + timestamp for ID generation
        id_string = f"{record.get('url', '')}{record.get('extracted_at', datetime.now().isoformat())}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    def _bulk_index_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk index documents using OpenSearch bulk API."""
        if not documents:
            return {'indexed': 0, 'errors': 0}
        
        # Prepare bulk request body
        bulk_body = []
        for doc in documents:
            # Index action
            action = {
                "index": {
                    "_index": index_name,
                    "_id": doc.get('id')
                }
            }
            bulk_body.append(action)
            bulk_body.append(doc)
        
        try:
            response = self.client.bulk(body=bulk_body, refresh='wait_for')
            
            # Parse response
            indexed_count = 0
            error_count = 0
            
            for item in response.get('items', []):
                if 'index' in item:
                    if item['index'].get('status') in [200, 201]:
                        indexed_count += 1
                    else:
                        error_count += 1
                        logger.warning(f"Indexing error: {item['index'].get('error')}")
            
            return {'indexed': indexed_count, 'errors': error_count}
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return {'indexed': 0, 'errors': len(documents)}
    
    def export(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> ExportResult:
        """Export data to OpenSearch.
        
        Args:
            data: List of dictionaries to export
            data_type: Type of data (used for index naming)
            output_path: Not used for OpenSearch (index determined by pattern)
            **kwargs: Additional export options:
                - index_name: Override index name
                - refresh: Whether to refresh index after bulk operations
        
        Returns:
            ExportResult with OpenSearch-specific information
        """
        if not data:
            return ExportResult(
                success=True,
                message="No data to export",
                records_exported=0,
                file_path=None,
                file_size=0,
                metadata={}
            )
        
        try:
            # Determine index name
            index_name = kwargs.get('index_name') or self._generate_index_name(data_type)
            
            # Create index if needed
            self._create_index_if_not_exists(index_name, data_type)
            
            # Prepare documents
            documents = [self._prepare_document(record) for record in data]
            
            # Index documents in batches
            total_indexed = 0
            total_errors = 0
            batch_results = []
            
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                result = self._bulk_index_documents(index_name, batch)
                
                total_indexed += result['indexed']
                total_errors += result['errors']
                
                batch_results.append({
                    'batch_index': i // self.batch_size + 1,
                    'documents_attempted': len(batch),
                    'documents_indexed': result['indexed'],
                    'errors': result['errors']
                })
                
                logger.info(f"Batch {i//self.batch_size + 1} completed: {result['indexed']} indexed, {result['errors']} errors")
            
            # Refresh index if requested
            if kwargs.get('refresh', True):
                self.client.indices.refresh(index=index_name)
            
            # Get index stats
            index_stats = self._get_index_stats(index_name)
            
            success = total_errors == 0
            message = f"Exported {total_indexed} documents to OpenSearch index {index_name}"
            if total_errors > 0:
                message += f" with {total_errors} errors"
            
            return ExportResult(
                success=success,
                message=message,
                records_exported=total_indexed,
                file_path=index_name,
                file_size=0,  # Not applicable for OpenSearch
                metadata={
                    'index_name': index_name,
                    'total_documents': total_indexed,
                    'total_errors': total_errors,
                    'batch_results': batch_results,
                    'index_stats': index_stats
                }
            )
            
        except Exception as e:
            logger.error(f"OpenSearch export failed: {e}")
            return ExportResult(
                success=False,
                message=f"OpenSearch export failed: {str(e)}",
                records_exported=0,
                file_path=None,
                file_size=0,
                metadata={'error': str(e)}
            )
    
    def validate_connection(self) -> bool:
        """Validate OpenSearch connection."""
        try:
            info = self.client.info()
            cluster_health = self.client.cluster.health()
            
            logger.info(f"OpenSearch connection validated: {info.get('cluster_name')}")
            logger.info(f"Cluster health: {cluster_health.get('status')}")
            
            return True
            
        except Exception as e:
            logger.error(f"OpenSearch connection validation failed: {e}")
            return False
    
    def _get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics for an index."""
        try:
            stats = self.client.indices.stats(index=index_name)
            index_stats = stats.get('indices', {}).get(index_name, {})
            
            return {
                'document_count': index_stats.get('total', {}).get('docs', {}).get('count', 0),
                'index_size_bytes': index_stats.get('total', {}).get('store', {}).get('size_in_bytes', 0),
                'primary_shards': index_stats.get('primaries', {}).get('docs', {}).get('count', 0)
            }
            
        except Exception as e:
            logger.warning(f"Failed to get index stats for {index_name}: {e}")
            return {}
    
    def search_index(self, index_name: str, query: Dict[str, Any], size: int = 100) -> List[Dict[str, Any]]:
        """Search an OpenSearch index."""
        try:
            response = self.client.search(
                index=index_name,
                body=query,
                size=size
            )
            
            hits = response.get('hits', {}).get('hits', [])
            return [hit['_source'] for hit in hits]
            
        except Exception as e:
            logger.error(f"Search failed for index {index_name}: {e}")
            return []
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index."""
        try:
            self.client.indices.delete(index=index_name)
            logger.info(f"Index {index_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {e}")
            return False
