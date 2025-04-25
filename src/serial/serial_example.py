import logging
import time
from src.serial.serial_manager import SerialManager
from src.config.config_manager import ConfigManager

def main():
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 获取配置
    config = ConfigManager()
    serial_config = config.get('serial', {})

    # 创建串口管理器
    serial_manager = SerialManager(serial_config, logger)

    # 定义数据接收回调
    def on_data_received(data: bytes):
        print(f"收到数据: {data}")

    # 注册接收回调
    serial_manager.register_receiver(on_data_received)

    try:
        # 连接串口
        if serial_manager.connect():
            print("串口连接成功")
            
            # 发送数据
            data = b"Hello World"
            if serial_manager.send_data(data):
                print("数据发送成功")
            
            # 等待一段时间接收数据
            time.sleep(5)
            
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        # 断开连接
        serial_manager.disconnect()

if __name__ == "__main__":
    main() 