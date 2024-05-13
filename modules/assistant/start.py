# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import contextlib, re
from datetime import datetime

from telethon import Button, events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.utils import get_display_name

from core import LOGS, ultroid_bot, HNDLR, rm
from core.decorators import fullsudos, owner_and_sudos
from core.version import version
from database import udB
from database.helpers import KeyManager
from localization import get_string
from utilities.helper import inline_mention

from . import *


async def get_stored_file(event, hash):
    keym = KeyManager("FILE_STORE", cast=dict)
    msg_id = keym.get_child(hash)
    if not msg_id:
        return
    try:
        msg = await asst.get_messages(udB.get_config("LOG_CHANNEL"), ids=msg_id)
    except Exception as er:
        LOGS.warning(f"FileStore, Error: {er}")
        return
    if not msg:
        return await asst.send_message(
            event.chat_id, "__Message was deleted by owner!__", reply_to=event.id
        )
    await asst.send_message(event.chat_id, msg.text, file=msg.media, reply_to=event.id)


def get_start_message():
    Owner_info_msg = udB.get_key("BOT_INFO_START")
    _custom = True
    if Owner_info_msg is None:
        _custom = False
        Owner_info_msg = f"""
**Owner** - {ultroid_bot.full_name}
**OwnerID** - `{ultroid_bot.uid}`

**Message Forwards** - {udB.get_key("PMBOT")}

**Ultroid [v{version}](https://github.com/TeamUltroid/Ultroid), powered by @TeamUltroid**
"""
    return Owner_info_msg, _custom


_start = [
    [
        Button.inline("Lᴀɴɢᴜᴀɢᴇ 🌐", data="lang"),
#        Button.inline("Sᴇᴛᴛɪɴɢs ⚙️", data="setter"),
    ],
    [
        Button.inline("Sᴛᴀᴛs ✨", data="stat"),
        Button.inline("Bʀᴏᴀᴅᴄᴀsᴛ 📻", data="bcast"),
    ],
    [Button.inline("TɪᴍᴇZᴏɴᴇ 🌎", data="tz")],
]


@callback("ownerinfo")
async def own(event):
    message, custom = get_start_message()
    msg = message.format(
        mention=event.sender.mention, me=inline_mention(ultroid_bot.me)
    )
    if custom:
        msg += "\n\n• Powered by **@TeamUltroid**"
    await event.edit(
        msg,
        buttons=Button.inline("Close", data="closeit"),
        link_preview=False,
    )


@callback("closeit")
async def closet(lol):
    try:
        await lol.delete()
    except MessageDeleteForbiddenError:
        await lol.answer("MESSAGE_TOO_OLD", alert=True)


@asst_cmd(pattern="start( (.*)|$)", forwards=False, func=lambda x: not x.is_group)
async def ultroid_handler(event):
    args = event.pattern_match.group(1).strip()
    keym = KeyManager("BOT_USERS", cast=list)
    if not keym.contains(event.sender_id) and event.sender_id not in owner_and_sudos():
        keym.add(event.sender_id)
        kak_uiw = udB.get_key("OFF_START_LOG")
        if not kak_uiw or kak_uiw != True:
            msg = f"{inline_mention(event.sender)} `[{event.sender_id}]` started your [Assistant bot](@{asst.me.username})."
            buttons = [[Button.inline("Info", "itkkstyo")]]
            if event.sender.username:
                buttons[0].append(
                    Button.mention(
                        "User", await event.client.get_input_entity(event.sender_id)
                    )  # type: ignore
                )
            await event.client.send_message(
                udB.get_config("LOG_CHANNEL"), msg, buttons=buttons
            )
    if event.sender_id not in fullsudos():
        ok = ""
        me = inline_mention(ultroid_bot.me)
        mention = inline_mention(event.sender)
        if args and args != "set":
            await get_stored_file(event, args)
        if _starts := udB.get_key("STARTMSG"):
            msg = _starts
        else:
            if udB.get_key("PMBOT"):
                ok = "You can contact my master using this bot!!\n\nSend your Message, I will Deliver it To Master."
            msg = f"Hey there {mention}, this is Ultroid Assistant of {me}!\n\n{ok}"
        await event.reply(
            msg.format(me=me, mention=mention),
            file=udB.get_key("STARTMEDIA"),
            buttons=Button.inline("Info.", data="ownerinfo")
            if (get_start_message()[0])
            else None,
        )
    else:
        name = get_display_name(event.sender)
        if args == "set":
            """
            await event.reply(
                "Choose from the below options -",
                buttons=_settings,
            )
            """
            return
        elif args == "_manager":
            with contextlib.suppress(ImportError):
                from modules.manager._help import START, get_buttons
                await event.reply(START, buttons=get_buttons())
        elif args:
            await get_stored_file(event, args)
            return

        await event.reply(
                get_string("ast_3").format(name),
                buttons=_start,
            )


@callback("itkkstyo", owner=True)
async def ekekdhdb(e):
    text = f"When New Visitor will visit your Assistant Bot. You will get this log message!\n\nTo Disable : {HNDLR}setdb OFF_START_LOG True"
    await e.answer(text, alert=True)


@callback("mainmenu", owner=True, func=lambda x: not x.is_group)
async def ultroid(event):
    await event.edit(
        get_string("ast_3", get_display_name(event.sender)),
        buttons=_start,
    )


@callback("stat", owner=True)
async def botstat(event):
    ok = len(udB.get_key("BOT_USERS") or [])
    msg = """Ultroid Assistant - Stats
Total Users - {}""".format(
        ok,
    )
    await event.answer(msg, cache_time=0, alert=True)


@callback("bcast", owner=True)
async def bdcast(event):
    keym = KeyManager("BOT_USERS", cast=list)
    total = keym.count()
    await event.edit(f"• Broadcast to {total} users.")
    async with event.client.conversation(event.sender_id) as conv:
        await conv.send_message(
            "Enter your broadcast message.\nUse /cancel to stop the broadcast.",
        )
        response = await conv.get_response()
        if response.message == "/cancel":
            return await conv.send_message("Cancelled!!")
        success = 0
        fail = 0
        await conv.send_message(f"Starting a broadcast to {total} users...")
        start = datetime.now()
        for i in keym.get(): # type: ignore
            try:
                await asst.send_message(int(i), response)
                success += 1
            except BaseException:
                fail += 1
        end = datetime.now()
        time_taken = (end - start).seconds
        await conv.send_message(
            f"""
**Broadcast completed in {time_taken} seconds.**
Total Users in Bot - {total}
**Sent to** : `{success} users.`
**Failed for** : `{fail} user(s).`""",
        )


"""

_settings = [
    [
        Button.inline("API Kᴇʏs", data="cbs_apiset"),
        Button.inline("Pᴍ Bᴏᴛ", data="cbs_chatbot"),
    ],
    [
        Button.inline("Aʟɪᴠᴇ", data="cbs_alvcstm"),
        Button.inline("PᴍPᴇʀᴍɪᴛ", data="cbs_ppmset"),
    ],
    [
        Button.inline("Fᴇᴀᴛᴜʀᴇs", data="cbs_otvars"),
        Button.inline("VC Sᴏɴɢ Bᴏᴛ", data="cbs_vcb"),
    ],
    [Button.inline("« Bᴀᴄᴋ", data="mainmenu")],
]


@callback("setter", owner=True)
async def setting(event):
    await event.edit(
        "Choose from the below options -",
        buttons=_settings,
    )
"""

@callback("lang", owner=True)
async def setlang(event):
    languages = await rm.getLanguages()
    tultd = [
        Button.inline(
            f"{languages[ult]['name']} [{ult.lower()}]",
            data=f"set_{ult}",
        )
        for ult in languages
    ]
    buttons = list(zip(tultd[::2], tultd[1::2]))
    if len(tultd) % 2 == 1:
        buttons.append((tultd[-1],))
    buttons.append([Button.inline("« Back", data="mainmenu")])
    await event.edit(get_string("ast_4"), buttons=buttons)


@callback(re.compile(b"set_(.*)"), owner=True)
async def settt(event):
    lang = event.data_match.group(1).decode("UTF-8")
    languages = await rm.getLanguages()
    udB.del_key("language") if lang == "en" else udB.set_key("language", lang)
    await event.edit(
        f"Your language has been set to {languages[lang]['name']} [{lang}].",
        buttons=get_back_button("lang"),
    )


@callback("tz", owner=True)
async def timezone_(event):
     from pytz import timezone
     await event.delete()

     pru = event.sender_id
     var = "TIMEZONE"
     name = "Timezone"
     async with event.client.conversation(pru) as conv:
         await conv.send_message(
             "Send Your TimeZone From This List [Check From Here](http://www.timezoneconverter.com/cgi-bin/findzone.tzc)"
         )
         response = conv.wait_event(events.NewMessage(chats=pru))
         response = await response
         themssg = response.message.message
         if themssg == "/cancel":
             return await conv.send_message(
                 "Cancelled!!",
                 buttons=get_back_button("mainmenu"),
             )
         try:
             timezone(themssg)
             udB.set_key(var, themssg)
             await conv.send_message(
                f"{name} changed to {themssg}\n",
                 buttons=get_back_button("mainmenu"),
             )
         except BaseException:
             await conv.send_message(
                 "Wrong TimeZone, Try again",
                 buttons=get_back_button("mainmenu"),
             )
