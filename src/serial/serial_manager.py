import serial
import logging
from typing import Callable, Optional
import os
from datetime import datetime
from src.config.config_manager import ConfigManager


class SerialManager:
    """串口通信管理器，处理串口数据收发"""
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.serial_port = None
        self.receiver_callback = None
        self.log_file = None
        self._setup_log_file()

    def _setup_log_file(self) -> None:
        """设置日志文件"""
        log_dir = self.config.get('log_dir', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 使用时间戳创建唯一的日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(log_dir, f'serial_{timestamp}.log')
        self.log_file = open(log_filename, 'a', encoding='utf-8')
        self.logger.info(f"串口日志文件已创建: {log_filename}")

    def _write_log(self, direction: str, data: bytes) -> None:
        """写入日志"""
        if self.log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            try:
                ascii_data = data.decode('ascii')
            except UnicodeDecodeError:
                ascii_data = str(data)
            log_entry = f"[{timestamp}] {direction}: {ascii_data}\n"
            self.log_file.write(log_entry)
            self.log_file.flush()

    def connect(self) -> bool:
        """连接串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.config.get('port', 'COM1'),
                baudrate=self.config.get('baudrate', 9600),
                bytesize=self.config.get('bytesize', serial.EIGHTBITS),
                parity=self.config.get('parity', serial.PARITY_NONE),
                stopbits=self.config.get('stopbits', serial.STOPBITS_ONE),
                timeout=self.config.get('timeout', 1)
            )
            self.logger.info(f"串口连接成功: {self.config.get('port')}")
            return True
        except Exception as e:
            self.logger.error(f"串口连接失败: {str(e)}")
            return False

    def send_data(self, data: bytes) -> bool:
        """发送数据"""
        if not self.serial_port or not self.serial_port.is_open:
            self.logger.error("串口未连接")
            return False
        try:
            self.serial_port.write(data)
            self.logger.debug(f"发送数据: {data}")
            self._write_log("TX", data)
            return True
        except Exception as e:
            self.logger.error(f"发送数据失败: {str(e)}")
            return False

    def register_receiver(self, callback: Callable[[bytes], None]) -> None:
        """注册接收回调函数"""
        self.receiver_callback = callback

    def disconnect(self) -> None:
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.logger.info("串口已断开连接")
        if self.log_file:
            self.log_file.close()
            self.log_file = None


if __name__ == "__main__":
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

    # 连接串口
    if serial_manager.connect():
        print("串口连接成功")
        
        # 发送数据
        data = b"Hello World"
        if serial_manager.send_data(data):
            print("数据发送成功")
        
        # 等待一段时间接收数据
        import time
        time.sleep(5)
        
        # 断开连接
        serial_manager.disconnect() 