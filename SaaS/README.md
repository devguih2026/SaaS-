# EventMaster SaaS - Gestão Inteligente para Eventos e Buffet

## 🚀 Sobre o Projeto
Este SaaS foi desenvolvido para resolver problemas reais de gestão em eventos de grande porte (casamentos, formaturas e festas corporativas). O foco principal é a **redução de custos operacionais** e o **controle de desperdício**, substituindo métodos arcaicos por tecnologia de precisão.

### 🚩 O Problema
Donos de buffet e organizadores de eventos enfrentam dois grandes gargalos:
1. **Gasto Excessivo com Insumos:** Atualmente, gasta-se em média R$ 300,00/mês apenas com pulseiras de identificação (tickets físicos).
2. **Falta de Dados:** Dificuldade em prever se a comida preparada será suficiente ou se haverá desperdício, gerando prejuízo financeiro.

### ✨ A Solução
O **EventMaster** digitaliza a jornada do convidado e do organizador:
* **Check-in via QR Code:** Substitui as pulseiras físicas por convites digitais enviados por E-mail ou WhatsApp, gerando uma economia imediata de centenas de reais por mês.
* **Dashboard Financeiro:** Visão clara do lucro real por evento, confrontando o valor cobrado vs. gasto com comida.
* **Monitoramento de Consumo em Tempo Real:** Registro de repetições de pratos para prever sobras ou faltas antes que o evento acabe.
* **Comunicação em Massa:** Arena para envio de comunicados e convites aos convidados.

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python 3.12+ com Framework **Django**.
* **Banco de Dados:** MySQL (Relacional).
* **API:** Arquitetura REST (JsonResponse) para integração com Frontend.
* **Autenticação:** Sistema de usuários nativo do Django para segurança dos dados.

## 📈 Funcionalidades Implementadas (MVP)
- [x] Modelagem de Banco de Dados (Eventos, Convidados, Consumo).
- [x] Lógica de Automação de Presença (Check-in automático ao consumir).
- [x] API de Dashboard com cálculos financeiros automatizados.
- [x] Sistema de Assinaturas (Planos para empresas de eventos).