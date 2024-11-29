from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import datetime
import os  # Para usar variáveis de ambiente
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Leia o token do bot e outras informações sensíveis das variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "C:/chromedriver/chromedriver.exe")
MATRICULA = os.getenv("MATRICULA")
SENHA = os.getenv("SENHA")
EMPRESA = os.getenv("EMPRESA", "1")  # Valor padrão como '1'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Olá! Eu sou o seu salvador. Bora bater o ponto, minha fia!')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

async def bater_ponto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Rodar o navegador em modo headless

    # Use o caminho fornecido pela variável de ambiente
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get('https://dok.pactosolucoes.com.br/dok/registrarPonto')

        # Aguarda e seleciona a empresa
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "codEmpresa")))
        Select(driver.find_element(By.NAME, 'codEmpresa')).select_by_value(EMPRESA)

        driver.find_element(By.ID, 'edtMatricula').send_keys(MATRICULA)
        senha_elemento = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ':nth-child(4) > .texto')))
        senha_elemento.send_keys(SENHA)

        # Supondo que o botão de registrar ponto possa ser selecionado dessa maneira
        botao_registrar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Registrar ponto')]")))
        botao_registrar.click()

        horario = datetime.datetime.now().strftime('%H:%M:%S')
        await update.message.reply_text(f'Ponto batido - {horario}')
    
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro ao tentar bater o ponto: {str(e)}")
    
    finally:
        driver.quit()

def main():
    # Certifique-se de que o token está definido
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN não está definido. Configure a variável de ambiente corretamente.")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("baterponto", bater_ponto))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()

if __name__ == '__main__':
    main()
