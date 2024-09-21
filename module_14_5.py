import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from crud_functions import initiate_products_db, initiate_users_db, get_all_products, add_user, is_included

initiate_products_db()
# Инициализация базы данных пользователей
initiate_users_db()

logging.basicConfig(level=logging.INFO)
API_TOKEN = '6439882866:AAHkrWNj7oQ7lFXPmKseM9X4GJ_G5x-LX64'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Состояния для регистрации
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

button_calculate = KeyboardButton('Рассчитать норму калорий')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')
button_register = KeyboardButton('Регистрация')  # Добавляем кнопку "Регистрация"

# Добавляем кнопки к клавиатуре
keyboard.add(button_calculate, button_info, button_buy, button_register)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, помогающий вашему здоровью!", reply_markup=keyboard)


# Функция для обработки нажатия кнопки 'Рассчитать норму калорий'
@dp.message_handler(lambda message: message.text == 'Рассчитать норму калорий')
async def calculate_calories(message: types.Message):
    await UserState.age.set()
    await message.reply("Введите свой возраст:")


# Функция для ввода роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    await UserState.growth.set()
    await message.reply("Введите свой рост (в см):")


# Функция для ввода веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = message.text
    await UserState.weight.set()
    await message.reply("Введите свой вес (в кг):")


# Функция для отправки нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = message.text
        age = int(data['age'])
        growth = int(data['growth'])
        weight = int(data['weight'])
        calories = (10 * weight) + (6.25 * growth) - (5 * age) + 5
        await message.reply(f"Ваша норма калорий составляет: {calories:.2f} Kcal")
    await state.finish()  # Завершаем состояние


# Функция для демонстрации продуктов
@dp.message_handler(lambda message: message.text == 'Купить')
async def show_products(message: types.Message):
    products = get_all_products()  # Получаем все продукты из базы данных
    for product in products:
        product_message = f"**{product['title']}**\nОписание: {product['description']}\nЦена: {product['price']}₽"
        await bot.send_photo(chat_id=message.chat.id, photo=open(product['photo'], 'rb'), caption=product_message)

    # После отображения продуктов создаем инлайн-клавиатуру
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for product in products:
        button_product = InlineKeyboardButton(product['title'], callback_data=f'buy_{product["id"]}')
        inline_keyboard.add(button_product)

    await message.reply("Выберите продукт для покупки:", reply_markup=inline_keyboard)


# Обработчик покупки продуктов
@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def buy_product(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.reply("Вы успешно приобрели продукт!")


# Функция для начала регистрации
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Привет! Чтобы зарегистрироваться, нажмите 'Регистрация'.")


@dp.message_handler(text='Регистрация')
async def sing_up(message: types.Message):
    await RegistrationState.username.set()  # Устанавливаем состояние username
    await message.answer("Введите имя пользователя (только латинский алфавит):")


# Функция для установки username
@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    # Проверьте, существует ли пользователь с таким именем в базе данных
    if not user_exists(username):  # user_exists - это ваша функция проверки
        await state.update_data(username=username)
        await RegistrationState.email.set()  # Переходим к следующему состоянию
        await message.answer("Введите свой email:")
    else:
        await message.answer("Пользователь существует, введите другое имя.")  # Ответ в случае существования пользователя
        return


# Функция для установки email
@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await RegistrationState.age.set()  # Переходим к следующему состоянию
    await message.answer("Введите свой возраст:")


# Функция для установки age и добавления пользователя в БД
@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    age = message.text
    user_data = await state.get_data()
    username = user_data['username']
    email = user_data['email']
    # Проверка, что возраст - это положительное число
    if age.isdigit() and int(age) > 0:
        # Добавляем пользователя в таблицу Users
        add_user(username=username, email=email, age=int(age))  # Убрали balance здесь, потому что он теперь в функции
        await state.finish()  # Завершаем прием состояний
        await message.answer("Вы успешно зарегистрированы!")
    else:
        await message.answer("Некорректный возраст. Пожалуйста, введите положительное число.")
        return

# Пример функции для проверки существования пользователя
def user_exists(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists


# Функция для добавления пользователя
def add_user(username, email, age):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
                   (username, email, age, 1000))  # Устанавливаем баланс по умолчанию на 1000
    conn.commit()
    conn.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
