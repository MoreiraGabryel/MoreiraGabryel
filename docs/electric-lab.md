# Electric Lab — manutenção

Identidade visual do perfil de Marcos Gabryel: grafite, azul elétrico e amarelo, com monograma MG desenhado como circuito. O hero combina arte autoral e dados do GitHub.

## Arquivos

- `README.md`: conteúdo, links, seleção de imagens e seções expansíveis.
- `scripts/electric_lab.py`: consulta GraphQL e geração de SVG, sem dependências externas.
- `scripts/freeze_snake.py`: versões sem movimento do calendário da cobrinha.
- `.github/workflows/snake.yml`: geração e publicação conjunta do hero e da cobrinha.
- `assets/`: botões SVG locais, ícones de tecnologias, WebP original do Choque Estático e primeiro quadro estático.
- Branch `output`: quatro variantes do hero, seis variantes da cobrinha e `activity.json`.

## Dados e atualização

O workflow roda às **05:23 e 17:23 UTC**, manualmente e em alterações do gerador/workflow na `main`. Execuções agendadas podem atrasar. O cache de imagens do GitHub também pode atrasar a exibição do último snapshot.

O token temporário `GITHUB_TOKEN` é fornecido apenas durante a execução; não é escrito nas imagens nem no JSON. Repositórios são consultados com `privacy: PUBLIC`, `ownerAffiliations: OWNER` e `isFork: false`. Entre os 30 mais recentemente atualizados, o gerador escolhe o último push em um projeto não arquivado, excluindo o próprio repositório de perfil. Não são consultadas mensagens de commits, código, e-mails nem nomes de projetos privados.

As contribuições são as contagens retornadas pelo calendário do perfil, nos últimos **30 dias corridos em UTC, incluindo o dia atual**. Não equivalem apenas a commits e podem incluir contagens privadas anonimizadas conforme as configurações de visibilidade e o acesso do token. O snapshot identifica claramente a janela e a data de geração. A posição vertical usa `sqrt(contagem / pico)`; um ponto azul significa atividade, um ponto apagado significa zero. O pulso amarelo é decorativo.

Se a API falhar ou devolver dias incompletos, a geração falha antes da publicação e o último snapshot publicado é preservado. Hero e cobrinha compartilham uma única publicação na branch `output`, com concorrência serializada. O histórico de código da `main` não recebe commits periódicos de imagens.

## Reprodução local

Com Python 3.12+ e GitHub CLI autenticado:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/electric_lab.py --output dist
python3 -m unittest discover -s tests -v
```

Para reconstruir a arte sem API a partir de um snapshot salvo:

```sh
python3 scripts/electric_lab.py --snapshot caminho/activity.json --output dist
```

Para atualizar no GitHub:

```sh
gh workflow run snake.yml --ref main --repo MoreiraGabryel/MoreiraGabryel
```

## Compatibilidade

O README usa Markdown e HTML permitido pelo GitHub. A arte é exibida por `<img>`/`<picture>`, nunca SVG inline. Os SVGs têm estilos autocontidos, não usam scripts, fontes remotas ou recursos externos. Os links ficam no Markdown.

- Desktop: `1200 × 584`; mobile: `600 × 800`, selecionado até 600px de viewport.
- Temas claro e escuro do hero e da cobrinha via CSS interno do SVG, herdando `color-scheme` do GitHub. Isso também respeita um tema escolhido manualmente diferente do sistema operacional.
- O `<picture>` do hero seleciona somente tamanho e movimento. Não combinar essas condições com `prefers-color-scheme`: o componente `themed-picture` do GitHub reescreve as condições de tema quando o visitante escolhe um tema manual, descartando as outras condições. Os ícones da stack usam apenas condições simples de tema.
- Movimento reduzido: imagens estáticas e `prefers-reduced-motion` no CSS dos SVGs animados.
- O nome, a função e os dados permanecem visíveis desde o primeiro quadro.
- A animação WebP também tem um primeiro quadro PNG para movimento reduzido.
- Textos essenciais, projetos e contatos permanecem disponíveis como texto nativo no README.

Antes de mudar dimensões, validar em desktop e celular, claro e escuro. O preview de um editor Markdown não reproduz necessariamente a filtragem e a seleção de temas do GitHub.

## Paleta e créditos

| Elemento | Escuro | Claro |
| --- | --- | --- |
| Fundo | `#0B1018` | `#F3F7FC` |
| Texto | `#F0F5FC` | `#12243B` |
| Azul | `#53C7FF` | `#0969B5` |
| Energia | `#F4D35E` | `#8C6200` |

- Monograma, hero e botões: arte criada para este perfil; fontes de sistema.
- Cobrinha: [Platane/snk](https://github.com/Platane/snk).
- Ícones de tecnologias: [Skill Icons](https://github.com/tandpfun/skill-icons/tree/7f7e691e71aec64e8354bf697835e009d1ad80f8/icons), cópias locais em `assets/stack/`, com licença MIT incluída. Os SVGs originais desse commit foram combinados em linhas de até cinco ícones de 48px, com espaçamento de 4px e IDs prefixados para evitar colisões. Há versões `dark` e `light`.
- Estatísticas expansíveis: `github-stats-extended.vercel.app`.
- Choque Estático: animação que já era usada no perfil, preservada do [arquivo original no Tenor](https://media.tenor.com/Mf57HFtQHMYAAAA1/static-shock.webp). O personagem e a animação pertencem aos respectivos titulares.
