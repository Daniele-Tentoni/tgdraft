from datetime import datetime
from logging import Logger
import re
from typing import Any, List, Match, Tuple

from tgdraft.managers.draft_manager import DraftManager
from tgdraft.managers.user_manager import UserManager
from tgdraft.managers.cube_manager import CubeManager

from pymongo import MongoClient
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    ForceReply,
)
from telegram.ext import (
    CallbackContext,
)

prepare_reg = r"^prepare\s(?P<cube_name>\S+)\sfor\s(?P<player_number>\d+)\sat\s((?P<time>\d{2}(?:\d{2})?[-\.]\d{1,2}(?:[-\.]\d{1,2})?\b)|(?P<word>\w*))$"
sign_reg = r"^sign\sme\sfor\s(?P<draft_id>\S+)$"
unsign_reg = r"^unsign\sme\sform\s(?P<draft_id>\S+)$"


class Bot:
    def __init__(self, logger: Logger, mongo: MongoClient) -> None:
        self.logger = logger
        self.mongo = mongo
        db = mongo.tgdraft
        self.cubeManager = CubeManager(db)
        self.draftManager = DraftManager(db)
        self.userManager = UserManager(db)

        self.matches: List[Tuple[str, Any]] = (
            [prepare_reg, self.prepare_cube],
            [sign_reg, self.sign_me],
            [unsign_reg, self.unsign_me],
        )

    async def start(
        self, update: Update, context: CallbackContext.DEFAULT_TYPE
    ) -> None:
        """
        Start bot saving user chat_id.

        Save user chat_id in the database, remembering his first access to the bot and asking him to input his username to use in telegram groups to prepare drafts.

        :param update: Update from Telegram
        :type update: Update
        :param context: PTB Context
        :type context: CallbackContext
        """
        # TODO: Change group with the group name or use another definition if we are in a private chat.

        if update.message.chat.type == update.message.chat.GROUP:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Welcome in the group {update.message.chat.title} from @tgdraft_bot",
            )

        user = update.effective_user
        await update.message.reply_markdown_v2(
            rf"Hi {user.mention_markdown_v2()}\! You can use me to manage your drafts or ask to your friends to come to play at your cube",
        )

        # Try to retrieve a previous user
        new_registered = False
        botuser = self.userManager.getByChatId(update.message.from_user.id)
        if not botuser:
            # If not, create a new one
            username = user.username if user.username else user.full_name
            botuser = self.userManager.create(
                chat_id=update.message.from_user.id, username=username
            )
            self.logger.debug("Created a new user %s", botuser.chat_id)
            new_registered = True

        if new_registered:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Registered as {botuser.username}!",
            )

    async def start_deep(
        self, update: Update, context: CallbackContext.DEFAULT_TYPE
    ) -> None:
        """
        Start bot from deep linking or inline query.

        :param update: Update from Telegram
        :type update: Update
        :param context: PTB Context
        :type context: CallbackContext
        """
        payload = context.args
        keyboard = [
            [
                InlineKeyboardButton(text="Ret", callback_data=str("Hi")),
                InlineKeyboardButton(text="Return", switch_inline_query=""),
            ],
            [
                InlineKeyboardButton(text="Ask", callback_data=str("Nope")),
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        context.user_data["cube"] = True
        cube_name = payload[0]
        context.user_data["cube_name"] = cube_name
        text = f"""So you wanna create a cube named {cube_name}??? You have to reply to this message with your cube cobra id to link it to your cube cobra cube or reply with #empty to don't link it if you haven't created you cube on cube cobra yet."""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=ForceReply(selective=True),
        )

    async def change_name(
        self, update: Update, context: CallbackContext.DEFAULT_TYPE
    ) -> None:
        """Let users change their names."""
        botuser = self.userManager.getByChatId(
            chat_id=update.message.from_user.id,
        )
        self.logger.debug(
            f"{botuser.username}({botuser.chat_id}) want to change is name"
        )
        username = botuser.username
        message = await update.message.reply_markdown_v2(
            text=f"Your actual username is {username}, how would you change it? *Send `/empty` to abort this operation\.*",
            reply_markup=ForceReply(selective=True),
        )
        context.user_data["rename"] = True
        context.user_data["rename_message"] = message.message_id

    async def handle_text(
        self, update: Update, context: CallbackContext.DEFAULT_TYPE
    ) -> None:
        botuser = self.userManager.getByChatId(update.message.from_user.id)
        is_renaming = context.user_data.get("rename", False)
        if is_renaming:
            return await self.renaming(update=update, context=context)

        is_cube = context.user_data.get("cube", False)
        if is_cube:
            group_chat_id = update.message.chat.id
            name = context.user_data.get("cube_name", "#empty")
            cobra_id = (
                "" if update.message.text == "#empty" else update.message.text
            )
            self.cubeManager.confirm_cube_cobra_id(
                cobra_id=cobra_id, cube_chat_id=group_chat_id, cube_name=name
            )
            if botuser.update_message:
                await update.message.reply_markdown_v2(
                    text=rf"You have assigned the name {name} to your cube",
                )
            return

        is_preparing_draft = context.user_data["draft", False]
        if is_preparing_draft:
            com = re.compile(prepare_reg)
            if mat := com.match(update.message.text):
                self.logger.info(f"Matched {mat} from inline query")
                cube_name = mat.group("cube_name")
                player_number = mat.group("player_number")
                word = mat.group("word")

                cube = self.cubeManager.getByName(
                    chat_id=update.effective_chat.id, name=cube_name
                )
                draft = self.draftManager.create(
                    cube=cube,
                    players=player_number,
                    date=datetime.now(),
                    chat_id=update.effective_chat.id,
                )
                keyboard = [
                    [
                        InlineKeyboardButton(
                            text="Ret", callback_data=str("Hi")
                        ),
                        InlineKeyboardButton(
                            text="Return", switch_inline_query=""
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Ask", callback_data=str("Nope")
                        ),
                    ],
                ]
                markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Prepared cube {cube_name}",
                    reply_markup=markup,
                )
            context.user_data["draft"] = False
            return

        for r, f in self.matches:
            com = re.compile(r)
            if mat := com.match(update.message.text):
                self.logger.info(f"Matched {mat}!!")
                await f(mat, update, context)
                return
        self.logger.info("No handler found")

    async def renaming(
        self, update: Update, context: CallbackContext.DEFAULT_TYPE
    ) -> None:
        try:
            self.logger.debug(f"Proceed to renaming {update.message.text}")
            botuser = self.userManager.getByChatId(update.message.from_user.id)
            message = context.user_data.get("rename_message", 0)
            id = update.message.reply_to_message.message_id
            if message != id:
                self.logger.warn("Rename messages doesn't match")
                return None

            # Check if I have to erase the existing username
            new_name = update.message.text
            if new_name == "/empty":
                new_name = ""
                text = "You have erased your username"
            else:
                text = f"You are renamed in {new_name}."

            self.logger.debug(
                f"Modify username from {botuser.username} to {new_name}"
            )
            botuser.username = new_name
            self.userManager.save(botuser)
            return await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
            )
        except Exception as ex:
            self.logger.exception("Exception in renaming", exc_info=ex)
            return None
        finally:
            # Exit from renaming status.
            context.user_data["rename"] = False
            context.user_data["rename_message"] = 0

    async def prepare_cube(
        self, mat: Match, update: Update, context: CallbackContext.DEFAULT_TYPE
    ):
        cube_name = mat.group("cube_name")
        player_number = mat.group("player_number")
        word = mat.group("word")

        cube = self.cubeManager.getByName(
            chat_id=update.effective_chat.id, name=cube_name
        )
        draft = self.draftManager.create(
            cube=cube,
            players=player_number,
            date=datetime.now(),
            chat_id=update.effective_chat.id,
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    text="Sign me", callback_data=str(draft.code)
                )
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Draft {cube_name} for {player_number} at {word}",
            reply_markup=markup,
        )

    async def callback_sign_me(self, update: Update, context: CallbackContext):
        query = update.callback_query
        cube_code = query.data
        user = update.callback_query.from_user.id
        draft = self._sign_me(cube_code, user, update, context)
        if draft is None:
            query.answer(text="You are not registered")
            return

        messages = [f"Draft {draft.code} players:"]
        index = 1
        for user in draft.users:
            messages.append(f"{index}. {user.username}")
        message = "\n".join(messages)
        await query.answer(text=message)
        await context.bot.send_message(chat_id=draft.chat_id, text=message)

    def _sign_me(
        self, code: str, user_id: int, update: Update, context: CallbackContext
    ):
        user = self.userManager.getById(user_id)
        draft = self.draftManager.sign_in(code, user)
        return draft

    async def new_cube(self, update: Update, context: CallbackContext):
        botuser = self.userManager.getById(update.message.from_user.id)
        message = await update.message.reply_markdown_v2(
            text=rf"""What is cube name?
            *For more info about register cubes in tgdraft bot, follow [this link](github.com)*""",
            reply_markup=ForceReply(selective=True),
        )
        botuser.update_message = message.message_id

    async def give_id_to_cube(self, update: Update, context: CallbackContext):
        botuser = self.userManager.getById(update.message.from_user.id)
        if botuser.update_message:
            message = await update.message.reply_markdown_v2(
                text=rf"You can give your cube an id that match a cube present in [CubeCobra](https://www.cubecobra.com) to link them",
                reply_markup=ForceReply(selective=True),
            )
            botuser.update_message = message.message_id

    async def _confirm_cube_id(
        self, id: str, name: str, update: Update, context: CallbackContext
    ):
        botuser = self.userManager.getById(update.message.from_user.id)
        group_chat_id = update.message.chat.id
        self.cubeManager.confirm_cube_cobra_id(
            cobra_id=id, cube_chat_id=group_chat_id, cube_name=name
        )
        if botuser.update_message:
            await update.message.reply_markdown_v2(
                text=rf"You have assigned the name ... to your cube",
            )

    async def confirm_cube_id(
        self, mat: Match, update: Update, context: CallbackContext
    ):
        cube_id = mat.group("cube_id")
        cube_name = mat.group("cube_name")
        self._confirm_cube_id(cube_id, cube_name, update, context)

    async def sign_me(
        self, mat: Match, update: Update, context: CallbackContext
    ):
        cube_code = mat.group("cube_code")
        user = update.message.from_user.id
        self._sign_me(cube_code, user, update, context)

    async def unsign_me(
        self, mat: Match, update: Update, context: CallbackContext
    ):
        cube_code = mat.group("cube_code")
        await update.message.reply_markdown_v2(
            f"You are sign out from {cube_code}", reply_markup=ForceReply()
        )

    async def inline_query(
        self, update: Update, context: CallbackContext
    ) -> None:
        if not (query := update.inline_query.query):
            return

        results = [
            InlineQueryResultArticle(
                id=1,
                title=f"To upper {query}",
                input_message_content=InputTextMessageContent(query.upper()),
            )
        ]

        bot_user = self.userManager.getByChatId(
            update.inline_query.from_user.id
        )
        if not bot_user:
            await context.bot.send_message(
                chat_id=update.inline_query.from_user.id,
                text=f"Missing {update.inline_query.from_user.id} user",
            )
            return

        bot_user.cubes.sort()
        names = [
            cube.cube_name
            for cube in bot_user.cubes
            if query in cube.cube_name
        ]
        if len(names) >= 1:
            pm_text = f"Prepare **{names[0]}** draft"
            pm_parameter = f"draft_{names[0]}"
        else:
            pm_text = f"Register **{query}** cube"
            pm_parameter = f"cube_{query}"
        await update.inline_query.answer(
            results=results,
            switch_pm_text=pm_text,
            switch_pm_parameter=pm_parameter,
        )
