from neo4j import GraphDatabase
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.driver = None
    
    def init_app(self, app):
        """初始化连接（在应用工厂中调用）"""
        self.driver = GraphDatabase.driver(
            app.config['NEO4J_URI'],
            auth=(app.config['NEO4J_USERNAME'], app.config['NEO4J_PASSWORD'])
        )
        # 验证连接
        try:
            self.driver.verify_connectivity()
            logger.info("✅ Neo4j连接成功")
        except Exception as e:
            logger.error(f"❌ Neo4j连接失败: {e}")
            self.driver = None
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("🔒 Neo4j连接已关闭")
    
    def get_session(self):
        """获取数据库会话"""
        if not self.driver:
            raise Exception("Neo4j driver not initialized")
        return self.driver.session()
    
    def verify_connection(self):
        """验证连接状态"""
        try:
            if self.driver:
                self.driver.verify_connectivity()
                return True
            return False
        except Exception:
            return False
