
import os
import json
import logging
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

ARQUIVO = Path("produtos.json")

NOME, PRECO, MIDIA = range(3)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def carregar_produtos():
    if not ARQUIVO.exists():
        return []

    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def salvar_produtos(produtos):
    ARQUIVO.write_text(
        json.dumps(produtos, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def sou_admin(user_id):
    return ADMIN_ID and str(user_id) == str(ADMIN_ID)


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Ver catálogo", callback_data="catalogo")],
        [InlineKeyboardButton("👤 Meu perfil", callback_data="perfil")],
        [InlineKeyboardButton("📞 Suporte", callback_data="suporte")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔴 DZ STORE +18\n\n"
        "Bem-vindo à nossa loja de conteúdos exclusivos!\n\n"
        "Escolha uma opção:",
        reply_markup=menu()
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sou_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Acesso não autorizado.")
        return

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Cadastrar conteúdo", callback_data="cadastrar")],
        [InlineKeyboardButton("📦 Ver produtos cadastrados", callback_data="admin_lista")]
    ])

    await update.message.reply_text(
        "⚙️ PAINEL ADMINISTRATIVO\n\n"
        "Gerencie os conteúdos da DZ STORE:",
        reply_markup=teclado
    )


async def iniciar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not sou_admin(query.from_user.id):
        return ConversationHandler.END

    await query.message.reply_text("📝 Digite o nome do conteúdo:")
    return NOME


async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text.strip()

    if len(nome) < 2 or len(nome) > 80:
        await update.message.reply_text("Digite um nome entre 2 e 80 caracteres.")
        return NOME

    context.user_data["novo_produto"] = {"nome": nome}

    await update.message.reply_text(
        "💰 Agora informe o preço em reais.\n"
        "Exemplo: 25.00"
    )
    return PRECO


async def receber_preco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        preco = float(update.message.text.replace(",", "."))
        if not 0.01 <= preco <= 10000:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Preço inválido. Digite um valor entre R$ 0,01 e R$ 10.000."
        )
        return PRECO

    context.user_data["novo_produto"]["preco"] = round(preco, 2)

    await update.message.reply_text(
        "📸 Envie agora a foto ou o vídeo do conteúdo.\n\n"
        "O arquivo será usado na entrega após a confirmação da compra."
    )
    return MIDIA


async def receber_midia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message

    if mensagem.photo:
        tipo = "foto"
        arquivo_id = mensagem.photo[-1].file_id
    elif mensagem.video:
        tipo = "video"
        arquivo_id = mensagem.video.file_id
    else:
        await mensagem.reply_text("Envie uma foto ou um vídeo, por favor.")
        return MIDIA

    produto = context.user_data.pop("novo_produto", {})
    produtos = carregar_produtos()

    novo_id = max([p.get("id", 0) for p in produtos], default=0) + 1

    produto.update({
        "id": novo_id,
        "tipo": tipo,
        "arquivo_id": arquivo_id
    })

    produtos.append(produto)
    salvar_produtos(produtos)

    await mensagem.reply_text(
        f"✅ Produto cadastrado!\n\n"
        f"Nome: {produto['nome']}\n"
        f"Preço: R$ {produto['preco']:.2f}\n"
        f"ID: {novo_id}"
    )

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("novo_produto", None)
    await update.message.reply_text("Cadastro cancelado.")
    return ConversationHandler.END


async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalogo":
        produtos = carregar_produtos()

        if not produtos:
            await query.message.reply_text(
                "🛍️ Nosso catálogo está sendo preparado. Volte em breve!"
            )
            return

        for p in produtos:
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🔎 Ver detalhes",
                    callback_data=f"produto:{p['id']}"
                )]
            ])

            texto = (
                f"🔎 Produto {p['id']}\n\n"
                f"✨ {p['nome']}\n\n"
                f"💵 Preço: R$ {p['preco']:.2f}\n"
                f"🔒 Conteúdo exclusivo"
            )

            await query.message.reply_text(texto, reply_markup=teclado)

    elif query.data.startswith("produto:"):
        produto_id = int(query.data.split(":")[1])
        produtos = carregar_produtos()
        produto = next(
            (p for p in produtos if p["id"] == produto_id),
            None
        )

        if not produto:
            await query.message.reply_text("Produto não encontrado.")
            return

        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🛒 Comprar",
                callback_data=f"comprar:{produto_id}"
            )],
            [InlineKeyboardButton("⬅️ Catálogo", callback_data="catalogo")]
        ])

        await query.message.reply_text(
            f"✨ DETALHES DO CONTEÚDO\n\n"
            f"Produto: {produto['nome']}\n"
            f"Formato: {produto['tipo'].upper()}\n"
            f"Preço: R$ {produto['preco']:.2f}\n\n"
            f"🔐 Arquivo protegido até a confirmação do pagamento.",
            reply_markup=teclado
        )

    elif query.data.startswith("comprar:"):
        await query.message.reply_text(
            "💳 O pagamento ainda não está configurado.\n\n"
            "Nenhuma cobrança foi realizada. Em breve você poderá comprar "
            "com segurança."
        )

    elif query.data == "perfil":
        await query.message.reply_text(
            f"👤 MEU PERFIL\n\n"
            f"Nome: {query.from_user.first_name}\n"
            f"ID: {query.from_user.id}"
        )

    elif query.data == "suporte":
        await query.message.reply_text(
            "📞 SUPORTE DZ STORE\n\nEntre em contato com o administrador."
        )

    elif query.data == "admin_lista":
        if not sou_admin(query.from_user.id):
            return

        produtos = carregar_produtos()

        if not produtos:
            await query.message.reply_text("Nenhum produto cadastrado.")
            return

        texto = "📦 PRODUTOS CADASTRADOS\n\n"
        for p in produtos:
            texto += (
                f"ID: {p['id']}\n"
                f"Nome: {p['nome']}\n"
                f"Preço: R$ {p['preco']:.2f}\n\n"
            )

        await query.message.reply_text(texto)


def main():
    if not TOKEN:
        raise RuntimeError("Configure TELEGRAM_BOT_TOKEN.")

    if not ADMIN_ID:
        raise RuntimeError("Configure ADMIN_ID.")

    app = Application.builder().token(TOKEN).build()

    cadastro = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            iniciar_cadastro,
            pattern="^cadastrar$"
        )],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            PRECO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_preco)],
            MIDIA: [MessageHandler(
                filters.PHOTO | filters.VIDEO,
                receber_midia
            )]
        },
        fallbacks=[CommandHandler("cancelar", cancelar)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(cadastro)
    app.add_handler(CallbackQueryHandler(botoes))

    logging.info("DZ STORE iniciado!")
    app.run_polling()


if __name__ == "__main__":
    main()
