import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from crud_functions import initiate_db, get_all_products

# Инициализация базы данных и создание таблицы
initiate_db()

# Получение всех продуктов
products = get_all_products()
print(products)

logging.basicConfig(level=logging.INFO)

API_TOKEN = '6439882866:AAHkrWNj7oQ7lFXPmKseM9X4GJ_G5x-LX64'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний для FSM
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать норму калорий')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')  # Кнопка "Купить"
keyboard.add(button_calculate, button_info, button_buy)

# Inline клавиатура
inline_keyboard = InlineKeyboardMarkup(row_width=2)
button_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton('Формулы расчета', callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, помогающий вашему здоровью!", reply_markup=keyboard)


# Функция главного меню
@dp.message_handler(lambda message: message.text == 'Рассчитать норму калорий')
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_keyboard)


# Функция для показа формул расчета
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)  # Убираем индикатор загрузки
    formula_message = (
        "Формула расчёта нормы калорий по Миффлину - Сан Жеору:\n"
        "Для мужчин: Kcal = (10 × Вес) + (6.25 × Рост) - (5 × Возраст) + 5\n"
        "Для женщин: Kcal = (10 × Вес) + (6.25 × Рост) - (5 × Возраст) - 161"
    )
    await call.message.reply(formula_message)


# Функция для запуска механизма расчета калорий
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)  # Убираем индикатор загрузки
    await UserState.age.set()
    await call.message.reply("Введите свой возраст:")


# Функция для ввода роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text  # Сохраняем возраст
    await UserState.growth.set()
    await message.reply("Введите свой рост (в см):")


# Функция для ввода веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = message.text  # Сохраняем рост
    await UserState.weight.set()
    await message.reply("Введите свой вес (в кг):")


# Функция для отправки нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = message.text  # Сохраняем вес

        # Используем формулу Миффлина - Сан Жеора (для мужчин)
        age = int(data['age'])
        growth = int(data['growth'])
        weight = int(data['weight'])
        # Формула для мужчин
        calories = 10 * weight + 6.25 * growth - 5 * age + 5
        await message.reply(f"Ваша норма калорий: {calories} ккал.")
    await state.finish()  # Завершение состояния

@dp.message_handler(lambda message: message.text == 'Купить')
async def get_buying_list(message: types.Message):
    for index, product in enumerate(products):
        await message.answer(
            f'Название: {product["title"]} | Описание: {product["description"]} | Цена: {product["price"]} руб.'
        )
        try:
            with open(product["photo"], 'rb') as photo:
                await bot.send_photo(message.chat.id, photo)  # Отправка фото продукта
        except FileNotFoundError:
            await message.answer(f"Извините, фото для {product['title']} не найдено.")

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)

# Создание Inline клавиатуры для продуктов
inline_keyboard = InlineKeyboardMarkup(row_width=2)
button_product1 = InlineKeyboardButton('Product1', callback_data="product_buying")
button_product2 = InlineKeyboardButton('Product2', callback_data="product_buying")
button_product3 = InlineKeyboardButton('Product3', callback_data="product_buying")
button_product4 = InlineKeyboardButton('Product4', callback_data="product_buying")
inline_keyboard.add(button_product1, button_product2, button_product3, button_product4)

# Callback хэндлер для покупки продукта
@dp.callback_query_handler(lambda call: call.data == "product_buying")
async def send_confirm_message(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)  # Убираем индикатор загрузки
    await call.message.answer("Вы успешно приобрели продукт!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
