"""简单的 QVERISAI 测试脚本

用于快速验证搜索和执行功能是否正常。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 设置 API Key
QVERIS_API_KEY = "sk-xxx"
os.environ["QVERIS_API_KEY"] = QVERIS_API_KEY

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_search():
    """测试搜索功能"""
    print("=" * 60)
    print("测试搜索功能")
    print("=" * 60)
    
    try:
        from openbb_qveris.utils.client import QverisClient
        
        client = QverisClient(api_key=QVERIS_API_KEY)
        print(f"[OK] 客户端创建成功")
        print(f"  Timeout: {client.TIMEOUT}s")
        print(f"  Base URL: {client.BASE_URL}")
        
        # 测试搜索
        print(f"\n搜索查询: weather")
        result = await client.search_tools(query="weather", limit=5)
        
        print(f"[OK] 搜索成功")
        print(f"  Search ID: {result.get('search_id', 'N/A')}")
        print(f"  Total: {result.get('total', 0)}")
        
        tools = result.get("tools", []) or result.get("results", [])
        print(f"  找到工具数: {len(tools)}")
        
        if tools:
            print(f"\n  前3个工具:")
            for i, tool in enumerate(tools[:3], 1):
                tool_id = tool.get("tool_id") or tool.get("id")
                tool_name = tool.get("tool_name") or tool.get("name") or tool.get("title")
                print(f"    {i}. {tool_name} (ID: {tool_id})")
        else:
            print(f"\n  [WARNING] 未找到工具")
            print(f"  完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        return result
        
    except Exception as e:
        print(f"[ERROR] 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_execute():
    """测试执行功能"""
    print("\n" + "=" * 60)
    print("测试执行功能")
    print("=" * 60)
    
    try:
        from openbb_qveris.utils.client import QverisClient
        
        client = QverisClient(api_key=QVERIS_API_KEY)
        
        # 使用已知的 tool_id
        tool_id = "ths_ifind.company_basics.v1"
        parameters = {"codes": "600519.SH"}
        
        print(f"执行工具: {tool_id}")
        print(f"参数: {parameters}")
        print(f"超时设置: {client.TIMEOUT}s")
        
        result = await client.execute_tool(
            tool_id=tool_id,
            parameters=parameters
        )
        
        print(f"\n[OK] 执行成功！")
        print(f"  执行 ID: {result.get('execution_id', 'N/A')}")
        print(f"  成功: {result.get('success', False)}")
        print(f"  耗时: {result.get('elapsed_time_ms', 0)}ms")
        
        if result.get('result'):
            result_data = result.get('result', {})
            if isinstance(result_data, dict) and 'data' in result_data:
                data = result_data.get('data', [])
                print(f"  数据条数: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"  结果预览: {str(result_data)[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    print("=" * 60)
    print("QVERISAI 简单测试")
    print("=" * 60)
    print(f"API Key: {QVERIS_API_KEY[:10]}...{QVERIS_API_KEY[-4:]}")
    print()
    
    # 测试搜索
    search_result = await test_search()
    
    # 测试执行
    execute_result = await test_execute()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    if search_result and search_result.get('total', 0) > 0:
        print("[OK] 搜索功能正常")
    else:
        print("[ERROR] 搜索功能异常（返回空结果）")
    
    if execute_result and execute_result.get('success', False):
        print("[OK] 执行功能正常")
    else:
        print("[ERROR] 执行功能异常")


if __name__ == "__main__":
    asyncio.run(main())

