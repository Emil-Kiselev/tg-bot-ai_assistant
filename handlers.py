from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.gpt import gpt_request

router = Router()


class StateGpt(StatesGroup):
    text = State()


@router.message(StateGpt.text)
async def state_answer(message: Message):
    await message.reply("Please, wait for the answer!")



@router.message(F.text)
async def gpt_work(message: Message, state: FSMContext):
    await state.set_state(StateGpt.text)

    answer = await message.reply("Answer is generating...")
    response = await gpt_request(message.text)

    response = await gpt_request(message.text)

    if "didn't find" in response.lower() or "sorry" in response.lower():
        response += "\n\nYou can find more info here 📄:" #your link

    await answer.edit_text(response)
    await state.clear()
