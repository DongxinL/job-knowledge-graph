from flask import Flask
from app.core.config import Config
from app.extensions import neo4j_conn
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 初始化扩展
    neo4j_conn.init_app(app)
    
    # 注册蓝图
    from app.api.health import health_bp
    app.register_blueprint(health_bp)
    
    # 确保应用关闭时释放连接
    @app.teardown_appcontext
    def close_neo4j_connection(error):
        # 注意：这里不关闭driver，只在应用退出时关闭
        pass
    
    return app
