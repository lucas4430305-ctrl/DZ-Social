
import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

PRODUTOS = [
    ("📘 E-book", "Em breve"),
    ("🎨 Artes digitais", "Em breve"),
    ("📱 Templates", "Em breve"),
    ("📦 Outros produtos", "Em breve")
]


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
    mensagem = (
        "🟢 BEM-VINDO À DZ STORE!\n\n"
        "Sua loja de produtos digitais.\n\n"
        "Escolha uma opção abaixo para continuar:"
    )

    await update.message.reply_text(
        mensagem,
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
            [InlineKeyboardButton(
                f"{nome} — {preco}",
                callback_data="indisponivel"
            )]
            for nome, preco in PRODUTOS
        ]
        teclado.append([
            InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")
        ])

        await query.edit_message_text(
            "🛍️ CATÁLOGO DZ STORE\n\n"
            "Confira nossos produtos digitais:\n\n"
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
            "O sistema de recarga via Pix será integrado "
            "após configurarmos o provedor de pagamento.\n\n"
            "Nenhum pagamento é solicitado nesta versão.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
            ])
        )

    elif query.data == "suporte":
        await query.edit_message_text(
            "📞 SUPORTE DZ STORE\n\n"
            "Em breve disponibilizaremos nosso canal de atendimento.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Voltar", callback_data="inicio")]
            ])
        )

    elif query.data == "indisponivel":
        await query.answer(
            "Este produto ainda não está disponível.",
            show_alert=True
        )


def main():
    if not TOKEN:
        raise RuntimeError("Configure a variável TELEGRAM_BOT_TOKEN.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botoes))

    print("DZ STORE iniciado!")
    app.run_polling()


if __name__ == "__main__":
    main()
