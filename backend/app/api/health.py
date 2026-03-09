from flask import Blueprint, jsonify
from datetime import datetime
from app.extensions import neo4j_conn
from flask_restx import Api, Resource, Namespace

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """健康检查接口"""
    neo4j_status = neo4j_conn.verify_connection()
    
    # 尝试获取Neo4j版本
    version = None
    if neo4j_status:
        try:
            with neo4j_conn.get_session() as session:
                result = session.run("CALL dbms.components() YIELD versions RETURN 'test' AS test, versions[0] AS version")
                record = result.single()
                version = record.get('version') if record else None
        except:
            pass
    
    return jsonify({
        "status": "ok",
        "neo4j_connected": neo4j_status,
        "neo4j_version": version,
        "timestamp": datetime.utcnow().isoformat()
    })
