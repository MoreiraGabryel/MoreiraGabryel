import os
import re
import sys

def main():
    # 1. Pega o título da Issue (ex: tttp:1,1)
    issue_title = os.getenv("ISSUE_TITLE", "")
    if "tttp:" not in issue_title:
        print("Título inválido")
        return

    # Extrai a coordenada
    move = issue_title.split("tttp:")[1].strip()

    # 2. Abre o README
    if not os.path.exists("README.md"):
        print("README.md não encontrado")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Procura o link exato e substitui por X
    # Usamos re.escape para não dar erro com os caracteres do link
    pattern = rf"\[\s*\]\(.*?title=tttp:{move}\)"
    
    if re.search(pattern, content):
        content = re.sub(pattern, "❌", content)
        
        # 4. Jogada da IA: Procura o primeiro espaço vazio e coloca O
        ia_pattern = r"\[\s*\]\(.*?title=tttp:.*?\)"
        if re.search(ia_pattern, content):
            content = re.sub(ia_pattern, "⭕", content, count=1)
            status_msg = "**Status:** Sua vez!"
        else:
            status_msg = "**Status:** Fim de jogo. `eu sempre ganho 🤖`"
    else:
        print(f"Não encontrei o movimento {move} no README")
        return

    # 5. Atualiza o Status (ajustado para o seu texto atual)
    content = re.sub(r"Status:.*", f"Status: {status_msg}", content)

    # 6. Salva o arquivo
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("Sucesso: README atualizado!")

if __name__ == "__main__":
    main()
