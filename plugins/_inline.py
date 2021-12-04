# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
import time
from datetime import datetime
from os import remove

from git import Repo
from pyUltroid.dB._core import HELP, LIST
from pyUltroid.functions.helper import gen_chlog, time_formatter, updater
from pyUltroid.functions.misc import split_list
from pyUltroid.misc._assistant import callback, in_pattern
from telethon import Button
from telethon.tl.types import InputWebDocument, Message
from telethon.utils import resolve_bot_file_id

from . import HNDLR, INLINE_PIC, LOGS, OWNER_NAME, asst, get_string, start_time, udB
from ._help import _main_help_menu

# ================================================#

TLINK = INLINE_PIC or "https://telegra.ph/file/d9c9bc13647fa1d96e764.jpg"
helps = get_string("inline_1")

add_ons = udB.get_key("ADDONS")

if add_ons is not False:
    zhelps = get_string("inline_2")
else:
    zhelps = get_string("inline_3")

PLUGINS = HELP.get("Official", [])
ADDONS = HELP.get("Addons", [])
upage = 0
# ============================================#

# --------------------BUTTONS--------------------#

SUP_BUTTONS = [
    [
        Button.url("• Repo •", url="https://github.com/TeamUltroid/Ultroid"),
        Button.url("• Support •", url="t.me/UltroidSupport"),
    ],
]

# --------------------BUTTONS--------------------#


@in_pattern(owner=True, func=lambda x: not x.text)
async def inline_alive(o):
    MSG = "• **Ultroid Userbot •**"
    WEB0 = InputWebDocument(
        "https://telegra.ph/file/55dd0f381c70e72557cb1.jpg", 0, "image/jpg", []
    )
    RES = [
        await o.builder.article(
            type="photo",
            text=MSG,
            include_media=True,
            buttons=SUP_BUTTONS,
            title="Ultroid Userbot",
            description="Userbot | Telethon",
            url=TLINK,
            thumb=WEB0,
            content=InputWebDocument(TLINK, 0, "image/jpg", []),
        )
    ]
    await o.answer(RES, switch_pm="👥 ULTROID PORTAL", switch_pm_param="start")


@in_pattern("ultd", owner=True)
async def inline_handler(event):
    z = []
    for x in LIST.values():
        z.extend(x)
    text = get_string("inline_4").format(
        OWNER_NAME,
        len(HELP.get("Official", [])),
        len(HELP.get("Addons", [])),
        len(z),
    )
    if INLINE_PIC:
        result = await event.builder.photo(
            file=INLINE_PIC,
            link_preview=False,
            text=text,
            buttons=_main_help_menu,
        )
    else:
        result = await event.builder.article(
            title="Ultroid Help Menu", text=text, buttons=_main_help_menu
        )
    await event.answer([result], gallery=True)


@in_pattern("pasta", owner=True)
async def _(event):
    ok = event.text.split("-")[1]
    link = "https://spaceb.in/" + ok
    raw = f"https://spaceb.in/api/v1/documents/{ok}/raw"
    result = await event.builder.article(
        title="Paste",
        text="Pasted to Spacebin 🌌",
        buttons=[
            [
                Button.url("SpaceBin", url=link),
                Button.url("Raw", url=raw),
            ],
        ],
    )
    await event.answer([result])


@callback("ownr", owner=True)
async def setting(event):
    z = []
    for x in LIST.values():
        z.extend(x)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(HELP.get("Official", [])),
            len(HELP.get("Addons", [])),
            len(z),
        ),
        file=INLINE_PIC,
        link_preview=False,
        buttons=[
            [
                Button.inline("•Pɪɴɢ•", data="pkng"),
                Button.inline("•Uᴘᴛɪᴍᴇ•", data="upp"),
            ],
            [
                Button.inline("•Stats•", data="alive"),
                Button.inline("•Uᴘᴅᴀᴛᴇ•", data="doupdate"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="open")],
        ],
    )


_strings = {"Official": helps, "Addons": zhelps, "VCBot": get_string("inline_6")}


@callback(re.compile("uh_(.*)"))
async def help_func(ult):
    key, count = ult.data_match.group(1).decode("utf-8").split("_")
    if key == "VCBot" and HELP.get("VCBot") is None:
        return await ult.answer("Voice Call is not Active!", alert=True)
    elif key == "Addons" and HELP.get("Addons") is None:
        return await ult.answer(
            f"Do '{HNDLR}setdb ADDONS True' to Load Official Addons", alert=True
        )
    if "|" in count:
        _, count = count.split("|")
    if not count:
        count = 0
    else:
        count = int(count)
    text = _strings.get(key, "").format(OWNER_NAME, len(HELP.get(key)))
    await ult.edit(
        text, file=INLINE_PIC, buttons=page_num(count, key), link_preview=False
    )


@callback(re.compile("uplugin_(.*)"))
async def uptd_plugin(event):
    key, file = event.data_match.group(1).decode("utf-8").split("_")
    index = None
    if "|" in file:
        file, index = file.split("|")
    key_ = HELP.get(key, [])
    hel_p = f"Plugin Name - `{file}`\n"
    help_ = ""
    try:
        for i in key_[file]:
            help_ += i
    except BaseException:
        if file in LIST:
            help_ = get_string("help_11").format(file)
            for d in LIST[file]:
                help_ += HNDLR + d
                help_ += "\n"
    if not help_:
        help_ = f"{file} has no Detailed Help!"
    help_ += "\n© Join @TeamUltroid"
    buttons = []
    if INLINE_PIC:
        data = f"sndplug_{key}_{file}"
        if index is not None:
            data += f"|{index}"
        buttons.append(
            [
                Button.inline(
                    "« Sᴇɴᴅ Pʟᴜɢɪɴ »",
                    data=data,
                )
            ]
        )
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
    buttons.append(
        [
            Button.inline("« Bᴀᴄᴋ", data=data),
        ]
    )
    try:
        await event.edit(help_, buttons=buttons)
    except Exception as er:
        LOGS.exception(er)
        help = f"Do `{HNDLR}help {key}` to get list of commands."
        await event.edit(help, buttons=buttons)


@callback(data="doupdate", owner=True)
async def _(event):
    if not updater():
        return await event.answer(get_string("inline_9"), cache_time=0, alert=True)
    if not INLINE_PIC:
        return await event.answer(f"Do '{HNDLR}update'")
    repo = Repo.init()
    changelog, tl_chnglog = await gen_chlog(
        repo, f"HEAD..upstream/{repo.active_branch}"
    )
    changelog_str = changelog + "\n\n" + get_string("inline_8")
    if len(changelog_str) > 1024:
        await event.edit(get_string("upd_4"))
        with open("ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await event.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=[
                [Button.inline("• Uᴘᴅᴀᴛᴇ Nᴏᴡ •", data="updatenow")],
                [Button.inline("« Bᴀᴄᴋ", data="ownr")],
            ],
        )
        remove("ultroid_updates.txt")
    else:
        await event.edit(
            changelog_str,
            buttons=[
                [Button.inline("Update Now", data="updatenow")],
                [Button.inline("« Bᴀᴄᴋ", data="ownr")],
            ],
            parse_mode="html",
        )


@callback(data="pkng", owner=True)
async def _(event):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds
    pin = f"🌋Pɪɴɢ = {ms} microseconds"
    await event.answer(pin, cache_time=0, alert=True)


@callback(data="upp", owner=True)
async def _(event):
    uptime = time_formatter((time.time() - start_time) * 1000)
    pin = f"🙋Uᴘᴛɪᴍᴇ = {uptime}"
    await event.answer(pin, cache_time=0, alert=True)


@callback(data="inlone", owner=True)
async def _(e):
    button = [
        [
            Button.switch_inline(
                "Pʟᴀʏ Sᴛᴏʀᴇ Aᴘᴘs",
                query="app telegram",
                same_peer=True,
            ),
            Button.switch_inline(
                "Mᴏᴅᴅᴇᴅ Aᴘᴘs",
                query="mods minecraft",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Sᴇᴀʀᴄʜ Oɴ Gᴏᴏɢʟᴇ",
                query="go TeamUltroid",
                same_peer=True,
            ),
            Button.switch_inline(
                "Search on XDA",
                query="xda telegram",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "WʜɪSᴘᴇʀ",
                query="wspr @username Hello🎉",
                same_peer=True,
            ),
            Button.switch_inline(
                "YᴏᴜTᴜʙᴇ Dᴏᴡɴʟᴏᴀᴅᴇʀ",
                query="yt Ed Sheeran Perfect",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Piston Eval",
                query="run javascript console.log('Hello Ultroid')",
                same_peer=True,
            ),
            Button.switch_inline(
                "OʀᴀɴɢᴇFᴏx🦊",
                query="ofox beryllium",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Tᴡɪᴛᴛᴇʀ Usᴇʀ", query="twitter theultroid", same_peer=True
            ),
            Button.switch_inline(
                "Kᴏᴏ Sᴇᴀʀᴄʜ", query="koo @__kumar__amit", same_peer=True
            ),
        ],
        [
            Button.switch_inline(
                "Fᴅʀᴏɪᴅ Sᴇᴀʀᴄʜ", query="fdroid telegram", same_peer=True
            )
        ],
        [
            Button.inline(
                "« Bᴀᴄᴋ",
                data="open",
            ),
        ],
    ]
    await e.edit(buttons=button, link_preview=False)


@callback(data="open", owner=True)
async def opner(event):
    z = []
    for x in LIST.values():
        z.extend(x)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(HELP.get("Official", [])),
            len(HELP.get("Addons", [])),
            len(z),
        ),
        buttons=_main_help_menu,
        link_preview=False,
    )


@callback(data="close", owner=True)
async def on_plug_in_callback_query_handler(event):
    await event.edit(
        get_string("inline_5"),
        buttons=Button.inline("Oᴘᴇɴ Aɢᴀɪɴ", data="open"),
    )


def page_num(index, key):
    rows = 5
    cols = 2
    loaded = HELP.get(key, [])
    emoji = udB.get_key("EMOJI_IN_HELP") or "✘"
    List = [
        Button.inline(f"{emoji} {x} {emoji}", data=f"uplugin_{key}_{x}|{index}")
        for x in sorted(loaded)
    ]
    all_ = split_list(List, cols)
    new_ = split_list(all_, rows)
    try:
        new_ = new_[index]
    except IndexError:
        new_ = new_[0] if new_ else []
    new_.append(
        [
            Button.inline(
                "« Pʀᴇᴠɪᴏᴜs",
                data=f"uh_{key}_{index-1}",
            ),
            Button.inline("« Bᴀᴄᴋ »", data="open"),
            Button.inline(
                "Nᴇxᴛ »",
                data=f"uh_{key}_{index+1}",
            ),
        ]
    )
    return new_


# --------------------------------------------------------------------------------- #


STUFF = {}


@in_pattern("stf(.*)", owner=True)
async def ibuild(e):
    n = e.pattern_match.group(1)
    builder = e.builder
    if not (n and n.isdigit()):
        return
    ok = STUFF.get(int(n))
    txt = ok.get("msg")
    pic = ok.get("media")
    btn = ok.get("button")
    if not (pic or txt):
        txt = "Hey!"
    if pic:
        try:
            include_media = True
            mime_type, _pic = None, None
            cont, results = None, None
            try:
                ext = str(pic).split(".")[-1].lower()
            except BaseException:
                ext = None
            if ext in ["img", "jpg", "png"]:
                _type = "photo"
                mime_type = "image/jpg"
            elif ext in ["mp4", "mkv", "gif"]:
                mime_type = "video/mp4"
                _type = "gif"
            else:
                try:
                    if "telethon.tl.types" in str(type(pic)):
                        _pic = pic
                    else:
                        _pic = resolve_bot_file_id(pic)
                except BaseException:
                    pass
                if _pic:
                    results = [
                        await builder.document(
                            _pic,
                            title="Ultroid Op",
                            text=txt,
                            description="@TheUltroid",
                            buttons=btn,
                            link_preview=False,
                        )
                    ]
                else:
                    _type = "article"
                    include_media = False
            if not results:
                if include_media:
                    cont = InputWebDocument(pic, 0, mime_type, [])
                results = [
                    await builder.article(
                        title="Ultroid Op",
                        type=_type,
                        text=txt,
                        description="@TeamUltroid",
                        include_media=include_media,
                        buttons=btn,
                        thumb=cont,
                        content=cont,
                        link_preview=False,
                    )
                ]
            return await e.answer(results)
        except Exception as er:
            LOGS.exception(er)
    result = [
        await builder.article("Ultroid Op", text=txt, link_preview=False, buttons=btn)
    ]
    await e.answer(result)


async def something(e, msg, media, button, reply=True, chat=None):
    if e.client._bot:
        return await e.reply(msg, file=media, buttons=button)
    num = len(STUFF) + 1
    STUFF.update({num: {"msg": msg, "media": media, "button": button}})
    try:
        res = await e.client.inline_query(asst.me.username, f"stf{num}")
        return await res[0].click(
            chat or e.chat_id,
            reply_to=bool(isinstance(e, Message) and reply),
            hide_via=True,
            silent=True,
        )

    except Exception as er:
        LOGS.info(er)
