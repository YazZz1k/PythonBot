import time
import logging

from aiogram import Bot, Dispatcher, executor, types

#keyboard imports
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

#state machine
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import random
import sqlite_db

TOKEN = 'TOKEN'

class FSMDelete(StatesGroup):
    word2del = State()

class FSMAdd(StatesGroup):
    word = State()
    translation = State()

class FSMRepeat(StatesGroup):
    check_answer = State()

#state machine
storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

#sqlit 
sqlite_db.sql_start()

#keyboard
add_card_board = KeyboardButton('/add')
delete_board = KeyboardButton('/delete')
list_board = KeyboardButton('/list')
repeat_board = KeyboardButton('/repeat')

kb_client = ReplyKeyboardMarkup(resize_keyboard = True)
kb_client.row(add_card_board, repeat_board).row(list_board, delete_board)

@dp.message_handler(commands = ['start'])
async def start_handler(message: types.Message):
  print("start handler")
  user_id = message.from_user.id
  user_name = message.from_user.first_name
  user_full_name = message.from_user.full_name
  await bot.send_message(user_id, f"Hi! {user_full_name}", reply_markup = kb_client)

#list
@dp.message_handler(commands = ['list'])
async def list_handler(message: types.Message):
  print("user tap list")
  user_id = message.from_user.id
  dict = await sqlite_db.sql_read(user_id)
  for card in dict:
    await bot.send_message(user_id, f"{card[1]} -> {card[2]}")

# delete
@dp.message_handler(commands = ['delete'], state = None)
async def delete_handler(message: types.Message):
  print("delete handler")
  await FSMDelete.word2del.set()
  await message.reply(f"Какое слово хочешь удалить?")

@dp.message_handler(state = FSMDelete.word2del)
async def get_delete_word(message: types.Message, state : FSMDelete):
  print('get delete word')
  if(await sqlite_db.sql_delete(message.from_user.id, message.text)):
    await message.reply(f"Удалил слово")
  else:
    await message.reply(f"Такого слова нет у тебя в карточках")
  
  await state.finish()

# add
@dp.message_handler(commands = ['add'], state = None)
async def add_card_handler(message: types.Message):
  print("User tap \\add")
  await FSMAdd.word.set()
  await message.reply("tap word")
  
@dp.message_handler(state = FSMAdd.word)
async def load_word(message: types.Message, state: FSMContext):
  print("load word")
  async with state.proxy() as data:
    data['word'] = message.text
  await FSMAdd.next()
  await message.reply('tap translation')

@dp.message_handler(state=FSMAdd.translation)
async def load_translation(message: types.Message, state: FSMContext):
  print("load translation")
  async with state.proxy() as data:
    data['translation'] = message.text
  
  await sqlite_db.sql_add_command(message.from_user.id, state)
  await state.finish()

# repeat single
@dp.message_handler(commands = ['repeat'], state = None)
async def repeat_handler(message: types.Message, state:FSMContext):
  user_id = message.from_user.id
  dict = await sqlite_db.sql_read(user_id)
  len_dict = len(dict) 
  rand_pair = dict[random.randint(0, len(dict) - 1)][1:]
  await bot.send_message(user_id, f"Как перевести на английский {rand_pair[0]}?")
  
  async with state.proxy() as data:
    data['check_answer'] = rand_pair[1]

  await FSMRepeat.check_answer.set()

@dp.message_handler(state=FSMRepeat.check_answer)
async def check_answer_handler(message: types.Message, state: FSMRepeat):
  async with state.proxy() as data:
    correct_answer = data['check_answer']

  user_id = message.from_user.id
  user_answer = message.text
  if user_answer.lower() == correct_answer.lower():
    await bot.send_message(user_id, "Отлично, ты прав!")
  else:
    await bot.send_message(user_id, f"Ты неправ, друг =(\nПравильный ответ {correct_answer}")

  await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)
