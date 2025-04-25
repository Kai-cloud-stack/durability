import logging
import time
from typing import Optional, List
import os
import json

import canexp


class VectorInterface:
    """
    Vector硬件接口类，基于python-can库实现
    提供CAN总线通信功能
    """

    def __init__(self):
        """初始化Vector接口"""
        self.logger = logging.getLogger('can.vector')
        # 加载配置文件
        config_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'can', 'channel.json'))
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"读取配置文件失败: {str(e)}")
            self.config = {}
        # 从配置文件获取CAN过滤规则
        self.can_filter = self.config.get('can_filter', [])
        self.printer = canexp.Logger(None, self.can_filter)
        self.bus = None
        self.notifier = None
        self.is_initialized = False
        self._rx_callbacks = {}  # 接收回调函数

    def initialize(self, channel: Optional[int] = None, channel_type: str = 'zcu_can') -> bool:
        """
        初始化Vector硬件接口
        
        Args:
            channel: CAN通道号(可选)，若不提供则从配置文件获取
            channel_type: 通道类型，可选 'zcu_can' 或 'chassis_can'
            
        Returns:
            bool: 初始化是否成功
        """
        # 从配置文件中获取参数
        channel_config = self.config.get(channel_type, {})
        channel = channel if channel is not None else channel_config.get('channel', 0)
        bitrate = channel_config.get('bitrate', 500000)
        app_name = self.config.get('app_name', 'PythonCAN')
        fd = channel_config.get('fd', False)
        bitrate_switch_auto = channel_config.get('bitrate_switch_auto', True)
        
        # 更新CAN过滤规则
        self.can_filter = channel_config.get(f'{channel_type}_filter', [])
        self.printer = canexp.Logger(None, self.can_filter)
        
        try:
            self.bus = canexp.Bus(
                interface=self.config.get('interface', 'vector'),
                channel=channel,
                bitrate=bitrate,
                app_name=app_name,
                can_fd=fd,
                bitrate_switch_auto=bitrate_switch_auto
            )
            self.is_initialized = True
            self.logger.info(f"Vector接口初始化成功，通道{channel}，波特率{bitrate}")
            # self.notifier = canexp.Notifier(self.bus, [self.printer, self.asc_file])
            return True
        except Exception as e:
            self.logger.error(f"Vector接口初始化失败: {str(e)}")
            return False

    def send_message(self, msg_id: int, data: List[int],
                     channel: Optional[int] = None) -> bool:
        """
        发送CAN报文
        
        Args:
            msg_id: 报文ID
            data: 数据字节列表
            channel: 通道号(可选)
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_initialized:
            self.logger.error("Vector接口未初始化")
            return False

        try:
            msg = canexp.Message(
                arbitration_id=msg_id,
                data=data,
                is_extended_id=False,
                is_fd=self.bus.fd,
                dlc=8,
                is_rx=False
            )
            self.bus.send(msg)
            self.logger.debug(f"发送报文: ID=0x{msg_id:X}, 数据={data}")

            return True
        except Exception as e:
            self.logger.error(f"发送报文失败: {str(e)}")
            return False

    def periodic_send(self, msg_id: int, data: List[int],
                      interval: float) -> bool:
        """
        周期性发送报文
        
        Args:
            msg_id: 报文ID
            data: 数据字节列表
            interval: 发送间隔(秒)
            
        Returns:
            bool: 启动是否成功
        """
        if not self.is_initialized:
            self.logger.error("Vector接口未初始化")
            return False

        try:
            msg = canexp.Message(
                arbitration_id=msg_id,
                data=data,
                is_extended_id=False,
                is_fd=self.bus.fd
            )
            task = self.bus.send_periodic(msg, interval)
            if not task:
                self.logger.error("创建周期性发送任务失败")
                return False

            self.logger.info(f"已启动周期性发送: ID=0x{msg_id:X}, 间隔={interval}s")
            return True
        except Exception as e:
            self.logger.error(f"周期性发送启动失败: {str(e)}")
            return False

    def close(self):
        """关闭Vector接口"""
        if self.is_initialized and self.bus:
            try:
                self.bus.shutdown()
                self.is_initialized = False
                self.logger.info("Vector接口已关闭")
            except Exception as e:
                self.logger.error(f"关闭Vector接口失败: {str(e)}")






if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.DEBUG)

    # 创建接口实例并初始化
    interface = VectorInterface()
    if interface.initialize():
        print("初始化成功")
        # 发送测试报文
        interface.send_message(0x100, [1, 2, 3, 4])
        # 启动Notifier，使用配置中的过滤规则
        notifier = canexp.Notifier(
            interface.bus,
            [interface.printer, canexp.Logger('logs/test.asc', can_filters=interface.can_filter)]
        )
        time.sleep(10)
        notifier.stop()
        interface.bus.shutdown()


