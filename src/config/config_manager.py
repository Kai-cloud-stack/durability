import json
import os
import logging
from typing import Any, Dict, Optional
from datetime import datetime

class ConfigManager:
    """配置管理器，用于加载和管理配置文件"""
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:
            self.logger = logging.getLogger(__name__)
            self._load_all_configs()

    def _load_all_configs(self) -> None:
        """加载config目录下的所有JSON配置文件"""
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_dir = os.path.join(root_dir, 'config')
        try:
            for root, _, files in os.walk(config_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                            # 使用文件名（不含扩展名）作为配置键
                            config_key = os.path.splitext(file)[0]
                            self._config[config_key] = config_data
            self.logger.info("所有配置文件加载成功")
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {str(e)}")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持多级配置（使用点号分隔）
        例如：get('channel.ZCU_NM')
        """
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict:
        """获取所有配置"""
        return self._config.copy()

    def set(self, key: str, value: Any) -> None:
        """设置配置项，支持多级配置（使用点号分隔）
        例如：set('channel.ZCU_NM', '0x3F, 0x40, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00')
        """
        keys = key.split('.')
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def save(self) -> bool:
        """保存配置到文件"""
        try:
            # 获取项目根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_dir = os.path.join(root_dir, 'config')
            for config_key, config_data in self._config.items():
                # 使用时间戳创建唯一的文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(config_dir, f"{config_key}_{timestamp}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)
            self.logger.info("配置保存成功")
            return True
        except Exception as e:
            self.logger.error(f"配置保存失败: {str(e)}")
            return False

    @staticmethod
    def read_json_file(file_path: str) -> Dict:
        """读取任意JSON文件
        Args:
            file_path: JSON文件路径
        Returns:
            Dict: JSON文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"读取JSON文件失败: {str(e)}")
            return {}

