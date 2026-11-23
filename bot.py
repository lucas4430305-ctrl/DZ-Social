
import os
import threading
import logging

from flask import Flask
from waitress import serve

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

web = Flask(__name__)


@web.route("/")
def home():
    return "DZ STORE está online!", 200


def menu_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛍️ Catálogo", callback_data="catalogo"),
            InlineKeyboardButton("👤 Meu perfil", callback_data="perfil")
        ],
        [
            InlineKeyboardButton("💰 Adicionar saldo", callback_data="saldo"),
            InlineKeyboardButton("📞 Suporte", callback_data="suporte")
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 BEM-VINDO À DZ STORE!\n\n"
        "Sua loja de produtos digitais.\n\n"
        "Escolha uma opção abaixo:",
        reply_markup=menu_principal()
    )


async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "inicio":
        await query.edit_message_text(
            "🟢 DZ STORE\n\nEscolha uma opção:",
            reply_markup=menu_principal()
        )

    elif query.data == "catalogo":
        teclado = [
            [InlineKeyboardButton("📘 E-books — Em breve", callback_data="indisponivel")],
            [InlineKeyboardButton("🎨 Artes digitais — Em breve", callback_data="indisponivel")],
            [InlineKeyboardButton("📱 Templates — Em breve", callback_data="indisponivel")],
            [InlineKeyboardButton("📦 Outros produtos — Em breve", callback_data="indisponivel")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
        ]

        await query.edit_message_text(
            "🛍️ CATÁLOGO DZ STORE\n\n"
            "Confira nossos produtos digitais.\n"
            "Novos produtos serão adicionados em breve.",
            reply_markup=InlineKeyboardMarkup(teclado)
        )

    elif query.data == "perfil":
        usuario = query.from_user

        await query.edit_message_text(
            "👤 MEU PERFIL\n\n"
            f"Nome: {usuario.first_name}\n"
            f"ID: {usuario.id}\n\n"
            "Saldo: R$ 0,00\n"
            "Compras: 0",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
            ])
        )

    elif query.data == "saldo":
        await query.edit_message_text(
            "💰 ADICIONAR SALDO\n\n"
            "A integração Pix será configurada em uma próxima etapa.\n"
            "Esta versão ainda não recebe pagamentos.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
            ])
        )

    elif query.data == "suporte":
        await query.edit_message_text(
            "📞 SUPORTE DZ STORE\n\n"
            "Nosso atendimento será disponibilizado em breve.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
            ])
        )

    elif query.data == "indisponivel":
        await query.answer(
            "Este produto ainda não está disponível.",
            show_alert=True
        )


def iniciar_bot():
    if not TOKEN:
        raise RuntimeError("A variável TELEGRAM_BOT_TOKEN não foi configurada.")

    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(botoes))

    logging.info("DZ STORE iniciado!")
    bot.run_polling(stop_signals=None)


if __name__ == "__main__":
    threading.Thread(
        target=iniciar_bot,
        daemon=True
    ).start()

    porta = int(os.environ.get("PORT", 10000))
    serve(web, host="0.0.0.0", port=porta)
