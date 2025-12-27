# 独立实现
import json
import random
from io import BytesIO
from pathlib import Path

from PIL import ImageFont
from PIL.Image import Image as IMG
from PIL.ImageFont import FreeTypeFont

data_dir = Path(__file__).parent / "resources"
fonts_dir = data_dir / "fonts"
equals_dir = data_dir / "equals"

def legal_equation(equation: str) -> bool:
    """
    检查等式是否合法
    1. 必须包含且仅包含一个等号
    2. 等号两边必须是有效的数学表达式
    3. 等式必须成立
    """
    # 检查等号数量
    if equation.count('=') != 1:
        return False
    
    try:
        # 分割等号左右两边
        left, right = equation.split('=')
        
        # 检查两边是否为空
        if not left or not right:
            return False
            
        # 计算左右两边的值
        left_value = eval(left)
        right_value = eval(right)
        
        # 检查等式是否成立
        return left_value == right_value
        
    except:
        # 任何异常都表示等式不合法
        return False


def random_equation(length: int) -> str:
    """从多个等式库文件中随机选择一个指定长度的等式"""
    equals_dir = Path(__file__).parent / "resources" / "equals"
    
    # 如果预加载过，直接用缓存
    if not hasattr(random_equation, 'all_equations'):
        random_equation.all_equations = []
        
        # 加载所有 dic-*.json 文件
        for file_path in equals_dir.glob("dic-*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    equations = json.load(f)
                    if isinstance(equations, list):
                        random_equation.all_equations.extend(equations)
                    else:
                        print(f"警告: {file_path.name} 文件格式不是列表，跳过")
            except Exception as e:
                print(f"加载 {file_path.name} 时出错: {e}")
        
        print(f"已从 {len(list(equals_dir.glob('dic-*.json')))} 个文件加载 {len(random_equation.all_equations)} 个等式")
    
    # 过滤出指定长度的等式
    valid_equations = [eq for eq in random_equation.all_equations if len(eq) == length]
    if not valid_equations:
        raise ValueError(f"没有找到长度为 {length} 的等式")
    
    return random.choice(valid_equations)


def save_png(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert("RGBA")
    frame.save(output, format="png")
    return output


def load_font(name: str, fontsize: int) -> FreeTypeFont:
    return ImageFont.truetype(str(fonts_dir / name), fontsize, encoding="utf-8")