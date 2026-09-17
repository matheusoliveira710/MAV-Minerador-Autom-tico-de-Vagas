"""
MAV — ETAPA 6.4: TESTE DE INTEGRAÇÃO DO DISCORD NOTIFIER
Valida o envio de embeds, regras de elegibilidade por classificação, 
resiliência a webhooks ausentes, tratamento de erros HTTP/timeout e proteção de segredos.
"""

import unittest
from unittest.mock import patch, MagicMock
import urllib.error
from models import Job
from matcher import JobMatcher, MatchResult
from discord_notifier import (
    is_job_eligible_for_notification,
    format_job_embed,
    send_job_to_discord
)


class TestDiscordNotifier(unittest.TestCase):

    def setUp(self):
        self.matcher = JobMatcher()
        
        self.sample_job = Job(
            title="Analista de Suporte Júnior",
            company="Tech Corp",
            location="Campinas - SP",
            link="https://apinfo.com/vaga/123",
            source="ApInfo",
            description_snippet="Suporte técnico, Windows 10 e Active Directory."
        )
        
        self.eligible_match = self.matcher.match(self.sample_job)
        
        self.discard_job = Job(
            title="Gerente Comercial Sênior",
            company="Vendas SA",
            location="Campinas - SP",
            link="https://apinfo.com/vaga/999",
            source="ApInfo",
            description_snippet="Gestão comercial e vendas B2B."
        )
        self.discard_match = self.matcher.match(self.discard_job)

        low_job = Job(
            title="Assistente",
            company="Empresa X",
            location="Campinas",
            link="",
            source="ApInfo",
            description_snippet="Outras tarefas"
        )
        self.low_match = self.matcher.match(low_job)

    def test_01_eligible_classifications(self):
        """TESTE 1, 2, 3 — Vagas relevantes, muito relevantes e excelentes são elegíveis."""
        for classif in ["RELEVANTE", "MUITO RELEVANTE", "EXCELENTE"]:
            # Utiliza o match real e sobrescreve apenas a classificação para o teste de elegibilidade
            res = self.matcher.match(self.sample_job)
            res.classification = classif
            self.assertTrue(is_job_eligible_for_notification(res))

    def test_02_non_eligible_classifications(self):
        """TESTE 4, 5 — Vagas descartadas ou de baixa relevância NÃO são elegíveis."""
        self.assertFalse(is_job_eligible_for_notification(self.discard_match))
        self.assertFalse(is_job_eligible_for_notification(self.low_match))

    def test_03_webhook_missing_handling(self):
        """TESTE 6 — Webhook ausente retorna False graciosamente sem quebrar o pipeline."""
        sent = send_job_to_discord(self.sample_job, self.eligible_match, webhook_url="")
        self.assertFalse(sent)

    @patch("urllib.request.urlopen")
    def test_04_successful_webhook_call(self, mock_urlopen):
        """TESTE 1 (Integração unitária) — Webhook chamado com sucesso para vaga relevante."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        sent = send_job_to_discord(self.sample_job, self.eligible_match, webhook_url="https://discord.com/api/webhooks/fake/token")
        self.assertTrue(sent)
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_05_http_error_handling(self, mock_urlopen):
        """TESTE 7 — Erro HTTP (ex: 400 Bad Request) é tratado de forma controlada."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://discord.com", code=400, msg="Bad Request", hdrs=None, fp=None
        )

        sent = send_job_to_discord(self.sample_job, self.eligible_match, webhook_url="https://discord.com/api/webhooks/fake/token")
        self.assertFalse(sent)

    @patch("urllib.request.urlopen")
    def test_06_timeout_handling(self, mock_urlopen):
        """TESTE 8 — Timeout de rede é tratado de forma controlada."""
        import socket
        mock_urlopen.side_effect = socket.timeout("timed out")

        sent = send_job_to_discord(self.sample_job, self.eligible_match, webhook_url="https://discord.com/api/webhooks/fake/token")
        self.assertFalse(sent)

    def test_07_discarded_job_not_sent(self):
        """TESTE 4 (Pipeline) — Vaga descartada não dispara requisição ao webhook."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            sent = send_job_to_discord(self.discard_job, self.discard_match, webhook_url="https://discord.com/api/webhooks/fake/token")
            self.assertFalse(sent)
            mock_urlopen.assert_not_called()

    def test_08_embed_payload_structure(self):
        """TESTE 9 — Payload do Embed contém todos os campos essenciais do Job."""
        payload = format_job_embed(self.sample_job, self.eligible_match)
        self.assertIn("embeds", payload)
        embed = payload["embeds"][0]
        self.assertIn("Analista de Suporte Júnior", embed["title"])
        
        field_names = [f["name"] for f in embed["fields"]]
        self.assertTrue(any("Empresa" in name for name in field_names))
        self.assertTrue(any("Score" in name for name in field_names))


if __name__ == "__main__":
    unittest.main()