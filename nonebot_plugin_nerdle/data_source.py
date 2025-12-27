# 参考 wordle 的 data_source.py，增加了每个字符状态的渲染，调整了部分 ui
from enum import Enum
from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw
from PIL.Image import Image as IMG

from .utils import legal_equation, load_font, save_png


class GuessResult(Enum):
    WIN = 0  # 猜出正确等式
    LOSS = 1  # 达到最大可猜次数，未猜出正确等式
    DUPLICATE = 2  # 等式重复
    ILLEGAL = 3  # 等式不合法


class Nerdle:
    def __init__(self, equation: str):
        self.equation: str = equation  # 等式
        self.result = f"【等式】：{self.equation}"
        self.length: int = len(equation)  # 等式长度
        self.rows: int = len(equation) - 2  # 猜测机会
        self.guessed_equations: list[str] = []  # 记录已猜等式

        self.block_size = (40, 40)  # 文字块尺寸
        self.block_padding = (10, 10)  # 文字块之间间距
        self.padding = (20, 20)  # 边界间距
        self.border_width = 2  # 边框宽度
        self.font_size = 20  # 字体大小
        self.font = load_font("KarnakPro-Bold.ttf", self.font_size)

        self.correct_color = (134, 163, 115)  # 存在且位置正确时的颜色
        self.exist_color = (198, 182, 109)  # 存在但位置不正确时的颜色
        self.wrong_color = (123, 123, 124)  # 不存在时颜色
        self.border_color = (123, 123, 124)  # 边框颜色
        self.bg_color = (255, 255, 255)  # 背景颜色
        self.font_color = (255, 255, 255)  # 文字颜色
        self.unguessed_color = (255, 255, 255)  # 未猜测字符的背景颜色（白色）
        self.unguessed_font_color = (123, 123, 124)  # 未猜测字符的字体颜色（灰色）
        
        # 初始化字符状态字典
        self.char_status = {}
        all_chars = "0123456789+-*/="
        for char in all_chars:
            self.char_status[char] = "unguessed"  # 初始状态为未猜测

    def guess(self, equation: str) -> Optional[GuessResult]:
        if equation == self.equation:
            self.guessed_equations.append(equation)
            self._update_char_status(equation)
            return GuessResult.WIN
        if equation in self.guessed_equations:
            return GuessResult.DUPLICATE
        if not legal_equation(equation):
            return GuessResult.ILLEGAL
        self.guessed_equations.append(equation)
        self._update_char_status(equation)
        if len(self.guessed_equations) == self.rows:
            return GuessResult.LOSS

    def _update_char_status(self, equation: str):
        """更新字符状态，基于当前猜测"""
        # 记录这次猜测中每个字符的最佳状态
        guess_status = {}
        
        # 初始化
        for char in equation:
            guess_status[char] = "wrong"  # 默认为不存在
        
        # 检查绿（位置正确）
        for i, char in enumerate(equation):
            if i < len(self.equation) and char == self.equation[i]:
                guess_status[char] = "correct"
        
        # 检查黄（存在但位置不正确）
        # 创建一个答案字符副本，跟踪尚未匹配的字符
        remaining_chars = list(self.equation)
        
        # 移除绿色字符
        for i, char in enumerate(equation):
            if i < len(self.equation) and char == self.equation[i]:
                if char in remaining_chars:
                    remaining_chars.remove(char)
        
        # 检查黄色字符
        for i, char in enumerate(equation):
            if char in remaining_chars and guess_status[char] != "correct":
                guess_status[char] = "exist"
                remaining_chars.remove(char)
        
        # 更新字符状态（优先级：correct > exist > wrong > unguessed）
        for char, new_status in guess_status.items():
            current_status = self.char_status[char]
            
            # 状态优先级映射
            status_priority = {
                "unguessed": 0,
                "wrong": 1,
                "exist": 2,
                "correct": 3
            }
            
            # 只有新状态优先级更高时才更新
            if status_priority[new_status] > status_priority[current_status]:
                self.char_status[char] = new_status

    def draw_block(self, color: tuple[int, int, int], char: str, font_color: tuple[int, int, int] = None) -> IMG:
        block = Image.new("RGB", self.block_size, self.border_color)
        inner_w = self.block_size[0] - self.border_width * 2
        inner_h = self.block_size[1] - self.border_width * 2
        inner = Image.new("RGB", (inner_w, inner_h), color)
        block.paste(inner, (self.border_width, self.border_width))
        if char:
            draw = ImageDraw.Draw(block)
            bbox = self.font.getbbox(char)
            x = (self.block_size[0] - bbox[2]) / 2
            y = (self.block_size[1] - bbox[3]) / 2
            
            # 使用指定的字体颜色，如果没有指定则使用默认的字体颜色
            text_color = font_color if font_color is not None else self.font_color
            draw.text((x, y), char, font=self.font, fill=text_color)
        return block

    def draw(self) -> BytesIO:
        # 计算主游戏区域宽度
        main_board_w = self.length * self.block_size[0]
        main_board_w += (self.length - 1) * self.block_padding[0] + 2 * self.padding[0]
        
        # 计算字符状态区域宽度
        char_blocks_per_row = 5  # 每行5个字符
        char_board_w = char_blocks_per_row * self.block_size[0]
        char_board_w += (char_blocks_per_row - 1) * self.block_padding[0] + 2 * self.padding[0]
        
        # 画布宽度取两者较大值
        board_w = max(main_board_w, char_board_w)
        
        # 计算主游戏区域高度
        main_board_h = self.rows * self.block_size[1]
        main_board_h += (self.rows - 1) * self.block_padding[1] + 2 * self.padding[1]
        
        # 计算字符状态区域高度（3行）
        char_status_rows = 3
        char_status_h = char_status_rows * self.block_size[1]
        char_status_h += (char_status_rows - 1) * self.block_padding[1] + 2 * self.padding[1]
        
        # 总高度 = 主游戏区域高度 + 字符状态区域高度
        total_h = main_board_h + char_status_h
        
        # 创建画布
        board_size = (board_w, total_h)
        board = Image.new("RGB", board_size, self.bg_color)

        # 计算主游戏区域的起始X坐标，使其居中
        main_board_start_x = (board_w - main_board_w) // 2 + self.padding[0]

        # 绘制主游戏区域
        for row in range(self.rows):
            if row < len(self.guessed_equations):
                guessed_equation = self.guessed_equations[row]

                equation_incorrect = ""  # 猜错的字符
                for i in range(self.length):
                    if guessed_equation[i] != self.equation[i]:
                        equation_incorrect += self.equation[i]
                    else:
                        equation_incorrect += "_"  # 猜对的字符用下划线代替

                blocks: list[IMG] = []
                for i in range(self.length):
                    char = guessed_equation[i]
                    if char == self.equation[i]:
                        color = self.correct_color
                    elif char in equation_incorrect:
                        equation_incorrect = equation_incorrect.replace(char, "_", 1)
                        color = self.exist_color
                    else:
                        color = self.wrong_color
                    blocks.append(self.draw_block(color, char))

            else:
                blocks = [
                    self.draw_block(self.bg_color, "") for _ in range(self.length)
                ]

            for col, block in enumerate(blocks):
                x = main_board_start_x + (self.block_size[0] + self.block_padding[0]) * col
                y = self.padding[1] + (self.block_size[1] + self.block_padding[1]) * row
                board.paste(block, (int(x), int(y)))
        
        # 绘制字符状态区域
        chars = "0123456789+-*/="  # 15个字符
        char_blocks_per_row = 5  # 每行5个字符
        
        # 计算字符状态区域的起始Y坐标
        char_start_y = main_board_h + self.padding[1]
        
        # 计算字符状态区域的起始X坐标，使其居中
        char_board_content_w = char_blocks_per_row * self.block_size[0]
        char_board_content_w += (char_blocks_per_row - 1) * self.block_padding[0]
        char_start_x = (board_w - char_board_content_w) // 2
        
        for row in range(char_status_rows):
            for col in range(char_blocks_per_row):
                char_index = row * char_blocks_per_row + col
                if char_index < len(chars):
                    char = chars[char_index]
                    # 根据字符状态选择颜色
                    status = self.char_status.get(char, "unguessed")
                    if status == "correct":
                        color = self.correct_color
                        font_color = self.font_color  # 白色字体
                    elif status == "exist":
                        color = self.exist_color
                        font_color = self.font_color  # 白色字体
                    elif status == "wrong":
                        color = self.wrong_color
                        font_color = self.font_color  # 白色字体
                    else:  # unguessed
                        color = self.unguessed_color  # 白色背景
                        font_color = self.unguessed_font_color  # 灰色字体
                    
                    # 绘制字符块
                    block = self.draw_block(color, char, font_color)
                    x = char_start_x + (self.block_size[0] + self.block_padding[0]) * col
                    y = char_start_y + (self.block_size[1] + self.block_padding[1]) * row
                    board.paste(block, (int(x), int(y)))
        
        return save_png(board)