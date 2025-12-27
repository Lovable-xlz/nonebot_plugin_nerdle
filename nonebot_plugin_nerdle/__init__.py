# 基本参考 nonebot_plugin_wordle 的 __init__，做了部分修改以适应 nerdle
import asyncio
from asyncio import TimerHandle
from typing import Annotated, Any

from nonebot import on_regex, require
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends, EventToMe, RegexDict
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.utils import run_sync

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from nonebot_plugin_alconna import (
    AlcMatches,
    Alconna,
    AlconnaQuery,
    Args,
    At,
    Image,
    Option,
    Query,
    Text,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_uninfo import Uninfo

from .data_source import GuessResult, Nerdle
from .utils import random_equation

__version__ = "0.1.0"

__plugin_meta__ = PluginMetadata(
    name="猜等式",
    description="nerdle猜等式游戏",
    usage=(
        "@我/私聊 + \"猜等式\"/\"nerdle\"开始游戏；\n"
        "答案为指定长度等式，满足：左式中参与运算值一定为正值，至少存在一个运算符；右式为左式的计算值；\n"
        "发送对应长度等式即可（允许猜测不符合前述条件的等式）；\n"
        "绿色块代表此等式中有此字符且位置正确；\n"
        "黄色块代表此等式中有此字符，但该字符所处位置不对；\n"
        "灰色块代表此等式中没有此字符；\n"
        "猜出等式或用光次数则游戏结束；\n"
        "发送\"结束\"结束游戏；\n"
        "可使用 -l/--length 指定等式长度，默认为8；\n"
        f"等式长度区间：6~10"
    ),
    type="application",
    homepage="https://github.com/Lovable-xlz/nonebot_plugin_nerdle",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
)

games: dict[str, Nerdle] = {}
timers: dict[str, TimerHandle] = {}


def get_user_id(uninfo: Uninfo) -> str:
    return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"


UserId = Annotated[str, Depends(get_user_id)]


def game_is_running(user_id: UserId) -> bool:
    return user_id in games


def game_not_running(user_id: UserId) -> bool:
    return user_id not in games


def same_user(game_user_id: str):
    def _same_user(user_id: UserId) -> bool:
        return user_id in games and user_id == game_user_id

    return _same_user


nerdle_alc = Alconna(
    "nerdle",
    Option("-l|--length", Args["length", int], help_text="等式长度"),
)

matcher_nerdle = on_alconna(
    nerdle_alc,
    aliases=("猜等式",),
    rule=game_not_running,
    use_cmd_start=True,
    block=True,
    priority=13,
)
matcher_stop = on_alconna(
    "nerdle_stop",
    aliases=("结束", "结束游戏", "结束猜等式"),
    rule=game_is_running,
    use_cmd_start=True,
    block=True,
    priority=13,
)
matchers_equation: dict[str, type[Matcher]] = {}


def stop_game(user_id: str):
    if timer := timers.pop(user_id, None):
        timer.cancel()
    games.pop(user_id, None)
    if matcher := matchers_equation.pop(user_id, None):
        matcher.destroy()


async def stop_game_timeout(matcher: Matcher, user_id: str):
    game = games.get(user_id, None)
    stop_game(user_id)
    if game:
        msg = "猜等式超时，游戏结束"
        if len(game.guessed_equations) >= 1:
            msg += f"\n{game.result}"
        await matcher.send(msg)


def set_timeout(matcher: Matcher, user_id: str, timeout: float = 300):
    if timer := timers.get(user_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout,
        lambda: asyncio.ensure_future(stop_game_timeout(matcher, user_id)),
    )
    timers[user_id] = timer


@matcher_nerdle.handle()
async def _(
    matcher: Matcher,
    user_id: UserId,
    alc_matches: AlcMatches,
    to_me: bool = EventToMe(),
    length: Query[int] = AlconnaQuery("length", 8),
):
    header_match = str(alc_matches.header_match.result)
    command = str(nerdle_alc.command)
    if not (to_me or bool(header_match.rstrip(command))):
        logger.debug("Not to me, ignore")
        matcher.block = False
        await matcher.finish()

    if length.result < 6 or length.result > 10:
        await matcher.finish("等式长度应在 6~10 之间")

    equation = random_equation(length.result)
    game = Nerdle(equation)

    games[user_id] = game
    set_timeout(matcher, user_id)
    matcher_equation = on_regex(
        rf"^(?P<equation>[0-9+\-*/=]{{{length.result}}})$",
        rule=same_user(user_id),
        block=True,
        priority=14,
    )
    matcher_equation.append_handler(handle_equation)
    matchers_equation[user_id] = matcher_equation

    msg = Text(
        f"你有 {game.rows} 次机会猜出等式，等式长度为 {game.length}，请发送等式"
    ) + Image(raw=await run_sync(game.draw)())
    await msg.send()


@matcher_stop.handle()
async def _(matcher: Matcher, user_id: UserId):
    game = games[user_id]
    stop_game(user_id)

    msg = "游戏已结束"
    if len(game.guessed_equations) >= 1:
        msg += f"\n{game.result}"
    await matcher.finish(msg)


async def handle_equation(
    matcher: Matcher,
    uninfo: Uninfo,
    user_id: UserId,
    matched: dict[str, Any] = RegexDict(),
):
    game = games[user_id]
    set_timeout(matcher, user_id)

    equation = str(matched["equation"])
    result = game.guess(equation)

    if result in [GuessResult.WIN, GuessResult.LOSS]:
        stop_game(user_id)

        await (
            UniMessage.template(
                (
                    "恭喜{user} 猜出了等式！"
                    if result == GuessResult.WIN
                    else "很遗憾，没有人猜出来呢"
                )
                + "\n{result}\n{image}"
            )
            .format(
                user="你" if uninfo.scene.is_private else At("user", uninfo.user.id),
                result=game.result,
                image=Image(raw=await run_sync(game.draw)()),
            )
            .send()
        )

    elif result == GuessResult.DUPLICATE:
        await matcher.finish("你已经猜过这个等式了呢")

    elif result == GuessResult.ILLEGAL:
        await matcher.finish(f"你确定 {equation} 是一个合法的等式吗？请检查等式是否正确。")

    else:
        await UniMessage.image(raw=await run_sync(game.draw)()).send()
