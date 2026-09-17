MAV — MINERADOR AUTOMÁTICO DE VAGAS
STATUS DO PROJETO — O QUE JÁ FUNCIONA E O QUE AINDA FALTA
Data do levantamento: 29/08/2026


=================================================================
1. OBJETIVO DO PROJETO
=================================================================

O MAV (Minerador Automático de Vagas) foi criado para:

- Acessar plataformas de vagas automaticamente.
- Coletar vagas de tecnologia e infraestrutura.
- Comparar cada vaga com o perfil profissional/currículo do Matheus.
- Atribuir uma pontuação de compatibilidade.
- Descartar vagas fora do perfil.
- Evitar processar a mesma vaga novamente.
- Enviar ao Discord somente vagas consideradas elegíveis.
- Rodar automaticamente em horários definidos pelo scheduler.


=================================================================
2. ESTRUTURA ATUAL DO PROJETO
=================================================================

minerador_vagas/
|
|-- config.py
|-- models.py
|-- browser_utils.py
|-- discord_notifier.py
|-- matcher.py
|-- profile.py
|-- main.py
|-- scheduler.py
|-- requirements.txt
|-- .env
|
|-- scrapers/
|   |-- apinfo.py
|
|-- data/
|   |-- seen_jobs.json
|   |-- scheduler_state.json       (usado pelo scheduler)
|
|-- logs/
|   |-- scheduler.log              (usado pelo scheduler)
|
|-- tests/
|   |-- testes existentes
|
|-- utils/
|
=================================================================


3. O QUE JÁ ESTÁ FUNCIONANDO CORRETAMENTE
=================================================================

3.1. AMBIENTE PYTHON

STATUS: FUNCIONANDO

- Projeto roda dentro de .venv.
- Python 3.12 está sendo utilizado.
- Os módulos principais são importados corretamente.
- main.py está sendo executado diretamente pelo PowerShell.


3.2. PLAYWRIGHT / NAVEGAÇÃO

STATUS: FUNCIONANDO

O MAV consegue abrir o navegador e acessar o APInfo.

Foi validado:

URL:
https://www.apinfo.com/apinfo/inc/list4.cfm

O scraper encontra corretamente o container:

#vagas .box-vagas.linha.pd

Nos testes realizados foram encontradas 8 vagas.


3.3. SCRAPER DO APINFO

STATUS: FUNCIONANDO

O scraper do APInfo está conseguindo:

- Acessar a página de pesquisa.
- Localizar os cards.
- Extrair título.
- Extrair empresa.
- Extrair localização.
- Extrair link.
- Identificar o código da vaga (codvaga).
- Exibir as vagas encontradas no terminal.

Exemplo real obtido:

Analista de Redes Mainframe IBM SR
Empresa: SPASSU
Local: Brasília - DF
Código: 85913

O scraper está estável nos testes realizados.


3.4. MODELO Job

STATUS: FUNCIONANDO

models.py possui a estrutura Job com:

- title
- company
- location
- link
- source
- description_snippet
- matched_categories
- score

Também existe normalize(), que:

- remove espaços extras;
- trata valores vazios;
- mantém caracteres UTF-8;
- retorna um Job normalizado.


3.5. IDENTIFICADOR ESTÁVEL DA VAGA NO APINFO

STATUS: FUNCIONANDO

Foi identificado e corrigido um problema importante.

O APInfo altera o parâmetro pkey do link.

Portanto:

LINK A:
...?codvaga=85913&pkey=ABC123

LINK B:
...?codvaga=85913&pkey=XYZ789

representam a mesma vaga.

A versão corrigida de models.py utiliza o codvaga para criar um ID estável no APInfo.

Exemplo:

APInfo:85913

é convertido em SHA-256.

Isso foi validado no PowerShell: links diferentes com o mesmo codvaga produziram o mesmo unique_id.

Essa correção é FUNDAMENTAL para a deduplicação.


3.6. DEDUPLICAÇÃO

STATUS: FUNCIONANDO

O arquivo:

data/seen_jobs.json

está sendo utilizado para armazenar as vagas já processadas.

Teste realizado:

Primeira execução:
- 8 vagas coletadas
- 8 vagas novas

Segunda execução:
- 8 vagas coletadas
- 8 vagas já processadas
- 0 vagas novas

Resultado observado:

[DEDUP] Já processada: Operador de Vendas e Serviço de Campo
[DEDUP] Já processada: ...
[DEDUP] Já processada: Analista de Redes Mainframe IBM SR

Depois:

[DEDUP] Já processadas: 8
[DEDUP] Novas vagas: 0

Portanto, a deduplicação está funcionando.


3.7. MATCHER

STATUS: FUNCIONANDO, MAS PRECISA DE REFINAMENTO

O matcher já:

- carrega o profile.py;
- normaliza texto;
- remove acentos para comparação;
- procura cargos;
- procura competências;
- calcula score;
- gera classificação;
- diferencia vagas mais e menos compatíveis.

Nos testes:

Analista de Redes Mainframe IBM SR
Score: 76.5
Classificação: MUITO RELEVANTE

Analista de Segurança da Informação
Score: 48.5
Classificação: MODERADA

Operador de Vendas
Score: 0.0
Classificação: DESCARTAR


3.8. PERFIL PROFISSIONAL

STATUS: IMPLEMENTADO

O arquivo profile.py foi criado especificamente para representar o currículo/perfil profissional.

O perfil possui como cargos principais:

- Analista de Suporte Júnior
- Analista de Suporte
- Suporte de TI
- Infraestrutura de TI

Cargos secundários:

- Service Desk
- Desenvolvedor Júnior

Áreas principais:

- Suporte de TI
- Infraestrutura de TI
- Service Desk
- Redes
- Sistemas

Áreas secundárias:

- Desenvolvimento
- Automação
- Cloud Computing
- Virtualização

Também existem competências técnicas relacionadas a:

- suporte técnico;
- Windows;
- Linux;
- Ubuntu;
- redes TCP/IP;
- Active Directory;
- hardware;
- Microsoft 365;
- acesso remoto;
- servidores;
- backup;
- automação;
- Ansible;
- virtualização;
- Python;
- SQL;
- JavaScript.


3.9. CONFIGURAÇÃO DE PALAVRAS-CHAVE

STATUS: IMPLEMENTADO

config.py possui categorias baseadas no perfil:

- Suporte
- Infraestrutura
- Sistemas
- Microsoft / AD
- Redes
- Hardware
- Servidores
- Backup
- Automação / DevOps
- Desenvolvimento

Também existem pesos diferentes por categoria.

Exemplos:

Suporte = 5
Infraestrutura = 5
Redes = 4
Sistemas = 4
Microsoft / AD = 4
Servidores = 4
Hardware = 3
Backup = 3
Automação / DevOps = 3
Desenvolvimento = 1


3.10. TERMOS DE EXCLUSÃO

STATUS: IMPLEMENTADO

Já existem exclusões para cargos claramente acima do perfil atual, como:

- Gerente de TI
- Gerente de Tecnologia
- Coordenador de TI
- Coordenador de Infraestrutura
- Diretor de TI
- Diretor de Tecnologia
- Tech Lead
- Staff Engineer
- Principal Engineer
- Arquiteto de Software

Esses termos podem impedir uma vaga de ser considerada.


3.11. NOTIFICAÇÃO NO DISCORD

STATUS: FUNCIONANDO

O webhook do Discord foi testado com sucesso.

No teste real:

Analista de Redes Mainframe IBM SR
Score: 76.5
Classificação: MUITO RELEVANTE

Resultado:

[DISCORD] ✓ Webhook enviado com sucesso.

Também está funcionando o bloqueio das vagas abaixo do nível necessário.

Exemplo:

Analista de Segurança da Informação
Score: 48.5
Classificação: MODERADA

Resultado:

[DISCORD] ✗ Não elegível para notificação.


3.12. DRY-RUN

STATUS: FUNCIONANDO

O comando:

python main.py --site ApInfo --dry-run --headed

funciona.

No modo dry-run:

- o scraper executa;
- o matcher executa;
- a deduplicação executa;
- a elegibilidade é calculada;
- o webhook NÃO é chamado.

Foi validado no terminal:

✓ Elegível — DRY-RUN. Webhook não será chamado.


3.13. EXECUÇÃO NORMAL

STATUS: FUNCIONANDO

O comando:

python main.py --site ApInfo --headed

foi executado com sucesso.

Resultado do teste:

Vagas coletadas: 8
Vagas analisadas: 8
Vagas novas: 8
Enviadas ao Discord: 1
Bloqueadas pelo notifier: 7
Falhas de envio: 0

O banco de deduplicação também foi atualizado.


=================================================================
4. O PRINCIPAL PROBLEMA ATUAL
=================================================================

STATUS: PRECISA SER CORRIGIDO

O sistema já possui um profile.py baseado no currículo, MAS o filtro ainda está permissivo demais.

Isso foi comprovado pelo teste.

Exemplos:

Analista de Segurança da Informação
Score: 48.5
Classificação: MODERADA

Essa vaga pode ter alguma relação técnica com o perfil, mas não é necessariamente uma vaga-alvo principal.

Outro exemplo:

Scrum Master Sênior
Score: 0.0
Classificação: DESCARTAR
Cargos reconhecidos: devops

Mesmo descartada, o matcher reconheceu "devops" como cargo/área, mostrando que termos técnicos isolados ainda podem influenciar a análise.

Também houve:

Técnico Instalador de CFTV
Score: 19.5
Classificação: DESCARTAR
Core Skill: rede

Isso mostra claramente o problema:

A palavra "rede" sozinha pode aparecer em uma vaga que NÃO é de redes/infraestrutura de TI.

Portanto, o sistema precisa deixar de considerar palavras técnicas isoladas como evidência forte de compatibilidade.


=================================================================
5. O QUE PRECISA SER FEITO NO FILTRO
=================================================================

PRIORIDADE: ALTA

O objetivo deve ser:

"Não quero simplesmente vagas que contenham alguma tecnologia que aparece no meu currículo.
Quero vagas que sejam compatíveis com o meu perfil profissional."

A lógica precisa passar a priorizar:

1. Cargo compatível.
2. Área profissional compatível.
3. Atividades compatíveis.
4. Competências compatíveis.
5. Nível profissional compatível.

E somente depois considerar tecnologias.


=================================================================
6. COMO O FILTRO DEVE FUNCIONAR
=================================================================

O ideal é separar a análise em camadas.

CAMADA 1 — CARGO

Maior peso.

Exemplos fortes:

- Analista de Suporte Júnior
- Analista de Suporte
- Suporte Técnico
- Técnico de Suporte
- Analista de Infraestrutura
- Técnico de Infraestrutura
- Analista de Redes
- Service Desk
- Help Desk
- Suporte N1
- Suporte N2

CAMADA 2 — ÁREA

Exemplos:

- Suporte de TI
- Infraestrutura de TI
- Service Desk
- Redes
- Sistemas

CAMADA 3 — ATIVIDADES

Exemplos:

- atendimento a usuários;
- resolução de incidentes;
- troubleshooting;
- chamados;
- configuração de computadores;
- administração de Windows/Linux;
- Active Directory;
- redes TCP/IP;
- manutenção de hardware;
- suporte remoto;
- suporte presencial;
- backup;
- servidores.

CAMADA 4 — TECNOLOGIAS

Exemplos:

- Windows
- Linux
- Ubuntu
- Active Directory
- Microsoft 365
- TCP/IP
- Python
- SQL
- Ansible
- VirtualBox

Tecnologia isolada NÃO deve transformar uma vaga em relevante.

Exemplo:

"Rede" em uma vaga de vendedor não significa vaga de redes.

"DevOps" em uma vaga de Scrum Master não significa que a vaga seja adequada ao perfil.

"TCP/IP" em uma vaga Mainframe Sênior não significa automaticamente que ela seja adequada ao nível profissional.


=================================================================
7. NÍVEL PROFISSIONAL
=================================================================

PRIORIDADE: ALTA

O currículo atual está direcionado principalmente para:

- Júnior
- Suporte
- Infraestrutura
- Service Desk

O matcher ainda precisa considerar explicitamente senioridade.

Deve penalizar ou descartar automaticamente vagas claramente incompatíveis, como:

- Sênior
- Especialista
- Coordenador
- Gerente
- Diretor
- Principal
- Staff
- Tech Lead

quando a vaga exigir esse nível como requisito principal.


=================================================================
8. PROBLEMA ESPECÍFICO DO APINFO
=================================================================

STATUS: SCRAPER FUNCIONANDO

O APInfo está entregando apenas os dados básicos da listagem.

Para melhorar MUITO o filtro, será necessário avaliar a descrição completa da vaga.

Atualmente o sistema trabalha com:

- título;
- empresa;
- localização;
- link;
- descrição/snippet quando disponível.

Próximo passo importante:

Ao encontrar uma vaga potencialmente relevante, abrir a página da vaga e coletar a descrição completa.

Isso permitirá verificar:

- requisitos;
- atividades;
- senioridade;
- tecnologias;
- experiência exigida;
- formação;
- localização;
- modalidade;
- palavras de exclusão.


=================================================================
9. SCHEDULER
=================================================================

STATUS: ESTRUTURA IMPLEMENTADA, MAS PRECISA DE VALIDAÇÃO FINAL NO AMBIENTE LOCAL

Objetivo definido:

4 execuções pela manhã
4 execuções pela tarde
4 execuções pela noite
4 execuções pela madrugada

Total:

16 execuções por dia.

As janelas definidas são:

Madrugada: 02:00
Manhã: 08:00
Tarde: 14:00
Noite: 20:00

Cada janela possui quatro execuções.

Na versão final registrada, os horários são:

00 minutos
40 minutos
80 minutos
115 minutos

Exemplo — manhã:

08:00
08:40
09:20
09:55

Isso mantém as quatro execuções dentro da janela de duas horas.


=================================================================
10. ESTADO DO SCHEDULER
=================================================================

O scheduler utiliza:

data/scheduler_state.json

para registrar quantas execuções já foram realizadas em cada janela.

Também existe:

logs/scheduler.log

para registrar:

- inicialização;
- execução;
- erros;
- tempo de execução;
- código de retorno do main.py.


=================================================================
11. PROBLEMA JÁ ENCONTRADO NO scheduler.py
=================================================================

IMPORTANTE

Uma versão anterior do scheduler.py estava errada.

Ela tentava criar/escrever um arquivo em:

\mnt\data\scheduler.py

Isso causava:

FileNotFoundError:
No such file or directory: '\mnt\data\scheduler.py'

Essa versão NÃO deve ser utilizada.

A correção foi criar um scheduler que utiliza:

BASE_DIR = Path(__file__).resolve().parent

e executa:

BASE_DIR / "main.py"

A versão final registrada no projeto também cria:

data/
logs/

quando necessário.

O scheduler final ainda precisa ser executado no ambiente local e validado antes de ser considerado 100% concluído.


=================================================================
12. O QUE AINDA NÃO DEVE SER CONSIDERADO 100% PRONTO
=================================================================

1. Filtro realmente baseado no currículo.
2. Controle de senioridade.
3. Separação entre cargo-alvo e tecnologia isolada.
4. Análise da descrição completa da vaga.
5. Redução de falsos positivos.
6. Validação completa do scheduler no Windows.
7. Testes automatizados abrangentes do pipeline completo.
8. Tratamento de vagas que mudam conteúdo mantendo o mesmo codvaga.
9. Eventual classificação por faixa de compatibilidade mais precisa.
10. Execução 24/7 real por um período prolongado para validar estabilidade.


=================================================================
13. O QUE NÃO PRECISA SER REFEITO
=================================================================

Não é necessário recomeçar o projeto.

Já existem componentes funcionando:

- scraper APInfo;
- Playwright;
- main.py;
- models.py;
- matcher.py;
- profile.py;
- config.py;
- Discord notifier;
- deduplicação;
- unique_id estável por codvaga;
- dry-run;
- execução real;
- estrutura de scheduler;
- logs;
- estado do scheduler.


=================================================================
14. PRÓXIMA ETAPA RECOMENDADA
=================================================================

A prioridade agora NÃO deve ser o scheduler.

O próximo trabalho deve ser:

CORRIGIR O MATCHER PARA FILTRAR VAGAS REALMENTE COMPATÍVEIS COM O CURRÍCULO.

Ordem sugerida:

1. Revisar profile.py.
2. Revisar matcher.py.
3. Revisar config.py.
4. Criar regras de cargo-alvo.
5. Criar regras de senioridade.
6. Criar pesos por cargo/área/atividade/skill.
7. Criar penalidades.
8. Reduzir peso de tecnologias isoladas.
9. Fazer o matcher analisar título + descrição.
10. Criar uma bateria de vagas reais para teste.
11. Só depois validar o scheduler 24/7.


=================================================================
15. CRITÉRIO DE SUCESSO DO MAV
=================================================================

O MAV estará realmente pronto quando:

- encontrar vagas;
- ignorar vagas comerciais, administrativas e não relacionadas;
- não considerar uma simples palavra técnica como suficiente;
- priorizar Suporte de TI;
- priorizar Infraestrutura de TI;
- priorizar Service Desk;
- aceitar Redes quando houver contexto profissional de redes;
- respeitar o nível Júnior/Pleno compatível;
- rejeitar vagas claramente Sênior/Especialista/Coordenação/Gerência;
- enviar ao Discord somente vagas realmente compatíveis;
- nunca reenviar a mesma vaga;
- executar automaticamente nos quatro períodos;
- manter logs e estado;
- continuar funcionando sem intervenção manual.


=================================================================
16. RESUMO FINAL
=================================================================

ESTÁ FUNCIONANDO:

[OK] Python / ambiente virtual
[OK] Playwright
[OK] Scraper APInfo
[OK] Extração das vagas
[OK] Job model
[OK] Normalização
[OK] ID estável por codvaga no APInfo
[OK] Deduplicação
[OK] Profile profissional
[OK] Matcher básico
[OK] Score
[OK] Classificação
[OK] Discord Webhook
[OK] Dry-run
[OK] Execução real
[OK] Persistência de vagas processadas
[OK] Estrutura do scheduler
[OK] Estado do scheduler
[OK] Log do scheduler

PRECISA MELHORAR:

[!] Matcher baseado realmente no currículo
[!] Cargo deve ter prioridade sobre skill isolada
[!] Senioridade
[!] Análise de descrição completa
[!] Penalidades para vagas fora do perfil
[!] Redução de falsos positivos
[!] Testes automatizados mais completos
[!] Validação prolongada do scheduler

PRIORIDADE MÁXIMA:

>>> CORRIGIR O FILTRO/MATCHER PARA QUE O MAV ENVIE SOMENTE VAGAS REALMENTE COMPATÍVEIS COM O CURRÍCULO.


=================================================================
FIM DO DOCUMENTO
=================================================================
