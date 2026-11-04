# FraudShield AI — Frontend (Fase 10)

Console operacional em português brasileiro, separado do backend Python. Next.js com App Router, React, TypeScript strict, Tailwind CSS 4, componentes shadcn/ui sobre Radix, Recharts, Lucide, React Hook Form e Zod. Nenhum dado demonstrativo é servido pela aplicação.

## Iniciar

Requer Node.js 20.9 ou superior e npm. A implementação foi validada com Node.js 24.19.0 e npm 11.17.0.

```powershell
cd apps/web
npm.cmd ci
Copy-Item .env.example .env.local
npm.cmd run dev
```

Abra [http://localhost:3000](http://localhost:3000). Em shells sem a restrição de execução de scripts do PowerShell, `npm` pode substituir `npm.cmd`.

Configure `API_URL` em `.env.local` para o endereço do FastAPI, por padrão `http://127.0.0.1:8000`. Reinicie o servidor Next.js após mudar essa variável. O FastAPI e suas dependências precisam ser iniciados conforme a configuração existente do projeto; o frontend não inicia MLflow, PostgreSQL ou Kafka.

Para produção local:

```powershell
npm.cmd run build
npm.cmd start
```

## Páginas e contratos

| Página               | Integração real                                                   | Comportamento                                                                                                  |
| -------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `/dashboard`         | `GET /statistics/overview`, `GET /predictions?page=1&page_size=5` | Indicadores agregados, distribuição das classificações, score médio e registros recentes.                      |
| `/analyze`           | `POST /predict`                                                   | Formulário de 30 features, importação de payload JSON, validação, resultado e link para o registro persistido. |
| `/transactions`      | `GET /predictions`                                                | Filtros `prediction`, `model_version`, `start_date`, `end_date`; paginação por `page` e `page_size`.           |
| `/transactions/[id]` | `GET /predictions/{prediction_id}`                                | UUID, data, classificação, score, threshold, versão e features; estado específico para 404.                    |
| `/system`            | `GET /health`                                                     | Status reportado, nome do serviço e indicação de modelo carregado.                                             |

`/` redireciona para `/dashboard`. O health check é compartilhado entre as páginas e consultado a cada 60 segundos, com atualização manual em `/system`.

Os contratos foram conferidos diretamente em `src/fraudshield/api/schemas.py`, nos routers e nos serviços do backend. Não há prefixo global adicional.

### Dados e interpretação

- O payload de análise é exatamente `{ "features": { ... } }`, com `Time`, `Amount` e `V1` a `V28`. Todos os valores devem ser numéricos e finitos; `Time` e `Amount` devem ser não negativos. O formulário começa vazio e não gera valores aleatórios.
- As features V devem vir da transformação original do dataset. A interface não calcula essas features a partir de informações de uma compra.
- Valores monetários não recebem símbolo de moeda: o contrato não informa a moeda ou unidade de `Amount`.
- `alert_rate` e `fraud_score` são frações, formatadas como percentuais. A taxa de alertas não representa a precisão do modelo.
- A API fornece estatísticas agregadas, sem série temporal. Por isso, não há gráfico histórico, estimativas de economia ou métricas de performance inventadas.
- Os filtros usam a hora local do navegador e convertem as datas para ISO 8601 UTC, incluindo timezone. Datas de resposta são exibidas no fuso do navegador.
- A paginação respeita `page`, `page_size`, `total` e `total_pages` retornados pelo backend. Não há paginação local de um conjunto fictício.
- O health check não comprova a saúde de PostgreSQL, Kafka, MLflow, Prometheus ou Grafana. A observabilidade técnica continua no Grafana.

## Arquitetura e arquivos

```text
apps/web/
  src/app/                     # Rotas App Router, layout, estilos e favicon
    api/backend/[...path]/     # Proxy com lista restrita de rotas FastAPI
    dashboard/                 # Resumo operacional
    analyze/                   # Formulário de análise
    transactions/              # Histórico e detalhes por UUID
    system/                    # Health check
  src/components/
    ui/                        # Primitivos shadcn/ui: Button, Input, Sheet, Tooltip
    app-shell.tsx              # Sidebar, header, breadcrumbs e drawer
    health-provider.tsx        # Consulta compartilhada do health check
    shared.tsx                 # Cards, estados, badges e indicadores de score
    distribution-chart.tsx     # Gráfico com agregados reais
    transaction-filters.tsx    # Filtros e conversão de datas
    transactions-table.tsx     # Tabela desktop e cards mobile
    prediction-result.tsx      # Resultado de análise
  src/hooks/use-resource.ts    # Carregamento, cancelamento, erro e atualização
  src/lib/api/                 # Cliente fetch, contratos Zod e acesso a previsões
  src/lib/utils.ts             # Classes, números, percentuais e datas
  tests/                      # Testes de contratos e proxy HTTP
  e2e/                        # Testes de navegador com fixtures isoladas
```

Arquivos de configuração criados: `package.json`, `package-lock.json`, `tsconfig.json`, `next-env.d.ts`, `next.config.ts`, `postcss.config.mjs`, `eslint.config.mjs`, `components.json`, `playwright.config.ts`, `.env.example`, `.gitignore` e `.prettierignore`. Toda a implementação fica em `apps/web`; arquivos existentes do backend e da infraestrutura foram preservados.

### Comunicação e CORS

O navegador usa `/api/backend/...` na mesma origem do Next.js. O servidor Next.js encaminha somente as rotas necessárias para o FastAPI usando a variável privada `API_URL`. Não há necessidade de `NEXT_PUBLIC_API_URL`, nem alteração no CORS do FastAPI nesta arquitetura. O endereço do backend não é exposto no bundle do navegador.

O proxy não encaminha cookies ou credenciais do navegador. Requisições têm timeout de 15 segundos, cancelamento e cache desativado. Erros 422 e 404 preservam os detalhes do contrato; falhas internas recebem mensagem amigável. Não há repetição automática de `POST /predict`, evitando criar previsões duplicadas por retry automático.

As respostas são validadas em runtime com Zod. Respostas incompatíveis geram erro explícito em vez de números ou classificações de fallback. Requisições antigas são canceladas quando o componente desmonta ou os filtros mudam.

### Interface

Tokens semânticos em `src/app/globals.css`, tema escuro, sidebar recolhível no desktop, drawer acessível com foco gerenciado no mobile, link para pular ao conteúdo, navegação por teclado, campos rotulados e feedback de validação. A interface respeita `prefers-reduced-motion` e reorganiza cards, formulários e tabelas conforme a largura da tela.

## Validação

```powershell
npm.cmd run typecheck
npm.cmd run lint
npm.cmd test
npm.cmd run build

# Com Chrome já instalado:
$env:PLAYWRIGHT_CHANNEL = 'chrome'
npm.cmd run test:e2e

# Ou com o Chromium do Playwright:
npx.cmd playwright install chromium
Remove-Item Env:PLAYWRIGHT_CHANNEL -ErrorAction SilentlyContinue
npm.cmd run test:e2e
```

Os testes de navegador iniciam o build de produção na porta 3100 e encerram o servidor ao terminar. Execute o build antes deles. O servidor de teste usa `API_URL=http://127.0.0.1:1` para verificar uma falha real de conexão sem depender do estado do backend de desenvolvimento. Os demais cenários interceptam as requisições somente no navegador de teste, com fixtures sintéticas explicitamente isoladas em `e2e`. Os testes de proxy usam um servidor HTTP efêmero de teste.

Os testes cobrem contratos, validação de features, serialização de filtros, preservação de erros, proxy, submissão de análise, detalhes, 404, 422, paginação, estados vazio e loading, health check, drawer, sidebar, erros de runtime e ausência de overflow global nas cinco páginas em 320, 390, 768, 1024, 1440 e 2560 pixels. Capturas ficam em `test-results/`, ignoradas pelo Git.

### Limitações verificadas no ambiente de implementação

Resultados executados em 03/11/2026: TypeScript, lint e build de produção aprovados; 10 testes locais aprovados; 11 cenários de navegador aprovados. O último cenário foi repetido isoladamente após corrigir um seletor ambíguo do próprio teste. As cinco páginas foram verificadas nas seis larguras indicadas, e as capturas desktop/mobile foram inspecionadas visualmente. O teste de runtime não registrou erros ou warnings no console do navegador. O servidor temporário dos testes foi encerrado.

- A API não respondeu em `127.0.0.1:8000`. O estado real de indisponibilidade foi verificado; sucesso contra o modelo e o PostgreSQL reais depende de iniciar o backend existente. Fixtures de teste não substituem essa verificação integrada.
- `npm audit --omit=dev` não reportou vulnerabilidades de produção. O audit completo reportou 16 ocorrências moderadas ligadas ao `minimatch` transitivo da ferramenta de lint. O ESLint 9 é mantido por compatibilidade com os plugins oficiais atuais do Next.js, embora o npm emita aviso de depreciação dessa versão. Não foram aplicados downgrades ou overrides incompatíveis sugeridos pelo audit.
- No sandbox Windows desta sessão, o executor `tsx` precisou de execução autorizada fora do sandbox para consultar o usuário do sistema. Os testes passaram nessa execução; não foi necessário alterar o projeto para contornar a restrição.

Referências de configuração: [Next.js](https://nextjs.org/docs/app/getting-started/installation) e [shadcn/ui com Tailwind 4](https://ui.shadcn.com/docs/tailwind-v4).
