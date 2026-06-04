"""
掘金量化期货数据采集器
每隔十分钟抓取期货的十分钟K线数据，包括['open', 'high', 'low', 'close']
"""

import os
import csv
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import schedule
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class FuturesDataCollector:
    """期货数据采集器 - 定时采集K线数据"""
    
    def __init__(self, symbols: List[str], interval_minutes: int = 10):
        """
        初始化采集器
        
        参数:
            symbols: 期货品种列表，例如 ['IF', 'IC', 'CU', 'AU'] 等
            interval_minutes: 采集间隔（分钟），默认10分钟
        """
        self.symbols = symbols
        self.interval_minutes = interval_minutes
        self.api_token = os.getenv('GQUANT_API_TOKEN')
        self.account_id = os.getenv('GQUANT_ACCOUNT_ID')
        
        if not self.api_token or not self.account_id:
            raise ValueError(
                "请在 .env 文件中配置 GQUANT_ACCOUNT_ID 和 GQUANT_API_TOKEN"
            )
        
        # 初始化 Gquant 客户端
        try:
            from gquant import GQuantClient
            self.client = GQuantClient(
                account_id=self.account_id,
                api_token=self.api_token
            )
            print("✅ 成功连接掘金量化 API")
        except ImportError:
            print("❌ 未安装 gquant 库，请运行: pip install gquant")
            raise
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            raise
        
        # 创建数据存储目录
        self.data_dir = Path("futures_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 为每个品种创建CSV文件
        self.csv_files = {}
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """初始化CSV文件和表头"""
        headers = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        for symbol in self.symbols:
            csv_path = self.data_dir / f"{symbol}_kline.csv"
            self.csv_files[symbol] = csv_path
            
            # 如果文件不存在，创建并写入表头
            if not csv_path.exists():
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                print(f"✅ 创建 CSV 文件: {csv_path}")
            else:
                print(f"✅ CSV 文件已存在: {csv_path}")
    
    def fetch_kline_data(self, symbol: str, frequency: str = '10m') -> Optional[List[Dict]]:
        """
        获取K线数据
        
        参数:
            symbol: 期货品种代码 (例如 'IF', 'IC')
            frequency: 频率 ('10m' 表示10分钟K线)
        
        返回:
            K线数据列表，每条包含 {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        """
        try:
            # 获取最近的K线数据
            # 注：具体API参数需要根据掘金量化实际API调整
            kline_data = self.client.get_kline(
                symbol=symbol,
                frequency=frequency,
                count=1  # 获取最新的1条
            )
            
            if kline_data:
                print(f"✅ 获取 {symbol} K线数据成功")
                return kline_data
            else:
                print(f"⚠️  {symbol} 暂无数据")
                return None
                
        except Exception as e:
            print(f"❌ 获取 {symbol} K线数据失败: {e}")
            return None
    
    def save_kline_data(self, symbol: str, kline_data: List[Dict]):
        """
        保存K线数据到CSV
        
        参数:
            symbol: 期货品种代码
            kline_data: K线数据列表
        """
        if not kline_data:
            return
        
        csv_path = self.csv_files[symbol]
        
        try:
            with open(csv_path, 'a', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                for data in kline_data:
                    # 确保数据包含所需字段
                    row = {
                        'timestamp': data.get('time', datetime.now().isoformat()),
                        'open': data.get('open', 0),
                        'high': data.get('high', 0),
                        'low': data.get('low', 0),
                        'close': data.get('close', 0),
                        'volume': data.get('volume', 0)
                    }
                    writer.writerow(row)
            
            print(f"✅ {symbol} 数据已保存到 {csv_path}")
            
        except Exception as e:
            print(f"❌ 保存 {symbol} 数据失败: {e}")
    
    def collect_all_symbols(self):
        """采集所有品种的K线数据"""
        print(f"\n📊 开始采集数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for symbol in self.symbols:
            kline_data = self.fetch_kline_data(symbol)
            if kline_data:
                self.save_kline_data(symbol, kline_data)
        
        print(f"✅ 本轮采集完成\n")
    
    def start_scheduler(self):
        """
        启动定时任务
        每隔 interval_minutes 执行一次数据采集
        """
        print(f"🚀 启动期货数据采集器")
        print(f"📍 采集间隔: {self.interval_minutes} 分钟")
        print(f"📍 监控品种: {', '.join(self.symbols)}")
        print(f"📍 数据保存目录: {self.data_dir.absolute()}\n")
        
        # 立即执行一次
        self.collect_all_symbols()
        
        # 设置定时任务
        schedule.every(self.interval_minutes).minutes.do(self.collect_all_symbols)
        
        # 保持定时任务运行
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  采集器已停止")
    
    def get_collected_data(self, symbol: str) -> Optional[List[Dict]]:
        """
        获取已采集的数据
        
        参数:
            symbol: 期货品种代码
        
        返回:
            CSV中的所有数据行
        """
        csv_path = self.csv_files.get(symbol)
        if not csv_path or not csv_path.exists():
            return None
        
        data = []
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return data
        except Exception as e:
            print(f"❌ 读取数据失败: {e}")
            return None
    
    def get_latest_data(self, symbol: str, limit: int = 5) -> Optional[List[Dict]]:
        """
        获取最近的N条采集数据
        
        参数:
            symbol: 期货品种代码
            limit: 返回的最大条数
        
        返回:
            最近的N条数据
        """
        data = self.get_collected_data(symbol)
        if data:
            return data[-limit:]
        return None


# 使用示例
if __name__ == "__main__":
    # 配置要采集的期货品种
    # 常见品种: IF(沪深300), IC(中证500), CU(铜), AU(黄金), NQ(纳指100), etc.
    futures_symbols = ['IF', 'IC', 'CU', 'AU']
    
    try:
        # 创建采集器实例（10分钟采集一次）
        collector = FuturesDataCollector(
            symbols=futures_symbols,
            interval_minutes=10
        )
        
        # 启动定时采集任务
        collector.start_scheduler()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
