import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "9282894396:AAEcmtS-MnO4ifchzaiosnHWafW8L-mLLGQ"

if not TOKEN or TOKEN == "BU_YERGA_BOTFATHER_TOKEN":
    raise ValueError("BotFather tokenini kiriting!")

bot = telebot.TeleBot(TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

menu = {
    "palov": {
        "name": "O'zbek palovi",
        "price": 70000,
        "info": "Guruch, mol go'shti, sabzi, piyoz, yog'.",
        "image": "palov.jpg"
    },
    "manti": {
        "name": "Uy mantisi",
        "price": 65000,
        "info": "Xamir, mol go'shti, piyoz, ziravorlar.",
        "image": "manti.jpg"
    },
    "shashlik": {
        "name": "Mol go'shtli shashlik",
        "price": 45000,
        "info": "Mol go'shti, piyoz, ziravorlar.",
        "image": "shashlik.jpg"
    },
    "somsa": {
        "name": "Go'shtli somsa",
        "price": 18000,
        "info": "Xamir, go'sht, piyoz, ziravorlar.",
        "image": None
    },
    "salat": {
        "name": "Achichuk salati",
        "price": 15000,
        "info": "Pomidor, piyoz, bodring, ko'katlar.",
        "image": None
    },
    "choy": {
        "name": "Ko'k choy",
        "price": 5000,
        "info": "Ko'k choy.",
        "image": None
    }
}

carts = {}
states = {}

def money(value):
    return f"{value:,}".replace(",", " ") + " so'm"

def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🍽 Menyu", callback_data="menu"))
    keyboard.add(InlineKeyboardButton("🛒 Savatim", callback_data="cart"))
    keyboard.add(InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about"))
    return keyboard

def show_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    for key, item in menu.items():
        keyboard.add(
            InlineKeyboardButton(
                f"{item['name']} — {money(item['price'])}",
                callback_data="item_" + key
            )
        )
    keyboard.add(InlineKeyboardButton("🛒 Savatim", callback_data="cart"))
    bot.send_message(chat_id, "🍽 Bizning menyu:", reply_markup=keyboard)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! ZakazPro botiga xush kelibsiz!\n\n"
        "👨‍💻 Разработчик: Холбоев Норбек\n"
        "🎓 Студент IT-направления",
        reply_markup=main_menu()
    )
@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu_handler(call):
    bot.answer_callback_query(call.id)
    show_menu(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_handler(call):
    bot.answer_callback_query(call.id)
    key = call.data.replace("item_", "", 1)
    item = menu.get(key)

    if not item:
        return

    text = (
        f"🍴 {item['name']}\n"
        f"💰 Narxi: {money(item['price'])}\n"
        f"🥘 Tarkibi: {item['info']}"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "➕ Savatga qo'shish",
            callback_data="add_" + key
        )
    )
    keyboard.add(InlineKeyboardButton("⬅️ Menyu", callback_data="menu"))

    image = item["image"]
    image_path = os.path.join(IMAGE_DIR, image) if image else None

    if image_path and os.path.isfile(image_path):
        with open(image_path, "rb") as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=text,
                reply_markup=keyboard
            )
    else:
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboard
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_handler(call):
    bot.answer_callback_query(call.id, "Savatga qo'shildi!")
    key = call.data.replace("add_", "", 1)
    user_id = call.from_user.id

    if key not in menu:
        return

    if user_id not in carts:
        carts[user_id] = {}

    carts[user_id][key] = carts[user_id].get(key, 0) + 1
    bot.send_message(
        call.message.chat.id,
        menu[key]["name"] + " savatga qo'shildi."
    )

    @bot.callback_query_handler(func=lambda call: call.data == "cart")
    def cart_handler(call):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        cart = carts.get(user_id, {})

        if not cart:
            bot.send_message(call.message.chat.id, "Savatingiz hozircha bo'sh.")
            return

        total = 0
        text = "🛒 Sizning savatingiz:\n\n"

        for key, quantity in cart.items():
            item = menu[key]
            price = item["price"] * quantity
            total += price
            text += f"{item['name']} x {quantity} = {money(price)}\n"

        text += f"\n💰 Jami: {money(total)}"

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✅ Buyurtma berish", callback_data="checkout"))
        keyboard.add(InlineKeyboardButton("🗑 Savatni tozalash", callback_data="clear"))
        keyboard.add(InlineKeyboardButton("⬅️ Menyu", callback_data="menu"))

        bot.send_message(call.message.chat.id, text, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == "clear")
    def clear_handler(call):
        bot.answer_callback_query(call.id)
        carts.pop(call.from_user.id, None)
        bot.send_message(call.message.chat.id, "Savat tozalandi.")

    @bot.callback_query_handler(func=lambda call: call.data == "checkout")
    def checkout_handler(call):
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id

        if not carts.get(user_id):
            bot.send_message(call.message.chat.id, "Savat bo'sh!")
            return

        states[user_id] = "phone"
        bot.send_message(
            call.message.chat.id,
            "📞 Telefon raqamingizni yuboring:"
        )

    @bot.message_handler(func=lambda message: states.get(message.from_user.id) == "phone")
    def phone_handler(message):
        user_id = message.from_user.id
        phone = message.text.strip()

        if len(phone) < 7:
            bot.send_message(message.chat.id, "Telefon raqamni qayta kiriting:")
            return

        states[user_id] = {"step": "address", "phone": phone}
        bot.send_message(message.chat.id, "📍 Yetkazib berish manzilini yozing:")

    @bot.message_handler(func=lambda message: isinstance(states.get(message.from_user.id), dict))
    def address_handler(message):
        user_id = message.from_user.id
        address = message.text.strip()

        if len(address) < 5:
            bot.send_message(message.chat.id, "Manzilni to'liqroq yozing:")
            return

        state = states[user_id]
        cart = carts.get(user_id, {})
        total = sum(menu[key]["price"] * qty for key, qty in cart.items())

        order = "🆕 Yangi buyurtma!\n\n"
        for key, qty in cart.items():
            order += f"{menu[key]['name']} x {qty}\n"

        order += (
            f"\nJami: {money(total)}"
            f"\nTelefon: {state['phone']}"
            f"\nManzil: {address}"
        )

        bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi!\n" + order)
        carts.pop(user_id, None)
        states.pop(user_id, None)

    @bot.callback_query_handler(func=lambda call: call.data == "about")
    def about_handler(call):
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "ZakazPro — taomlarni onlayn buyurtma qilish boti."
        )

if __name__ == "__main__":
    print("ZakazPro ishga tushmoqda...")
    try:
        info = bot.get_me()
        print("Bot ulandi:", info.username)
        print("Telegram'da /start yuboring.")
        bot.infinity_polling(
            skip_pending=True,
            timeout=30,
            long_polling_timeout=30
        )
    except Exception as error:
        print("Xato:", error)


