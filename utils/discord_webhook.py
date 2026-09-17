import requests
from utils.logger import setup_logger
from config import DISCORD_WEBHOOK_URL

class DiscordWebhook:
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
        self.logger = setup_logger('discord')
        
    def send_jobs(self, jobs, platform_name):
        """Envia vagas formatadas para o Discord"""
        if not jobs:
            return
            
        try:
            # Agrupa por plataforma
            message = f"**🚀 NOVAS VAGAS - {platform_name.upper()}**\n\n"
            
            for job in jobs[:10]:  # Limita a 10 por mensagem
                message += f"**{job['title']}**\n"
                message += f"🏢 {job['company']}\n"
                message += f"📍 {job['location']}\n"
                message += f"🔗 {job['link']}\n"
                if job.get('description'):
                    message += f"📝 {job['description'][:200]}...\n"
                message += "\n" + "-"*30 + "\n\n"
            
            # Divide mensagens grandes
            if len(message) > 2000:
                # Divide em chunks
                chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
                for chunk in chunks:
                    payload = {'content': chunk}
                    response = requests.post(self.webhook_url, json=payload)
                    response.raise_for_status()
            else:
                payload = {'content': message}
                response = requests.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
            self.logger.info(f"Sent {len(jobs)} jobs to Discord")
            
        except Exception as e:
            self.logger.error(f"Error sending to Discord: {e}")
            
    def send_summary(self, results):
        """Envia resumo da execução"""
        try:
            message = "**📊 RESUMO DA EXECUÇÃO**\n\n"
            total = 0
            for platform, jobs in results.items():
                count = len(jobs)
                total += count
                message += f"✅ {platform}: {count} vagas\n"
            
            message += f"\n**Total: {total} vagas encontradas**"
            
            payload = {'content': message}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Error sending summary: {e}")
