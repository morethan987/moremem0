from typing import Dict, Any
from datetime import datetime
import pytz

def format_search_results(search_result: Dict[str, Any]) -> str:
    """
    将搜索结果格式化为更易读的形式
    
    Args:
        search_result: 搜索返回的原始结果字典
        
    Returns:
        str: 格式化后的易读文本
    """
    if not search_result:
        return "未找到相关记忆"
        
    formatted_text = "🔍 相关记忆:\n"
    
    # 处理记忆结果
    if "results" in search_result:
        formatted_text += "\n向量数据库查询结果："
        for i, result in enumerate(search_result["results"], 1):
            # 转换时间为本地时间
            created_at = datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
            local_time = created_at.astimezone(pytz.timezone('Asia/Shanghai'))
            formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加记忆内容
            formatted_text += f"\n{i}. {result['memory']}"
            formatted_text += f"\n   📅 记录于: {formatted_time}"
            
            # 如果有元数据，添加元数据信息
            if result.get("metadata"):
                metadata_str = ", ".join(f"{k}: {v}" for k, v in result["metadata"].items())
                formatted_text += f"\n   📎 附加元数据信息: {metadata_str}"
            
            formatted_text += "\n"
    
    # 处理关系数据
    if "relations" in search_result and search_result["relations"]:
        formatted_text += "\n图数据库查询结果："
        formatted_text += "\n🔗 相关关系:\n"
        for relation in search_result["relations"]:
            formatted_text += f"• ({relation['source']}) -[{relation['relationship']}]-> ({relation['destination']})\n"
    else:
        formatted_text += "图数据库查询失败❌"
    
    return formatted_text.strip()
