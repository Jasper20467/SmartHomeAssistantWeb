"""
測試修復 delete API 的 JSON 解析錯誤
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from LineBotAI.Home_assistant.base_service import BaseService
from LineBotAI.Home_assistant.schedule_service import ScheduleService
from LineBotAI.Home_assistant.consumable_service import ConsumableService
import logging

def test_delete_operations():
    """測試 delete 操作是否正確處理空響應"""
    
    # 設置 logger
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    
    # 創建 base service
    base_service = BaseService(
        base_url="http://localhost:8000",
        headers={"Content-Type": "application/json"},
        logger=logger
    )
    
    # 創建 services
    schedule_service = ScheduleService(base_service)
    consumable_service = ConsumableService(base_service)
    
    # 模擬 204 No Content 響應
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.content = b""
    mock_response.raise_for_status = Mock()
    
    print("=== 測試 Schedule Delete 操作 ===")
    with patch('requests.delete', return_value=mock_response):
        result = schedule_service.delete_schedule("1")
        print(f"Schedule Delete 結果: {result}")
        assert result == {"success": True, "message": "操作成功完成"}
        print("✓ Schedule Delete 測試通過")
    
    print("\n=== 測試 Consumable Delete 操作 ===")
    with patch('requests.delete', return_value=mock_response):
        result = consumable_service.delete_consumable("1")
        print(f"Consumable Delete 結果: {result}")
        assert result == {"success": True, "message": "操作成功完成"}
        print("✓ Consumable Delete 測試通過")
    
    # 測試其他 HTTP 狀態碼
    print("\n=== 測試其他成功狀態碼 ===")
    mock_response.status_code = 200
    mock_response.content = b""
    with patch('requests.delete', return_value=mock_response):
        result = schedule_service.delete_schedule("1")
        print(f"200 狀態碼結果: {result}")
        assert result == {"success": True, "message": "操作成功完成"}
        print("✓ 200 狀態碼測試通過")
    
    print("\n=== 所有測試通過！ ===")

if __name__ == "__main__":
    test_delete_operations()
