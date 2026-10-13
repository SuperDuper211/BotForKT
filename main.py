import telebot
from telebot import types
import database as db
from datetime import datetime

bot = telebot.TeleBot('8564868205:AAHKJ1fzbhPnhhWNQbntV1HMNZVT-IXcB8s')

db.init_db()

user_survey = {}

@bot.message_handler(commands=['start'])
def start_commands(message):
    bot.send_message(message.chat.id, f'Привет! <u><em>{message.from_user.first_name}</em></u> \nВы можете обратиться к /help чтобы узнать список команд', parse_mode='html')

@bot.message_handler(commands=['help'])
def help_commands(message):
    help_text = (
        "Доступные команды:\n"
        "/start — Запуск бота\n"
        "/add — Записать данные за день\n"
        "/stats — Показать статистику\n"
        "/history — История записей\n"
        "/settings — Настройки уведомлений\n"
        "/clear — Очистить все данные\n"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['add'])
def add_commands(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("1 😞", callback_data="m1")
    btn2 = types.InlineKeyboardButton("2 😐", callback_data="m2")
    btn3 = types.InlineKeyboardButton("3 🙂", callback_data="m3")
    btn4 = types.InlineKeyboardButton("4 😊", callback_data="m4")
    btn5 = types.InlineKeyboardButton("5 🤩", callback_data="m5")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "Оцените ваше настроение сегодня от 1 до 5, где 1 — отвратительно, 5 — великолепно.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('m'))
def mood_callback(call):
    mood_val = call.data[1:]
    user_survey[call.message.chat.id] = {'mood': mood_val}
    bot.edit_message_text("Сколько часов вы потратили дела (на работу/учебу)?", call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, get_work)

def get_work(message):
    user_survey[message.chat.id]['work'] = message.text
    bot.send_message(message.chat.id, "Сколько часов вы спали?")
    bot.register_next_step_handler(message, get_sleep)

def get_sleep(message):
    user_survey[message.chat.id]['sleep'] = message.text
    bot.send_message(message.chat.id, "Добавьте комментарий (или напишите 'нет'):")
    bot.register_next_step_handler(message, save_all)

def save_all(message):
    uid = message.chat.id
    data = user_survey[uid]
    date_str = datetime.now().strftime("%d.%m.%Y")
    db.save_log(uid, data['mood'], data['work'], data['sleep'], message.text, date_str)
    bot.send_message(uid, "✅ Данные успешно записаны!")
    del user_survey[uid]

@bot.message_handler(commands=['stats'])
def stats_commands(message):
    logs = db.get_user_logs(message.chat.id)
    if not logs:
        bot.send_message(message.chat.id, "Статистика пуста. Сначала используйте /add.")
        return
    avg_mood = sum(int(log[0]) for log in logs) / len(logs)
    bot.send_message(message.chat.id, f"📊 Твоё среднее настроение: {avg_mood:.1f}\nВсего записей: {len(logs)}")

@bot.message_handler(commands=['history'])
def history_commands(message):
    logs = db.get_user_logs(message.chat.id)
    if not logs:
        bot.send_message(message.chat.id, "История пуста.")
        return
    history_text = "📜 Последние записи:\n"
    for log in logs[-5:]:
        history_text += f"📅 {log[4]} | Настроение: {log[0]} | Работа: {log[1]}ч | Сон: {log[2]}ч | Коммент: {log[3]}\n"
    bot.send_message(message.chat.id, history_text)

@bot.message_handler(commands=['settings'])
def settings_commands(message):
    bot.send_message(message.chat.id, "⚙️ Настройки: Здесь вы сможете изменить время напоминаний (в разработке).")

@bot.message_handler(commands=['clear'])
def clear_commands(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Да, удалить всё", callback_data="confirm_delete"))
    bot.send_message(message.chat.id, "⚠️ Вы уверены, что хотите очистить все данные?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_delete")
def confirm_delete_callback(call):
    db.delete_all(call.message.chat.id)
    bot.answer_callback_query(call.id, "Данные удалены")
    bot.edit_message_text("🗑️ Все данные успешно очищены.", call.message.chat.id, call.message.message_id)

bot.polling(non_stop=True)