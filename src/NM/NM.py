import logging
import time
import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import canexp

from src.config.config_manager import ConfigManager
from src.can.vector_interface import VectorInterface

logging.basicConfig(level=logging.INFO)


config = ConfigManager()
NM_msg = config.get('channel.zcu_can.zcu_nm')
print([NM_msg])
# # 创建接口实例并初始化
interface = VectorInterface()
if interface.initialize():
    interface.logger.info("初始化成功")
    interface.logger.info("发送NM唤醒报文")
    interface.send_message(0x53F, [NM_msg])
#     # # 启动Notifier，使用配置中的过滤规则
#     notifier = canexp.Notifier(interface.bus, [interface.printer])
    # notifier = canexp.Notifier(
    #     interface.bus,
    #     [interface.printer, canexp.Logger('logs/test.asc', can_filters=interface.can_filter)]
    # )
    # time.sleep(10) 
    # notifier.stop()
    # interface.bus.shutdown()
