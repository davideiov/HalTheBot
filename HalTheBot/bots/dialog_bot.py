# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState, MessageFactory
from botbuilder.dialogs import Dialog
from botbuilder.schema import ChannelAccount, Activity, ConversationReference
from helpers.dialog_helper import DialogHelper
from typing import Dict


class DialogBot(ActivityHandler):

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
        conversation_references: Dict[str, ConversationReference]
    ):
        if conversation_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. user_state is required but None was given"
            )
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        self.conversation_references = conversation_references

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                reply = MessageFactory.text(
                    "Benvenuto in HalTheBot\.\n "
                    + "Il bot per gli appassionati di cinema! "
                    + "Scrivi qualcosa per iniziare\."
                )
                await turn_context.send_activity(reply)

    def _add_conversation_reference(self, activity: Activity):
        """
        This populates the shared Dictionary that holds conversation references. In this sample,
        this dictionary is used to send a message to members when /api/notify is hit.
        :param activity:
        :return:
        """
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[
            conversation_reference.user.id
        ] = conversation_reference