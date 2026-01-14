"""
数据库核心配置模块（对应SpringBoot的DataSourceConfig + MyBatis配置）
核心功能：
1. 初始化MySQL连接池（数据源）
2. 提供数据库会话（Session）获取方法（依赖注入）
3. 封装通用CRUD操作（简化DAO层代码）
4. 支持事务管理（符合企业级数据操作规范）
"""
import contextlib
from typing import Generator, Any, Dict, List

# SQLAlchemy核心依赖
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session

# 项目配置导入
from config.settings import settings
from utils.common_utils import logger  # 可选：日志工具，后续可补充

# ===================== 1. 基础配置（对应SpringBoot的DataSource） =====================
# 创建MySQL引擎（连接池），参数对齐企业级配置
engine = create_engine(
    settings.MYSQL_URL,  # 时区配置已移到URL中，见下面的settings说明
    # 连接池配置
    pool_size=settings.MYSQL_POOL_SIZE,
    max_overflow=settings.MYSQL_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    # 修复：connect_args只保留charset，移除time_zone
    connect_args={
        "charset": "utf8mb4"  # 仅保留字符集配置
    },
    echo=settings.DEBUG
)

# 创建会话工厂（对应SpringBoot的SqlSessionFactory）
SessionLocal = sessionmaker(
    autocommit=False,  # 关闭自动提交，手动控制事务
    autoflush=False,  # 关闭自动刷新，避免不必要的数据库交互
    bind=engine
)

# 线程安全的Scoped Session（可选，多线程场景用）
ScopedSession = scoped_session(SessionLocal)

# 基础ORM模型类（所有数据库模型继承此类，对应SpringBoot的BaseEntity）
Base = declarative_base()


# ===================== 2. 会话管理（对应SpringBoot的@Autowired Session） =====================
def get_db() -> Generator[Session, None, None]:
    """
    数据库会话依赖注入函数（FastAPI专用）
    用法：在接口函数中通过 Depends(get_db) 获取会话
    示例：
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(CoreUser).all()
    """
    db = SessionLocal()
    try:
        yield db  # 提供会话
        db.commit()  # 无异常则提交事务
    except SQLAlchemyError as e:
        db.rollback()  # 异常回滚
        logger.error(f"数据库操作异常：{str(e)}")  # 记录错误日志
        raise  # 抛出异常，让接口层处理
    finally:
        db.close()  # 最终关闭会话


# 上下文管理器：非FastAPI场景（如脚本/服务层）使用
@contextlib.contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    用法：
    with db_session() as db:
        db.query(CoreUser).filter_by(username="admin").first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"数据库会话异常：{str(e)}")
        raise
    finally:
        db.close()


# ===================== 3. 数据库初始化（对应SpringBoot的SchemaInit） =====================
def init_db() -> None:
    """
    初始化数据库：
    1. 创建所有表（基于ORM模型）
    2. 执行基础数据插入脚本（可选）
    注意：需先导入所有ORM模型，否则Base.metadata.create_all不会创建对应表
    """
    try:
        # 导入所有ORM模型（必须导入，否则无法创建表）
        from models.db_model.core_user import CoreUser
        from models.db_model.core_driver_ext import CoreDriverExt
        from models.db_model.core_warehouse import CoreWarehouse
        from models.db_model.core_order import CoreOrder
        from models.db_model.core_inbound import CoreInbound
        from models.db_model.core_outbound import CoreOutbound
        from models.db_model.core_delivery_task import CoreDeliveryTask
        from models.db_model.core_delivery_track import CoreDeliveryTrack
        # AI模块模型
        from models.db_model.ai_model.ai_ocr_record import AIOcrRecord
        from models.db_model.ai_model.ai_faq_knowledge import AIFaqKnowledge
        from models.db_model.ai_model.ai_chat_record import AIChatRecord
        from models.db_model.ai_model.ai_sql_template import AISqlTemplate
        from models.db_model.ai_model.ai_sql_record import AISqlRecord
        # 系统模块模型
        from models.db_model.system_model.sys_operation_log import SysOperationLog
        from models.db_model.system_model.sys_statistics import SysStatistics

        # 创建所有表（如果不存在）
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表结构初始化完成")

        # 可选：执行基础数据插入脚本（如字典数据）
        # init_base_data()

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败：{str(e)}")
        raise


def init_base_data() -> None:
    """插入基础字典数据（如订单状态、货物类型）"""
    with db_session() as db:
        # 检查是否已存在基础数据，避免重复插入
        check_sql = text("SELECT COUNT(*) FROM sys_dict WHERE dict_type = 'goods_type'")
        count = db.execute(check_sql).scalar()
        if count > 0:
            logger.info("基础数据已存在，无需重复插入")
            return

        # 插入货物类型
        goods_type_sql = text("""
            INSERT INTO sys_dict (dict_type, dict_code, dict_name) VALUES
            ('goods_type', 'normal', '普通货物'),
            ('goods_type', 'fragile', '易碎品'),
            ('goods_type', 'bulk', '大件货物');
        """)
        # 插入订单状态
        order_status_sql = text("""
            INSERT INTO sys_dict (dict_type, dict_code, dict_name) VALUES
            ('order_status', 'pending', '待分配'),
            ('order_status', 'delivering', '配送中'),
            ('order_status', 'signed', '已签收'),
            ('order_status', 'cancelled', '已取消');
        """)

        db.execute(goods_type_sql)
        db.execute(order_status_sql)
        logger.info("✅ 基础字典数据插入完成")


# ===================== 4. 通用CRUD封装（简化DAO层代码，求职加分） =====================
class BaseDAO:
    """基础DAO类，封装通用CRUD操作（对应SpringBoot的BaseMapper）"""

    def __init__(self, model: Base):
        self.model = model  # 传入具体ORM模型

    def get_by_id(self, db: Session, id: Any) -> Base | None:
        """根据ID查询单条数据"""
        return db.query(self.model).get(id)

    def get_by_conditions(self, db: Session, conditions: Dict[str, Any]) -> Base | None:
        """根据条件查询单条数据"""
        return db.query(self.model).filter_by(**conditions).first()

    def list_by_conditions(self, db: Session, conditions: Dict[str, Any]) -> List[Base]:
        """根据条件查询多条数据"""
        return db.query(self.model).filter_by(**conditions).all()

    def create(self, db: Session, data: Dict[str, Any]) -> Base:
        """新增数据"""
        instance = self.model(**data)
        db.add(instance)
        db.flush()  # 刷新获取ID，不提交事务
        return instance

    def update(self, db: Session, instance: Base, data: Dict[str, Any]) -> Base:
        """更新数据"""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.flush()
        return instance

    def delete(self, db: Session, id: Any) -> bool:
        """物理删除（如需软删除，可自定义）"""
        instance = self.get_by_id(db, id)
        if not instance:
            return False
        db.delete(instance)
        return True
