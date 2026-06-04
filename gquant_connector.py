"""
掘金量化 (Gquant) 连接模块
用于与掘金量化平台进行数据交互和交易执行
"""

import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GQuantConnector:
    """掘金量化连接器"""
    
    def __init__(self):
        """初始化掘金量化客户端"""
        self.account_id = os.getenv('GQUANT_ACCOUNT_ID')
        self.api_token = os.getenv('GQUANT_API_TOKEN')
        self.api_url = os.getenv('GQUANT_API_URL', 'https://api.myquant.cn')
        
        if not self.account_id or not self.api_token:
            raise ValueError(
                "请在 .env 文件中配置 GQUANT_ACCOUNT_ID 和 GQUANT_API_TOKEN\n"
                "或运行: cp .env.example .env，然后填入您的凭证"
            )
        
        try:
            # 这里导入 gquant 库
            from gquant import GQuantClient
            self.client = GQuantClient(
                account_id=self.account_id,
                api_token=self.api_token
            )
            print("✅ 成功连接掘金量化")
        except ImportError:
            print("❌ 未安装 gquant 库，请运行: pip install gquant")
            raise
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            raise
    
    def get_account_info(self) -> Optional[Dict]:
        """获取账户信息"""
        try:
            account = self.client.get_account()
            print(f"\n账户信息:")
            print(f"  余额: {account.get('balance')}")
            print(f"  资产: {account.get('assets')}")
            return account
        except Exception as e:
            print(f"❌ 获取账户信息失败: {e}")
            return None
    
    def get_positions(self) -> Optional[List]:
        """获取当前持仓"""
        try:
            positions = self.client.get_positions()
            print(f"\n当前持仓:")
            print(f"  持仓数: {len(positions)}")
            for pos in positions:
                print(f"  - {pos.get('symbol')}: {pos.get('quantity')} 股")
            return positions
        except Exception as e:
            print(f"❌ 获取持仓失败: {e}")
            return None
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = 'day'
    ) -> Optional[List]:
        """
        获取历史数据
        
        参数:
            symbol: 股票代码 (如 '000001.XSHE' 平安银行)
            start_date: 开始日期 (格式: '2024-01-01')
            end_date: 结束日期 (格式: '2024-12-31')
            frequency: 频率 ('day', 'hour', 'minute' 等)
        """
        try:
            data = self.client.get_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency
            )
            print(f"\n获取历史数据:")
            print(f"  股票代码: {symbol}")
            print(f"  数据条数: {len(data)}")
            print(f"  时间范围: {start_date} 到 {end_date}")
            return data
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return None
    
    def place_order(
        self,
        symbol: str,
        direction: str,
        volume: int,
        price: Optional[float] = None
    ) -> Optional[Dict]:
        """
        下单
        
        参数:
            symbol: 股票代码
            direction: 交易方向 ('buy' 或 'sell')
            volume: 交易数量
            price: 交易价格 (可选，None表示市价)
        """
        try:
            order = self.client.place_order(
                symbol=symbol,
                direction=direction,
                volume=volume,
                price=price
            )
            print(f"\n✅ 下单成功")
            print(f"  订单ID: {order.get('order_id')}")
            print(f"  股票代码: {symbol}")
            print(f"  交易方向: {direction}")
            print(f"  数量: {volume}")
            return order
        except Exception as e:
            print(f"❌ 下单失败: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> Optional[Dict]:
        """取消订单"""
        try:
            result = self.client.cancel_order(order_id)
            print(f"✅ 取消订单成功: {order_id}")
            return result
        except Exception as e:
            print(f"❌ 取消订单失败: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化连接
        gquant = GQuantConnector()
        
        # 获取账户信息
        gquant.get_account_info()
        
        # 获取持仓
        gquant.get_positions()
        
        # 获取历史数据示例
        data = gquant.get_historical_data(
            symbol='000001.XSHE',  # 平安银行
            start_date='2024-01-01',
            end_date='2024-12-31',
            frequency='day'
        )
        
        # 如果您想下单（需谨慎！）
        # gquant.place_order('000001.XSHE', 'buy', 100, 10.5)
        
    except Exception as e:
        print(f"初始化失败: {e}")
