"""
期货数据采集示例
展示如何使用 FuturesDataCollector 进行数据采集和分析
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from futures_data_collector import FuturesDataCollector
import pandas as pd
from datetime import datetime


def example_1_basic_collection():
    """示例1: 基础数据采集"""
    print("=" * 60)
    print("示例1: 基础期货数据采集")
    print("=" * 60)
    
    # 创建采集器
    collector = FuturesDataCollector(
        symbols=['IF', 'IC'],  # 沪深300, 中证500
        interval_minutes=10
    )
    
    # 立即采集一次数据（不启动定时任务）
    collector.collect_all_symbols()
    
    # 查看采集的数据
    for symbol in ['IF', 'IC']:
        data = collector.get_latest_data(symbol, limit=5)
        if data:
            print(f"\n{symbol} 最近5条数据:")
            for row in data:
                print(f"  时间: {row['timestamp']}, "
                      f"开: {row['open']}, "
                      f"高: {row['high']}, "
                      f"低: {row['low']}, "
                      f"收: {row['close']}")


def example_2_data_analysis():
    """示例2: 采集数据分析"""
    print("\n" + "=" * 60)
    print("示例2: 采集数据分析")
    print("=" * 60)
    
    collector = FuturesDataCollector(
        symbols=['CU', 'AU'],  # 铜, 黄金
        interval_minutes=10
    )
    
    # 获取所有采集数据
    for symbol in ['CU', 'AU']:
        data = collector.get_collected_data(symbol)
        if data:
            # 转换为 pandas DataFrame 进行分析
            df = pd.DataFrame(data)
            
            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"\n{symbol} 数据统计:")
            print(f"  总条数: {len(df)}")
            print(f"  平均价格: {df['close'].mean():.2f}")
            print(f"  最高价: {df['high'].max():.2f}")
            print(f"  最低价: {df['low'].min():.2f}")
            print(f"  平均成交量: {df['volume'].mean():.0f}")


def example_3_scheduled_collection():
    """示例3: 启动定时采集任务（会一直运行）"""
    print("\n" + "=" * 60)
    print("示例3: 启动定时采集任务")
    print("=" * 60)
    print("⚠️  此示例会持续运行，按 Ctrl+C 停止\n")
    
    # 创建采集器 - 每5分钟采集一次（演示用）
    collector = FuturesDataCollector(
        symbols=['IF', 'IC', 'CU', 'AU'],
        interval_minutes=5  # 生产环境改为10
    )
    
    try:
        # 启动定时采集
        collector.start_scheduler()
    except KeyboardInterrupt:
        print("\n✅ 采集任务已停止")


def example_4_multi_symbol_comparison():
    """示例4: 多品种数据对比"""
    print("\n" + "=" * 60)
    print("示例4: 多品种数据对比")
    print("=" * 60)
    
    collector = FuturesDataCollector(
        symbols=['IF', 'IC', 'CU', 'AU', 'NQ'],
        interval_minutes=10
    )
    
    # 采集数据
    collector.collect_all_symbols()
    
    # 对比各品种最新数据
    print("\n各品种最新K线数据对比:")
    print(f"{'品种':<6} {'开盘':<10} {'最高':<10} {'最低':<10} {'收盘':<10} {'时间':<20}")
    print("-" * 66)
    
    for symbol in ['IF', 'IC', 'CU', 'AU', 'NQ']:
        latest = collector.get_latest_data(symbol, limit=1)
        if latest:
            row = latest[0]
            print(f"{symbol:<6} {row['open']:<10} {row['high']:<10} "
                  f"{row['low']:<10} {row['close']:<10} {row['timestamp']:<20}")


if __name__ == "__main__":
    print(f"\n🚀 期货数据采集示例\n")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 选择要运行的示例
    print("请选择要运行的示例:")
    print("1. 基础数据采集")
    print("2. 采集数据分析")
    print("3. 启动定时采集任务")
    print("4. 多品种数据对比")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    try:
        if choice == '1':
            example_1_basic_collection()
        elif choice == '2':
            example_2_data_analysis()
        elif choice == '3':
            example_3_scheduled_collection()
        elif choice == '4':
            example_4_multi_symbol_comparison()
        else:
            print("❌ 无效选择")
    except Exception as e:
        print(f"❌ 错误: {e}")
