import requests
import asyncio
from telegram import Bot
import schedule
import time
from collections import Counter

# Token do seu bot do Telegram
TOKEN = '5771524262:AAEChBPjF1eJL-BUyKbLWQFyCGFwqoAtdWs'
# Chat ID do seu grupo do Telegram
CHAT_ID = -1002019610496
# URL da API
API_URL = 'https://br.betano.com/api/virtuals/resultsdata/?leagueId=199330&req=la,s,stnf,c,mb,mbl'

# Lista para armazenar os resultados de Ambas equipes Marcam (SIM ou NÃO) dos últimos 5 jogos
ambas_equipes_marcam_list = []

async def get_results():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(API_URL, headers=headers))
        response.raise_for_status()  # Lança um erro se a resposta não for bem-sucedida (código 200)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Erro ao obter os resultados da API:", e)
        return None
    except Exception as e:
        print("Ocorreu um erro inesperado:", e)
        return None

async def send_telegram_message(message):
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print("Erro ao enviar mensagem para o Telegram:", e)

def analyze_ambas_equipes_marcam(results):
    # Realizar a análise de distribuição de frequência
    counter = Counter(results)
    print("Análise de Distribuição de Frequência:")
    for outcome, frequency in counter.items():
        print(f"{outcome}: {frequency} vezes")
    # Verificar se há um padrão
    if 'SIM' in counter and counter['SIM'] == 5:
        return True
    elif 'NÃO' in counter and counter['NÃO'] == 5:
        return False
    else:
        return None

async def job():
    results = await get_results()
    if results:
        ambas_equipes_marcam_results = []  # Lista para armazenar os resultados de Ambas equipes Marcam
        for league in results['data']['results']:
            for event in league['events']:
                for market in event['markets']:
                    if market['name'] == 'Ambas equipes Marcam':
                        for selection in market['selections']:
                            outcome = selection['name']
                            ambas_equipes_marcam_results.append(outcome)
        # Analisar resultados dos últimos 5 jogos
        if len(ambas_equipes_marcam_results) >= 5:
            pattern_found = analyze_ambas_equipes_marcam(ambas_equipes_marcam_results[-5:])
            if pattern_found is not None:
                await send_telegram_message(f"Padrão identificado nos últimos 5 jogos: Ambas equipes marcam: {pattern_found}")
    else:
        print("Houve um problema ao obter os resultados da API.")

# Agendar a execução do job a cada 10 segundos
schedule.every(10).seconds.do(lambda: asyncio.run(job()))

# Loop para manter o script em execução
while True:
    schedule.run_pending()
    time.sleep(1)
  
